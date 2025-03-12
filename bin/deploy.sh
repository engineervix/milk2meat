#!/usr/bin/env bash
set -eo pipefail

# =============================================
# Milk2Meat Dokku Deployment Script
# =============================================

# Parse command line arguments
ENV_FILE=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --env-file=*)
      ENV_FILE="${1#*=}"
      shift 1
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# If env file not specified via argument, use default location
if [[ -z "$ENV_FILE" ]]; then
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    ENV_FILE="${SCRIPT_DIR}/.deploy.env"
fi

# Load secrets from environment file if it exists
if [[ -f "$ENV_FILE" ]]; then
    echo "➡️ Loading environment variables from $ENV_FILE"
    # shellcheck source=/dev/null
    source "$ENV_FILE"
else
    echo "⚠️ Environment file not found: $ENV_FILE"
    echo "Please create this file with your deployment configuration."
    exit 1
fi

# Configuration
DB_SERVICE_NAME="postgres-${APP_NAME}"
REDIS_SERVICE_NAME="redis-${APP_NAME}"
GIT_BRANCH="main"
PORT="8000"

# Check if we're connected to the correct server
function check_connection() {
    echo "🔍 Checking connection to Dokku server..."
    set +e
    ssh $DOKKU_HOST "dokku version" &> /dev/null
    local connection_status=$?
    set -e

    if [ $connection_status -ne 0 ]; then
        echo "❌ Cannot connect to Dokku server or dokku command not found!"
        exit 1
    fi
    echo "✅ Connection to Dokku server verified"
}

# Create the application if it doesn't exist
function create_app() {
    echo "🚀 Creating Dokku app $APP_NAME (if it doesn't exist)..."

    set +e
    ssh $DOKKU_HOST "dokku apps:exists $APP_NAME" &> /dev/null
    local app_exists=$?
    set -e

    if [ $app_exists -ne 0 ]; then
        ssh $DOKKU_HOST "dokku apps:create $APP_NAME"
        echo "✅ Created new Dokku app: $APP_NAME"
    else
        echo "ℹ️ App $APP_NAME already exists, skipping creation"
    fi
}

# Set up domain
function setup_domain() {
    echo "🌐 Setting up domain $DOMAIN for $APP_NAME..."

    # Add domain (this should not fail even if already added)
    ssh $DOKKU_HOST "dokku domains:add $APP_NAME $DOMAIN"

    # Remove default domain, suppress errors if it doesn't exist
    set +e
    ssh $DOKKU_HOST "dokku domains:remove $APP_NAME $APP_NAME.$ROOT_DOMAIN" 2>/dev/null
    set -e

    echo "✅ Domain configured"
}

# Set up PostgreSQL
function setup_postgres() {
    echo "🐘 Setting up PostgreSQL database..."

    # Check if Postgres plugin is installed
    set +e
    ssh $DOKKU_HOST "sudo dokku plugin:installed postgres"
    local postgres_plugin_installed=$?
    set -e

    if [ $postgres_plugin_installed -ne 0 ]; then
        echo "📦 Installing Postgres plugin..."
        ssh $DOKKU_HOST "sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git postgres"
    else
        echo "ℹ️ Postgres plugin already installed"
    fi

    # Create Postgres service if it doesn't exist
    set +e
    ssh $DOKKU_HOST "dokku postgres:list" | grep -q "$DB_SERVICE_NAME"
    local postgres_service_exists=$?
    set -e

    if [ $postgres_service_exists -ne 0 ]; then
        echo "🛠️ Creating new Postgres service: $DB_SERVICE_NAME"
        ssh $DOKKU_HOST "dokku postgres:create $DB_SERVICE_NAME --image postgres --image-version 15.7"
    else
        echo "ℹ️ Postgres service $DB_SERVICE_NAME already exists"
    fi

    # Link service to app
    echo "🔗 Linking Postgres to app..."
    set +e
    ssh $DOKKU_HOST "dokku postgres:link $DB_SERVICE_NAME $APP_NAME"
    set -e

    # Set up backups if credentials are provided
    if [[ -n "$BACKUP_AWS_ACCESS_KEY_ID" && -n "$BACKUP_AWS_SECRET_ACCESS_KEY" && -n "$BACKUP_AWS_DEFAULT_REGION" && -n "$BACKUP_AWS_ENDPOINT_URL" && -n "$BACKUP_BUCKET" ]]; then
        echo "💾 Setting up database backups..."
        ssh $DOKKU_HOST "dokku postgres:backup-auth $DB_SERVICE_NAME $BACKUP_AWS_ACCESS_KEY_ID $BACKUP_AWS_SECRET_ACCESS_KEY $BACKUP_AWS_DEFAULT_REGION v4 $BACKUP_AWS_ENDPOINT_URL"
        ssh $DOKKU_HOST "dokku postgres:backup $DB_SERVICE_NAME $BACKUP_BUCKET"
        ssh $DOKKU_HOST "dokku postgres:backup-schedule $DB_SERVICE_NAME \"15 10,22 * * *\" $BACKUP_BUCKET"
        echo "✅ Database backups configured"
    else
        echo "⚠️ Skipping database backup configuration (missing credentials)"
    fi
}

# Set up Redis
function setup_redis() {
    echo "🔄 Setting up Redis..."

    # Check if Redis plugin is installed
    set +e
    ssh $DOKKU_HOST "sudo dokku plugin:installed redis"
    local redis_plugin_installed=$?
    set -e

    if [ $redis_plugin_installed -ne 0 ]; then
        echo "📦 Installing Redis plugin..."
        ssh $DOKKU_HOST "sudo dokku plugin:install https://github.com/dokku/dokku-redis.git redis"
    else
        echo "ℹ️ Redis plugin already installed"
    fi

    # Create Redis service if it doesn't exist
    set +e
    ssh $DOKKU_HOST "dokku redis:list" | grep -q "$REDIS_SERVICE_NAME"
    local redis_service_exists=$?
    set -e

    if [ $redis_service_exists -ne 0 ]; then
        echo "🛠️ Creating new Redis service: $REDIS_SERVICE_NAME"
        ssh $DOKKU_HOST "dokku redis:create $REDIS_SERVICE_NAME --image valkey/valkey --image-version 8.0"
    else
        echo "ℹ️ Redis service $REDIS_SERVICE_NAME already exists"
    fi

    # Link service to app
    echo "🔗 Linking Redis to app..."
    set +e
    ssh $DOKKU_HOST "dokku redis:link $REDIS_SERVICE_NAME $APP_NAME"
    set -e
}

# Set environment variables
function setup_env_vars() {
    echo "🔐 Setting environment variables..."

    # Core environment variables
    ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME ALLOWED_HOSTS=$DOMAIN"
    ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME DEBUG=False"
    ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME PORT=$PORT"

    # Generate a secret key if not provided
    if [[ -z "$DJANGO_SECRET_KEY" ]]; then
        DJANGO_SECRET_KEY=$(openssl rand -hex 50)
        echo "🔑 Generated new Django secret key"
    fi
    ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"

    # Redis config
    ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME REDIS_KEY_PREFIX=$APP_NAME"

    # Email settings
    if [[ -n "$DJANGO_SERVER_EMAIL" ]]; then
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME DJANGO_SERVER_EMAIL=$DJANGO_SERVER_EMAIL"
    fi

    if [[ -n "$DEFAULT_FROM_EMAIL" ]]; then
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME DEFAULT_FROM_EMAIL='$DEFAULT_FROM_EMAIL'"
    fi

    if [[ -n "$EMAIL_RECIPIENTS" ]]; then
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME EMAIL_RECIPIENTS='$EMAIL_RECIPIENTS'"
    fi

    # Sentry settings
    if [[ -n "$SENTRY_DSN" ]]; then
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME SENTRY_DSN=$SENTRY_DSN"
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME DJANGO_SENTRY_LOG_LEVEL=${DJANGO_SENTRY_LOG_LEVEL:-20}"
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT:-production}"
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME SENTRY_TRACES_SAMPLE_RATE=${SENTRY_TRACES_SAMPLE_RATE:-0.5}"
    fi

    # Email provider settings
    if [[ -n "$BREVO_API_KEY" ]]; then
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME BREVO_API_KEY=$BREVO_API_KEY"
    fi

    # S3 storage settings
    if [[ -n "$AWS_ACCESS_KEY_ID" && -n "$AWS_SECRET_ACCESS_KEY" && -n "$AWS_S3_ENDPOINT_URL" && -n "$AWS_STORAGE_BUCKET_NAME" ]]; then
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME AWS_S3_ENDPOINT_URL=$AWS_S3_ENDPOINT_URL"
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME AWS_STORAGE_BUCKET_NAME=$AWS_STORAGE_BUCKET_NAME"

        # Generate a random location prefix if not provided
        if [[ -z "$AWS_LOCATION" ]]; then
            AWS_LOCATION=$(openssl rand -hex 10)
            echo "📁 Generated random AWS location prefix: $AWS_LOCATION"
        fi
        ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME AWS_LOCATION=$AWS_LOCATION"

        # Set custom domain if provided
        if [[ -n "$AWS_S3_CUSTOM_DOMAIN" ]]; then
            ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME AWS_S3_CUSTOM_DOMAIN=$AWS_S3_CUSTOM_DOMAIN"
        fi
    fi

    # Custom environment variables (from ENV_CUSTOM_VARS)
    if [[ -n "$ENV_CUSTOM_VARS" ]]; then
        # Split the string on semicolons and process each variable
        IFS=';' read -ra CUSTOM_VARS <<< "$ENV_CUSTOM_VARS"
        for var in "${CUSTOM_VARS[@]}"; do
            # Only process non-empty values
            if [[ -n "$var" ]]; then
                # Split key and value on the first equals sign
                key=${var%%=*}
                value=${var#*=}
                echo "🔧 Setting custom environment variable: $key"
                ssh $DOKKU_HOST "dokku config:set --no-restart $APP_NAME $key='$value'"
            fi
        done
    fi

    echo "✅ Environment variables configured"
}

# Configure Docker build options
function setup_docker_options() {
    echo "🐳 Setting Docker build options..."
    ssh $DOKKU_HOST "dokku docker-options:add $APP_NAME build '--target production'"
    echo "✅ Docker build options set"
}

# Configure Nginx
function setup_nginx() {
    echo "🌐 Configuring Nginx..."
    ssh $DOKKU_HOST "dokku nginx:set $APP_NAME client-max-body-size 50m"
    ssh $DOKKU_HOST "dokku nginx:set $APP_NAME hsts-preload true"

    set +e
    ssh $DOKKU_HOST "dokku proxy:build-config $APP_NAME"
    set -e

    echo "✅ Nginx configured"
}

# Set up SSL with Let's Encrypt
function setup_ssl() {
    echo "🔒 Setting up SSL with Let's Encrypt..."

    # Install Let's Encrypt plugin if not already installed
    set +e
    ssh $DOKKU_HOST "sudo dokku plugin:installed letsencrypt"
    local letsencrypt_installed=$?
    set -e

    if [ $letsencrypt_installed -ne 0 ]; then
        echo "📦 Installing Let's Encrypt plugin..."
        ssh $DOKKU_HOST "sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git"
    else
        echo "ℹ️ Let's Encrypt plugin already installed"
    fi

    # Set up Let's Encrypt
    if [[ -n "$LETSENCRYPT_EMAIL" ]]; then
        ssh $DOKKU_HOST "dokku config:set --no-restart --global DOKKU_LETSENCRYPT_EMAIL=$LETSENCRYPT_EMAIL"
        ssh $DOKKU_HOST "dokku letsencrypt:set $APP_NAME email $LETSENCRYPT_EMAIL"

        set +e
        ssh $DOKKU_HOST "dokku letsencrypt:enable $APP_NAME"
        local letsencrypt_result=$?
        set -e

        if [ $letsencrypt_result -ne 0 ]; then
            echo "⚠️ Let's Encrypt setup failed. Will try again after app is deployed."
        else
            echo "✅ SSL configured with Let's Encrypt"
        fi

        # Add cron job for automatic renewal
        set +e
        ssh $DOKKU_HOST "dokku letsencrypt:cron-job --add"
        set -e
    else
        echo "⚠️ Skipping Let's Encrypt setup (no email provided)"
    fi
}

# Set up ports
function setup_ports() {
    echo "🔌 Configuring ports..."

    # Remove HTTP port if it exists
    set +e
    ssh $DOKKU_HOST "dokku ports:remove $APP_NAME http:80:5000" 2>/dev/null
    set -e

    # Add HTTP port
    ssh $DOKKU_HOST "dokku ports:add $APP_NAME http:80:$PORT"

    # Remove HTTPS port if it exists
    set +e
    ssh $DOKKU_HOST "dokku ports:remove $APP_NAME https:443:5000" 2>/dev/null
    set -e

    # Add HTTPS port
    ssh $DOKKU_HOST "dokku ports:add $APP_NAME https:443:$PORT"

    echo "✅ Ports configured"
}

# Deploy application
function deploy_app() {
    echo "🚀 Preparing to deploy application..."

    # Check if we have the dokku remote
    set +e
    git remote | grep -q "dokku"
    local remote_exists=$?
    set -e

    if [ $remote_exists -ne 0 ]; then
        echo "🔗 Adding dokku remote..."
        git remote add dokku dokku@$DOKKU_HOST:$APP_NAME
    fi

    echo "📤 Pushing code to dokku..."
    git push dokku $GIT_BRANCH:master

    echo "✅ Deployment complete!"

    # If Let's Encrypt failed earlier, try again
    if [[ -n "$LETSENCRYPT_EMAIL" ]]; then
        echo "🔄 Ensuring Let's Encrypt is enabled..."
        set +e
        ssh $DOKKU_HOST "dokku letsencrypt:enable $APP_NAME"
        set -e
    fi
}

# Import database dump if provided
function import_database() {
    if [[ -n "$DB_DUMP_FILE" && -f "$DB_DUMP_FILE" ]]; then
        echo "📥 Importing database from $DB_DUMP_FILE..."
        cat "$DB_DUMP_FILE" | ssh $DOKKU_HOST "dokku postgres:import $DB_SERVICE_NAME"
        echo "✅ Database imported"
    fi
}

# Main execution
function main() {
    echo "🚀 Starting deployment process for $APP_NAME to $DOMAIN"

    # Check if required variables are set
    if [[ -z "$APP_NAME" ]]; then
        echo "❌ APP_NAME is not set. Please define it in your environment file."
        exit 1
    fi

    if [[ -z "$DOMAIN" ]]; then
        echo "❌ DOMAIN is not set. Please define it in your environment file."
        exit 1
    fi

    if [[ -z "$DOKKU_HOST" ]]; then
        echo "❌ DOKKU_HOST is not set. Please define it in your environment file."
        exit 1
    fi

    # Run all the steps in sequence
    check_connection
    create_app
    setup_domain
    setup_postgres
    setup_redis
    setup_env_vars
    setup_docker_options
    setup_nginx
    import_database
    setup_ports
    setup_ssl  # Do this after ports are configured

    # Deploy the application at the end
    if [[ "$SKIP_DEPLOY" != "true" ]]; then
        deploy_app
    else
        echo "⏩ Skipping code deployment as requested"
    fi

    echo "🎉 All done! Your app should be available at https://$DOMAIN"
}

# Run the script
main "$@"

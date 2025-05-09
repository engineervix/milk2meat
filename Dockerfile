#################################################################################
# use node:22.*-bookworm-slim as the base image for building the frontend
#################################################################################

FROM node:22.15-bookworm-slim AS frontend-builder

WORKDIR /app

# Copy only package files first to leverage Docker caching
COPY package*.json .babelrc.js webpack.config.js postcss.config.js tailwind.config.js ./
RUN npm ci --no-optional --no-audit --progress=false

# Copy only the files needed for the frontend build
COPY ./milk2meat/frontend ./milk2meat/frontend
# Copy template files needed for tailwind to detect utility classes
COPY ./milk2meat/auth ./milk2meat/auth
COPY ./milk2meat/bible ./milk2meat/bible
COPY ./milk2meat/notes ./milk2meat/notes
COPY ./milk2meat/core ./milk2meat/core
COPY ./milk2meat/home ./milk2meat/home
COPY ./milk2meat/templates ./milk2meat/templates

RUN npm run build:prod

#################################################################################
# use python:3.13-slim-bookworm as the base image for production
#################################################################################

FROM python:3.13-slim-bookworm AS production

# Add user that will be used in the container
RUN groupadd --system django && \
    useradd --system --create-home --shell /bin/bash -g django django

RUN mkdir -p /home/django/app && chown django:django /home/django/app

# Set work directory
WORKDIR /home/django/app

# Port used by this container to serve HTTP
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/home/django/app \
    DJANGO_SETTINGS_MODULE=milk2meat.settings.production \
    WEB_CONCURRENCY=3

# Install system dependencies required by Django and the project
RUN apt-get update --yes --quiet && \
    apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    gdal-bin \
    libgdal-dev \
    binutils \
    libproj-dev \
    git \
    imagemagick \
    libjpeg62-turbo-dev \
    libmagic1 \
    libpq-dev \
    libwebp-dev \
    zlib1g-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Use user "django" to run the build commands below and the server itself
USER django

# Set up virtual environment & install python dependencies
ARG DEVELOPMENT=false
ARG POETRY_VERSION=1.8.5
ENV VIRTUAL_ENV=/home/django/venv \
    DEVELOPMENT=${DEVELOPMENT}
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir poetry==$POETRY_VERSION

# Install dependencies first to leverage Docker caching
COPY --chown=django:django ./pyproject.toml ./poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Copy build artifacts from frontend-builder stage
RUN mkdir -p /home/django/app/milk2meat/static
COPY --from=frontend-builder --chown=django:django /app/milk2meat/static /home/django/app/milk2meat/static

# Copy the source code of the project into the container
COPY --chown=django:django . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Collect static files
RUN DJANGO_SECRET_KEY=fake DATABASE_URL=postgres://user:password@host:5432/db python manage.py collectstatic --noinput --clear

# Set the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

# Runtime command that executes when "docker run" is called
# gunicorn will use the settings defined in gunicorn.conf.py
CMD ["gunicorn"]

#################################################################################
# The next steps won't be run in production
#################################################################################

FROM production AS dev

# Swap user, so the following tasks can be run as root
USER root

# Install Node.js for development
ENV NODE_MAJOR=22
RUN apt-get update && \
    apt-get install -y --no-install-recommends gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    nodejs \
    postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install development dependencies
USER django
RUN poetry install --with dev,test,docs --no-interaction --no-ansi

# Pull in the node modules for the frontend
COPY --chown=django:django --from=frontend-builder /app/node_modules ./node_modules

# do nothing - exec commands elsewhere
CMD tail -f /dev/null

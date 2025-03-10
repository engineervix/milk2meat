#################################################################################
# use node:22.4-bookworm as the base image for building the frontend
#################################################################################

FROM node:22.4-bookworm AS frontend-builder

# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json .babelrc.js webpack.config.js postcss.config.js tailwind.config.js ./
RUN npm ci --no-optional --no-audit --progress=false --network=host

COPY ./milk2meat/assets ./milk2meat/assets

# we need these so tailwind can detect the utility classes
COPY ./milk2meat/auth ./milk2meat/auth
COPY ./milk2meat/core ./milk2meat/core
COPY ./milk2meat/home ./milk2meat/home
COPY ./milk2meat/templates ./milk2meat/templates

RUN npm run build:prod

#################################################################################
# use python:3.13-slim-bookworm as the base image for production and development
#################################################################################

FROM python:3.13-slim-bookworm AS production

# Add user that will be used in the container
RUN groupadd django && \
    useradd --create-home --shell /bin/bash -g django django

RUN mkdir -p /home/django/app && chown django:django /home/django/app

# set work directory
WORKDIR /home/django/app

# Port used by this container to serve HTTP.
EXPOSE 8000

# set environment variables
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/home/django/app \
    DJANGO_SETTINGS_MODULE=milk2meat.settings.production \
    ## Note: feel free to adjust WEB_CONCURRENCY based on the memory requirements of your processes
    ## ref: https://docs.gunicorn.org/en/stable/settings.html
    ## The suggested number of workers is (2*CPU)+1
    WEB_CONCURRENCY=3 \
    NODE_MAJOR=22

# Install system dependencies required by Django and the project
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    ca-certificates gnupg \
    curl \
    gdal-bin libgdal-dev binutils libproj-dev \
    git \
    imagemagick \
    libjpeg62-turbo-dev \
    libmagic1 \
    libpq-dev \
    libwebp-dev \
    zlib1g-dev \
    && apt-get clean

# Install node (Keep the version in sync with the node container above)
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get install -y nodejs

# Use user "django" to run the build commands below and the server itself.
USER django

# set up virtual environment & install python dependencies
ARG DEVELOPMENT
ARG POETRY_VERSION=1.8.5
ENV VIRTUAL_ENV=/home/django/venv \
    DEVELOPMENT=${DEVELOPMENT}
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip
RUN python -m pip install poetry==$POETRY_VERSION

COPY --chown=django ./pyproject.toml .
COPY --chown=django ./poetry.lock .
RUN poetry install ${DEVELOPMENT:+--with dev,test,docs} --no-root

# Copy build artifacts from frontend-builder stage
RUN mkdir -p /home/django/app/milk2meat/static
COPY --from=frontend-builder --chown=django:django /milk2meat/static /home/django/app/milk2meat/static

# Copy the source code of the project into the container
COPY --chown=django:django . .

# Run poetry install again to install the project (so that the `milk2meat` package is always importable)
RUN poetry install

# Run collectstatic.
# This step is deferred, because it somehow messes up production settings
# RUN python manage.py collectstatic --noinput --clear

# Runtime command that executes when "docker run" is called
# guicorn will:
#   - use the settings defined in gunicorn.conf.py
#   - make use of PORT and WEB_CONCURRENCY
CMD ["gunicorn"]

#################################################################################
# The next steps won't be run in production
#################################################################################

FROM production AS dev

# Swap user, so the following tasks can be run as root
USER root

# Install `psql`, useful for `manage.py dbshell`
RUN apt-get install -y postgresql-client

# Restore user
USER django

# Pull in the node modules for the frontend
COPY --chown=django:django --from=frontend-builder ./node_modules ./node_modules

# do nothing - exec commands elsewhere
CMD tail -f /dev/null

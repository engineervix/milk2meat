# README

This directory contains [Docker](https://www.docker.com/) configuration files for **development**.

## Development Setup

- `docker-compose.dev.yml` - Development Docker Compose configuration (Postgres only)
- `db/` - Contains the Dockerfile and setup for PostgreSQL
- `Procfile` - Used by honcho to run the Django development server and frontend tools

The production Docker Compose configuration is located in the root directory as `docker-compose.yml`.

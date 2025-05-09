#!/bin/bash

# the script should exit whenever it encounters an error
set -o errexit
# exit execution if one of the commands in the pipe fails.
set -o pipefail
# exit when the script tries to use undeclared variables.
set -o nounset

# Run collectstatic
# echo "Running static file collection..."
# python manage.py collectstatic --noinput --clear

# Run checks to verify that the correct settings are in use
echo "Running deployment checks..."
python manage.py check --deploy

# Run migrations
echo "Running migrations..."
python manage.py migrate --no-input

# We run buildwatson whenever new models are added to django-watson.
echo "Rebuilding the database indices needed by django-watson..."
python manage.py buildwatson

# Finally, run whatever command was passed (gunicorn)
exec "$@"

#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Convert static files for Render
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# This creates the superuser using the Env Vars you just set.
# The "|| true" ensures that if the user already exists, the build won't crash.
python manage.py createsuperuser --noinput || true
#!/usr/bin/env bash
set -e

# wait for db
until pg_isready -h db -p 5432 -U ${DB_USER}; do
  echo "Waiting for Postgres..."
  sleep 1
done

# run migrations & collectstatic
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# start gunicorn on port 8000
gunicorn area_project.wsgi:application --bind 0.0.0.0:8000 --workers 3

#!/bin/bash

# Navigate to backend
cd backend

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py create_admin

# Start the server
gunicorn kenyan_payroll_project.wsgi:application --bind 0.0.0.0:$PORT
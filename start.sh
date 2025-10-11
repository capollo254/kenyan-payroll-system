#!/bin/bash

# Navigate to backend
cd backend

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py create_admin

# Set up default tenants for multi-tenancy
python manage.py setup_tenants

# Start the server
gunicorn kenyan_payroll_project.wsgi:application --bind 0.0.0.0:$PORT
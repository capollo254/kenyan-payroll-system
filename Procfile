release: cd backend && python manage.py migrate && python manage.py create_admin
web: cd backend && gunicorn kenyan_payroll_project.wsgi:application --bind 0.0.0.0:$PORT
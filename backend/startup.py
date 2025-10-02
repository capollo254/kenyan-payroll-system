#!/usr/bin/env python
"""
Startup script for Railway deployment
This script handles database migrations and admin user creation automatically
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def run_startup_tasks():
    """Run database migrations and create superuser if needed"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
    django.setup()
    
    print("🚀 Starting Railway deployment tasks...")
    
    # Run migrations
    print("📊 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Database migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    
    # Create superuser if it doesn't exist
    print("👤 Creating admin user...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@company.com')
        admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123456')
        
        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            print(f"✅ Admin user '{admin_username}' created successfully!")
        else:
            print(f"ℹ️  Admin user '{admin_username}' already exists")
            
    except Exception as e:
        print(f"❌ Admin user creation error: {e}")
        return False
    
    print("🎉 All startup tasks completed successfully!")
    return True

if __name__ == '__main__':
    run_startup_tasks()
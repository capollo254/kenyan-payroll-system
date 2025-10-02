#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    
    email = 'constantive@gmail.com'
    username = 'constantive'
    password = 'September@2025.com'
    
    # Delete existing user if exists
    try:
        existing_user = User.objects.get(email=email)
        existing_user.delete()
        print(f"🗑️ Deleted existing user with email: {email}")
    except User.DoesNotExist:
        print("📝 No existing user found")
    
    # Create new superuser
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    print("✅ Superuser created successfully!")
    print(f"📧 Email: {email}")
    print(f"👤 Username: {username}")
    print(f"🔐 Password: {password}")
    print("🌐 Login at: /admin/ using EMAIL")
    print("=" * 50)

if __name__ == '__main__':
    create_superuser()
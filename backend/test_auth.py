#!/usr/bin/env python
import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from apps.core.serializers import UserLoginSerializer

User = get_user_model()

def test_authentication():
    print("=== Testing Authentication ===")
    
    # Get a test user
    test_users = [
        'testuser@admin.com',
        'frontend@gmail.com', 
        'constantive@gmail.com'
    ]
    
    for email in test_users:
        user = User.objects.filter(email=email).first()
        if user:
            print(f"\nTesting user: {email}")
            print(f"User active: {user.is_active}")
            print(f"User staff: {user.is_staff}")
            
            # Test common passwords
            test_passwords = ['testpassword', 'password123', 'admin123', 'password', '123456']
            
            for password in test_passwords:
                # Test Django authenticate
                auth_user = authenticate(email=email, password=password)
                if auth_user:
                    print(f"✅ Password '{password}' works with Django authenticate()")
                    
                    # Test with serializer
                    serializer = UserLoginSerializer(data={'email': email, 'password': password})
                    if serializer.is_valid():
                        print(f"✅ Serializer validation passed")
                    else:
                        print(f"❌ Serializer validation failed: {serializer.errors}")
                    break
            else:
                print(f"❌ No password worked for {email}")
                
            break
    
    print("\n=== Testing Backend Settings ===")
    print(f"AUTHENTICATION_BACKENDS: {settings.AUTHENTICATION_BACKENDS}")
    
if __name__ == '__main__':
    test_authentication()
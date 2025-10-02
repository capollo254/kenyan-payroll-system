#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

def test_superuser_passwords():
    """Test different password combinations for superusers"""
    print("TESTING SUPERUSER PASSWORDS")
    print("=" * 40)
    
    superusers = User.objects.filter(is_superuser=True, is_active=True)
    passwords_to_try = ['admin', 'password', '123456', 'admin123', 'superuser']
    
    for user in superusers[:2]:  # Test first 2 superusers
        print(f"\nTesting user: {user.email}")
        
        for password in passwords_to_try:
            try:
                authenticated_user = authenticate(email=user.email, password=password)
                if authenticated_user:
                    print(f"✅ FOUND PASSWORD: '{password}' works for {user.email}")
                    break
            except Exception as e:
                print(f"❌ Error testing password '{password}': {e}")
        else:
            print(f"❌ No working password found for {user.email}")

def reset_superuser_password():
    """Reset a superuser password for testing"""
    print("\nRESETTING SUPERUSER PASSWORD FOR TESTING")
    print("=" * 50)
    
    # Get the first superuser
    superuser = User.objects.filter(is_superuser=True, is_active=True).first()
    if superuser:
        superuser.set_password('testpass123')
        superuser.save()
        print(f"✅ Password reset for {superuser.email} to 'testpass123'")
        
        # Test the new password
        authenticated_user = authenticate(email=superuser.email, password='testpass123')
        if authenticated_user:
            print(f"✅ Password verification successful!")
            return superuser.email, 'testpass123'
        else:
            print(f"❌ Password verification failed!")
    else:
        print("❌ No superuser found")
    
    return None, None

if __name__ == '__main__':
    test_superuser_passwords()
    email, password = reset_superuser_password()
    
    if email and password:
        print(f"\n🔑 Use these credentials to test frontend login:")
        print(f"Email: {email}")
        print(f"Password: {password}")
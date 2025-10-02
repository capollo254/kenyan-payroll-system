#!/usr/bin/env python
import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth import get_user_model

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

User = get_user_model()

def test_superuser_api_access():
    """Test that superusers can access payslips via API (frontend simulation)"""
    print("TESTING SUPERUSER API ACCESS (Frontend Simulation)")
    print("=" * 60)
    
    # Get a superuser
    superusers = User.objects.filter(is_superuser=True, is_active=True)[:1]
    if not superusers:
        print("❌ No active superusers found")
        return
    
    superuser = superusers[0]
    print(f"Testing with superuser: {superuser.email}")
    
    # Create a test client
    client = Client()
    
    # Login the superuser
    login_success = client.login(email=superuser.email, password='admin')
    if not login_success:
        print("❌ Could not log in superuser")
        return
    
    print(f"✅ Logged in as: {superuser.email}")
    
    # Test the payslips API endpoint
    response = client.get('/api/v1/payroll/payslips/')
    print(f"API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        count = len(results)
        print(f"✅ SUCCESS: Superuser can access {count} payslips via API")
        
        if results:
            print("Sample payslips:")
            for i, payslip in enumerate(results[:3]):
                print(f"  - Payslip {i+1}: {payslip.get('employee_name', 'N/A')} - {payslip.get('pay_date', 'N/A')}")
    else:
        print(f"❌ FAILED: API returned status {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error details: {error_data}")
        except:
            print(f"Response content: {response.content}")

if __name__ == '__main__':
    test_superuser_api_access()
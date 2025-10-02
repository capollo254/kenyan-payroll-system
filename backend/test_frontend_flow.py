#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_frontend_login_flow():
    """Test the complete frontend login flow for a superuser"""
    print("TESTING FRONTEND LOGIN FLOW FOR SUPERUSER")
    print("=" * 60)
    
    # Get a superuser
    superuser = User.objects.filter(is_superuser=True, is_active=True).first()
    if not superuser:
        print("❌ No active superusers found")
        return
    
    print(f"Testing with superuser: {superuser.email}")
    print(f"- is_superuser: {superuser.is_superuser}")
    print(f"- is_staff: {superuser.is_staff}")
    print(f"- is_active: {superuser.is_active}")
    
    # Test 1: Login API call (what frontend does)
    print("\n1. TESTING LOGIN API CALL")
    login_url = "http://127.0.0.1:8000/api/v1/auth/login/"
    login_data = {
        "email": "eva@test.com",
        "password": "12345678"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            login_response_data = response.json()
            print(f"✅ Login successful!")
            print(f"Token: {login_response_data.get('token', 'N/A')[:20]}...")
            print(f"Role: {login_response_data.get('role', 'N/A')}")
            
            # Test 2: Use the token to fetch payslips (what frontend does)
            print("\n2. TESTING PAYSLIPS API CALL WITH TOKEN")
            payslips_url = "http://127.0.0.1:8000/api/v1/payroll/payslips/"
            headers = {
                "Authorization": f"Token {login_response_data['token']}"
            }
            
            payslips_response = requests.get(payslips_url, headers=headers)
            print(f"Payslips response status: {payslips_response.status_code}")
            
            if payslips_response.status_code == 200:
                payslips_data = payslips_response.json()
                print(f"✅ Payslips API successful!")
                print(f"Total payslips: {payslips_data.get('count', 'N/A')}")
                print(f"Results in current page: {len(payslips_data.get('results', []))}")
                
                if payslips_data.get('results'):
                    print("Sample payslips:")
                    for i, payslip in enumerate(payslips_data['results'][:3]):
                        print(f"  - Payslip {i+1}: {payslip.get('employee_name', 'N/A')} - {payslip.get('pay_date', 'N/A')}")
                else:
                    print("❌ NO PAYSLIPS RETURNED!")
            else:
                print(f"❌ Payslips API failed with status {payslips_response.status_code}")
                try:
                    error_data = payslips_response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {payslips_response.text}")
                    
        else:
            print(f"❌ Login failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Test 3: Check token directly in database
    print("\n3. CHECKING TOKEN IN DATABASE")
    try:
        token = Token.objects.get(user=superuser)
        print(f"✅ Token exists in database: {token.key[:20]}...")
        print(f"Token user: {token.user.email}")
        print(f"Token user is_superuser: {token.user.is_superuser}")
    except Token.DoesNotExist:
        print("❌ No token found in database for this user")
    except Exception as e:
        print(f"❌ Error checking token: {e}")

if __name__ == '__main__':
    test_frontend_login_flow()
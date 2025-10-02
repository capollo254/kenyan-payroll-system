#!/usr/bin/env python
import os
import sys
import django
import requests

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.payroll.models import Payslip

User = get_user_model()

def test_superuser_own_payslips_only():
    """Test that superusers now only see their own payslips"""
    print("TESTING SUPERUSER ACCESS - OWN PAYSLIPS ONLY")
    print("=" * 60)
    
    # Test the eva@test.com superuser
    superuser_email = "eva@test.com"
    
    # Test 1: Direct API call
    print("1. TESTING API ACCESS")
    login_url = "http://127.0.0.1:8000/api/v1/auth/login/"
    login_data = {
        "email": superuser_email,
        "password": "12345678"
    }
    
    try:
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data['token']
            print(f"✅ Login successful! Role: {login_data['role']}")
            
            # Get payslips via API
            payslips_url = "http://127.0.0.1:8000/api/v1/payroll/payslips/"
            headers = {"Authorization": f"Token {token}"}
            
            payslips_response = requests.get(payslips_url, headers=headers)
            if payslips_response.status_code == 200:
                payslips_data = payslips_response.json()
                results = payslips_data.get('results', [])
                print(f"✅ API returned {len(results)} payslips")
                
                if results:
                    # Check if all payslips belong to the same employee
                    employee_names = set()
                    for payslip in results:
                        employee_data = payslip.get('employee', {})
                        employee_names.add(employee_data.get('full_name', 'Unknown'))
                    
                    print(f"Employees in payslips: {list(employee_names)}")
                    if len(employee_names) == 1:
                        print("✅ SUCCESS: All payslips belong to the same employee (own payslips only)")
                    else:
                        print("❌ ISSUE: Payslips belong to multiple employees")
                else:
                    print("ℹ️  No payslips found for this superuser")
            else:
                print(f"❌ API failed: {payslips_response.status_code}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    # Test 2: Direct database check
    print("\n2. TESTING DATABASE ACCESS")
    try:
        superuser = User.objects.get(email=superuser_email)
        print(f"Superuser: {superuser.email}")
        print(f"- is_superuser: {superuser.is_superuser}")
        print(f"- has employee_profile: {hasattr(superuser, 'employee_profile')}")
        
        if hasattr(superuser, 'employee_profile'):
            employee = superuser.employee_profile
            print(f"- employee name: {employee.full_name()}")
            
            # Get payslips for this employee only
            employee_payslips = Payslip.objects.filter(employee=employee)
            print(f"- employee's payslips: {employee_payslips.count()}")
            
            # Get total payslips in system
            total_payslips = Payslip.objects.all().count()
            print(f"- total system payslips: {total_payslips}")
            
            if employee_payslips.count() < total_payslips:
                print("✅ SUCCESS: Employee has fewer payslips than total system payslips")
            elif employee_payslips.count() == total_payslips:
                print("ℹ️  NOTE: Employee has same number of payslips as system total")
            else:
                print("❌ ERROR: Something is wrong with the counts")
        else:
            print("❌ Superuser has no employee profile")
            
    except User.DoesNotExist:
        print(f"❌ Superuser {superuser_email} not found")
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == '__main__':
    test_superuser_own_payslips_only()
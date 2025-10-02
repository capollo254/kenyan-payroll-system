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

def test_detailed_payslips_api():
    """Test the detailed payslips API response structure"""
    print("TESTING DETAILED PAYSLIPS API RESPONSE")
    print("=" * 50)
    
    # Step 1: Login
    login_url = "http://127.0.0.1:8000/api/v1/auth/login/"
    login_data = {
        "email": "eva@test.com",
        "password": "12345678"
    }
    
    try:
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        login_data = login_response.json()
        token = login_data['token']
        print(f"✅ Login successful! Role: {login_data['role']}")
        
        # Step 2: Fetch payslips
        payslips_url = "http://127.0.0.1:8000/api/v1/payroll/payslips/"
        headers = {"Authorization": f"Token {token}"}
        
        payslips_response = requests.get(payslips_url, headers=headers)
        if payslips_response.status_code != 200:
            print(f"❌ Payslips API failed: {payslips_response.status_code}")
            return
        
        payslips_data = payslips_response.json()
        print(f"✅ Payslips API successful!")
        print(f"Total count: {payslips_data.get('count', 'N/A')}")
        print(f"Results in page: {len(payslips_data.get('results', []))}")
        
        # Step 3: Examine the structure of the first payslip
        results = payslips_data.get('results', [])
        if results:
            first_payslip = results[0]
            print(f"\n📋 FIRST PAYSLIP STRUCTURE:")
            print(f"ID: {first_payslip.get('id', 'N/A')}")
            
            # Employee data
            employee_data = first_payslip.get('employee', {})
            print(f"\n👤 EMPLOYEE DATA:")
            print(f"  - ID: {employee_data.get('id', 'N/A')}")
            print(f"  - Full Name: {employee_data.get('full_name', 'N/A')}")
            print(f"  - Email: {employee_data.get('email', 'N/A')}")
            print(f"  - First Name: {employee_data.get('first_name', 'N/A')}")
            print(f"  - Last Name: {employee_data.get('last_name', 'N/A')}")
            
            # Payroll run data
            payroll_run_data = first_payslip.get('payroll_run', {})
            print(f"\n📅 PAYROLL RUN DATA:")
            print(f"  - ID: {payroll_run_data.get('id', 'N/A')}")
            print(f"  - Period Start: {payroll_run_data.get('period_start_date', 'N/A')}")
            print(f"  - Period End: {payroll_run_data.get('period_end_date', 'N/A')}")
            print(f"  - Run Date: {payroll_run_data.get('run_date', 'N/A')}")
            
            # Financial data
            print(f"\n💰 FINANCIAL DATA:")
            print(f"  - Gross Salary: {first_payslip.get('gross_salary', 'N/A')}")
            print(f"  - Total Gross Income: {first_payslip.get('total_gross_income', 'N/A')}")
            print(f"  - Net Pay: {first_payslip.get('net_pay', 'N/A')}")
            
            print(f"\n📋 RAW JSON SAMPLE (first payslip):")
            print(json.dumps(first_payslip, indent=2, default=str)[:1000] + "...")
        else:
            print("❌ No payslips found in results")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_detailed_payslips_api()
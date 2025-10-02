#!/usr/bin/env python3
"""
Script to run payroll for September 2025
This script will:
1. Authenticate with the API
2. Create a payroll run for September 2025
3. Display the results
"""

import requests
import json

BASE_URL = "https://web-production-85d2b.up.railway.app"

def authenticate():
    """Login and get authentication token"""
    login_url = f"{BASE_URL}/api/v1/auth/login/"
    credentials = {
        "email": "employee@demo.com",
        "password": "demo123"
    }
    
    try:
        response = requests.post(login_url, data=credentials)
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"✅ Authentication successful - Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def run_september_payroll(token):
    """Create payroll run for September 2025"""
    payroll_url = f"{BASE_URL}/api/v1/payroll/payroll-runs/"
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    payroll_data = {
        "period_start_date": "2025-09-01",
        "period_end_date": "2025-09-30"
    }
    
    try:
        print("🔄 Creating payroll run for September 2025...")
        response = requests.post(payroll_url, headers=headers, json=payroll_data)
        
        if response.status_code == 201:
            payroll_result = response.json()
            print("✅ Payroll run created successfully!")
            print(f"📋 Payroll Run ID: {payroll_result.get('id')}")
            print(f"📅 Run Date: {payroll_result.get('run_date')}")
            print(f"📊 Period: {payroll_result.get('period_start_date')} to {payroll_result.get('period_end_date')}")
            print(f"👤 Run By: {payroll_result.get('run_by')}")
            return payroll_result
        else:
            print(f"❌ Payroll creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Payroll creation error: {e}")
        return None

def check_payslips(token):
    """Check the generated payslips"""
    payslips_url = f"{BASE_URL}/api/v1/payroll/payslips/"
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(payslips_url, headers=headers)
        if response.status_code == 200:
            payslips_data = response.json()
            count = payslips_data.get('count', 0)
            print(f"📄 Total payslips generated: {count}")
            
            if count > 0:
                results = payslips_data.get('results', [])
                print("📋 Recent payslips:")
                for i, payslip in enumerate(results[:5]):  # Show first 5
                    employee_name = payslip.get('employee', {}).get('full_name', 'Unknown')
                    net_pay = payslip.get('net_pay', 0)
                    print(f"  {i+1}. {employee_name}: KES {net_pay}")
            return True
        else:
            print(f"❌ Failed to fetch payslips: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error fetching payslips: {e}")
        return False

def main():
    """Main function to run the payroll process"""
    print("🚀 Starting September 2025 Payroll Run")
    print("="*50)
    
    # Step 1: Authenticate
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Run payroll for September
    payroll_result = run_september_payroll(token)
    if not payroll_result:
        print("❌ Payroll run failed")
        return
    
    # Step 3: Check generated payslips
    print("\n" + "="*50)
    print("📊 Checking generated payslips...")
    check_payslips(token)
    
    print("\n✅ Payroll process completed!")
    print("You can now view the payslips in the frontend at http://localhost:3001")

if __name__ == "__main__":
    main()
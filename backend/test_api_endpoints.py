#!/usr/bin/env python
import requests
import json

def test_api_endpoints():
    print("=== Testing API Endpoints ===")
    
    # First, login to get a token
    login_url = 'http://127.0.0.1:8000/api/v1/auth/login/'
    login_data = {
        'email': 'admin@demo.com',
        'password': 'admin123'
    }
    
    print("🔐 Logging in...")
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"   ✅ Login successful, token: {token[:20]}...")
            
            # Set headers for authenticated requests
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'
            }
            
            # Test endpoints
            endpoints = [
                ('User Profile', 'http://127.0.0.1:8000/api/v1/auth/profile/'),
                ('Employees List', 'http://127.0.0.1:8000/api/v1/employees/'),
                ('Payslips List', 'http://127.0.0.1:8000/api/v1/payroll/payslips/'),
                ('Payroll Runs', 'http://127.0.0.1:8000/api/v1/payroll/payroll-runs/'),
            ]
            
            for name, url in endpoints:
                print(f"\n🧪 Testing {name}...")
                try:
                    response = requests.get(url, headers=headers)
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"   ✅ Success - Response contains {len(data)} fields")
                            if 'results' in data:
                                print(f"   📊 Results count: {len(data['results'])}")
                        elif isinstance(data, list):
                            print(f"   ✅ Success - List with {len(data)} items")
                        else:
                            print(f"   ✅ Success - Response type: {type(data)}")
                    else:
                        print(f"   ❌ Error: {response.text}")
                        
                except Exception as e:
                    print(f"   ❌ Request failed: {e}")
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")

if __name__ == '__main__':
    test_api_endpoints()
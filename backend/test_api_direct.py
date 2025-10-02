#!/usr/bin/env python
import os
import django
import requests
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import authenticate

# Test authentication
print("=== Testing Direct Authentication ===")
user = authenticate(username='admin@demo.com', password='admin123')
print(f"Django authenticate result: {user is not None}")
if user:
    print(f"User: {user.email}, Active: {user.is_active}, Staff: {user.is_staff}")

# Test API endpoint
print("\n=== Testing API Endpoint ===")
try:
    url = 'http://127.0.0.1:8000/api/v1/auth/login/'
    data = {
        'email': 'admin@demo.com',
        'password': 'admin123'
    }
    
    response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Token: {result.get('token', 'Not found')}")
        print(f"Role: {result.get('role', 'Not found')}")
    
except Exception as e:
    print(f"Error: {e}")
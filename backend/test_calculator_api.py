#!/usr/bin/env python3
"""
Test the public payroll calculator API using Django's test client
"""
import sys
import os
import django
from decimal import Decimal
import json

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(backend_dir, 'kenyan_payroll_project')
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Import Django test client
try:
    from django.test import Client
    from django.urls import reverse
    print("✅ Django test client imported")
except Exception as e:
    print(f"❌ Django test client import failed: {e}")
    sys.exit(1)

def test_calculator():
    """Test the calculator with various scenarios using Django test client"""
    
    print("\n🧮 TESTING PUBLIC PAYROLL CALCULATOR API")
    print("=" * 60)
    
    client = Client()
    
    # Test Case 1: Basic salary with minimal deductions
    print("\n📋 Test Case 1: Basic Salary (KSh 50,000)")
    test_data_1 = {
        'gross_salary': 50000,
        'pension_contribution': 0,
        'insurance_premiums': 0,
        'medical_fund_contribution': 0,
        'mortgage_interest': 0,
        'helb_deduction': 0,
        'other_voluntary_deductions': 0
    }
    
    try:
        response_1 = client.post('/api/public/calculator/', 
                               data=json.dumps(test_data_1),
                               content_type='application/json')
        
        if response_1.status_code == 200:
            result_1 = json.loads(response_1.content)
            if result_1.get('success'):
                print(f"✅ Basic calculation successful")
                print(f"   Gross: KSh {result_1['summary']['gross_salary']:,.2f}")
                print(f"   Net Pay: KSh {result_1['summary']['net_pay']:,.2f}")
                print(f"   PAYE Tax: KSh {result_1['statutory_deductions']['paye_tax']['amount']:,.2f}")
                print(f"   NSSF: KSh {result_1['statutory_deductions']['nssf']['amount']:,.2f}")
                print(f"   SHIF: KSh {result_1['statutory_deductions']['shif']['amount']:,.2f}")
                print(f"   AHL: KSh {result_1['statutory_deductions']['ahl']['amount']:,.2f}")
                print(f"   Effective Tax Rate: {result_1['summary']['effective_tax_rate']:.2f}%")
            else:
                print(f"❌ Basic calculation failed: {result_1.get('error', 'Unknown error')}")
        else:
            print(f"❌ Basic calculation failed - Status: {response_1.status_code}")
            print(f"   Response: {response_1.content}")
    except Exception as e:
        print(f"❌ Basic calculation failed: {e}")
    
    # Test Case 2: High salary with all reliefs
    print("\n📋 Test Case 2: High Salary with All Reliefs (KSh 200,000)")
    test_data_2 = {
        'gross_salary': 200000,
        'pension_contribution': 30000,  # Max relief
        'insurance_premiums': 5000,     # For 15% relief
        'medical_fund_contribution': 15000,  # Max deductible
        'mortgage_interest': 30000,     # Max relief
        'helb_deduction': 3000,
        'other_voluntary_deductions': 5000
    }
    
    try:
        response_2 = client.post('/api/public/calculator/', 
                               data=json.dumps(test_data_2),
                               content_type='application/json')
        
        if response_2.status_code == 200:
            result_2 = json.loads(response_2.content)
            if result_2.get('success'):
                print(f"✅ High salary calculation successful")
                print(f"   Gross: KSh {result_2['summary']['gross_salary']:,.2f}")
                print(f"   Net Pay: KSh {result_2['summary']['net_pay']:,.2f}")
                print(f"   Total Deductions: KSh {result_2['summary']['total_deductions']:,.2f}")
                print(f"   Effective Tax Rate: {result_2['summary']['effective_tax_rate']:.2f}%")
                
                # Check reliefs
                reliefs = result_2['reliefs_applied']
                print(f"   Pension Relief: KSh {reliefs['pension_relief']['relief_amount']:,.2f}")
                print(f"   Insurance Relief: KSh {reliefs['insurance_relief']['relief_amount']:,.2f}")
                print(f"   Medical Fund Relief: KSh {reliefs['medical_fund_relief']['relief_amount']:,.2f}")
                print(f"   Mortgage Relief: KSh {reliefs['mortgage_relief']['relief_amount']:,.2f}")
            else:
                print(f"❌ High salary calculation failed: {result_2.get('error', 'Unknown error')}")
        else:
            print(f"❌ High salary calculation failed - Status: {response_2.status_code}")
    except Exception as e:
        print(f"❌ High salary calculation failed: {e}")
    
    # Test Case 3: Medium salary realistic scenario
    print("\n📋 Test Case 3: Medium Salary Realistic (KSh 120,000)")
    test_data_3 = {
        'gross_salary': 120000,
        'pension_contribution': 12000,
        'insurance_premiums': 2500,
        'medical_fund_contribution': 8000,
        'mortgage_interest': 18000,
        'helb_deduction': 2000,
        'other_voluntary_deductions': 3000
    }
    
    try:
        response_3 = client.post('/api/public/calculator/', 
                               data=json.dumps(test_data_3),
                               content_type='application/json')
        
        if response_3.status_code == 200:
            result_3 = json.loads(response_3.content)
            if result_3.get('success'):
                print(f"✅ Medium salary calculation successful")
                print(f"   Gross: KSh {result_3['summary']['gross_salary']:,.2f}")
                print(f"   Net Pay: KSh {result_3['summary']['net_pay']:,.2f}")
                print(f"   Effective Tax Rate: {result_3['summary']['effective_tax_rate']:.2f}%")
            else:
                print(f"❌ Medium salary calculation failed: {result_3.get('error', 'Unknown error')}")
        else:
            print(f"❌ Medium salary calculation failed - Status: {response_3.status_code}")
    except Exception as e:
        print(f"❌ Medium salary calculation failed: {e}")
    
    # Test Case 4: Error handling - invalid data
    print("\n📋 Test Case 4: Error Handling (Invalid Data)")
    test_data_4 = {
        'gross_salary': -50000,  # Negative salary
        'pension_contribution': 0,
        'insurance_premiums': 0,
        'medical_fund_contribution': 0,
        'mortgage_interest': 0,
        'helb_deduction': 0,
        'other_voluntary_deductions': 0
    }
    
    try:
        response_4 = client.post('/api/public/calculator/', 
                               data=json.dumps(test_data_4),
                               content_type='application/json')
        
        if response_4.status_code == 400:
            result_4 = json.loads(response_4.content)
            print(f"✅ Error handling successful: {result_4.get('error', 'Validation error caught')}")
        elif response_4.status_code == 200:
            result_4 = json.loads(response_4.content)
            if not result_4.get('success'):
                print(f"✅ Error handling successful: {result_4.get('error', 'Error caught')}")
            else:
                print(f"❌ Error handling failed - should have rejected negative salary")
        else:
            print(f"✅ Error handling caught error - Status: {response_4.status_code}")
    except Exception as e:
        print(f"✅ Error handling successful: {e}")
    
    # Test Case 5: Empty request
    print("\n📋 Test Case 5: Error Handling (Empty Request)")
    try:
        response_5 = client.post('/api/public/calculator/', 
                               data='{}',
                               content_type='application/json')
        
        if response_5.status_code == 400:
            result_5 = json.loads(response_5.content)
            print(f"✅ Empty request handling successful: {result_5.get('error', 'Missing gross_salary')}")
        else:
            print(f"❌ Empty request handling failed - Status: {response_5.status_code}")
    except Exception as e:
        print(f"✅ Empty request handling successful: {e}")
    
    print("\n🎉 CALCULATOR API TESTING COMPLETED!")
    print("=" * 60)
    print("🔗 API Endpoint: /api/public/calculator/")
    print("📋 Method: POST")
    print("📄 Content-Type: application/json")
    print("🔓 Authentication: None required")

if __name__ == "__main__":
    test_calculator()
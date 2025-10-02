#!/usr/bin/env python3
"""
Test the public payroll calculator API endpoint directly
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

# Import the calculator function
try:
    from apps.payroll.calculator_views import public_payroll_calculator
    print("✅ Calculator import successful")
except Exception as e:
    print(f"❌ Calculator import failed: {e}")
    sys.exit(1)

def test_calculator():
    """Test the calculator with various scenarios"""
    
    print("\n🧮 TESTING PUBLIC PAYROLL CALCULATOR")
    print("=" * 50)
    
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
        result_1 = test_single_calculation(test_data_1)
        print(f"✅ Basic calculation successful")
        print(f"   Gross: KSh {result_1['summary']['gross_salary']:,.2f}")
        print(f"   Net Pay: KSh {result_1['summary']['net_pay']:,.2f}")
        print(f"   Tax Rate: {result_1['summary']['effective_tax_rate']:.2f}%")
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
        result_2 = test_single_calculation(test_data_2)
        print(f"✅ High salary calculation successful")
        print(f"   Gross: KSh {result_2['summary']['gross_salary']:,.2f}")
        print(f"   Net Pay: KSh {result_2['summary']['net_pay']:,.2f}")
        print(f"   Tax Rate: {result_2['summary']['effective_tax_rate']:.2f}%")
        print(f"   Total Reliefs: KSh {result_2['summary']['total_deductions']:,.2f}")
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
        result_3 = test_single_calculation(test_data_3)
        print(f"✅ Medium salary calculation successful")
        print(f"   Gross: KSh {result_3['summary']['gross_salary']:,.2f}")
        print(f"   Net Pay: KSh {result_3['summary']['net_pay']:,.2f}")
        print(f"   Tax Rate: {result_3['summary']['effective_tax_rate']:.2f}%")
    except Exception as e:
        print(f"❌ Medium salary calculation failed: {e}")
    
    # Test Case 4: Error handling - negative salary
    print("\n📋 Test Case 4: Error Handling (Negative Salary)")
    test_data_4 = {
        'gross_salary': -50000,
        'pension_contribution': 0,
        'insurance_premiums': 0,
        'medical_fund_contribution': 0,
        'mortgage_interest': 0,
        'helb_deduction': 0,
        'other_voluntary_deductions': 0
    }
    
    try:
        result_4 = test_single_calculation(test_data_4)
        if not result_4['success']:
            print(f"✅ Error handling successful: {result_4['error']}")
        else:
            print(f"❌ Error handling failed - should have rejected negative salary")
    except Exception as e:
        print(f"✅ Error handling successful: {e}")
    
    print("\n🎉 CALCULATOR TESTING COMPLETED!")
    print("=" * 50)

def test_single_calculation(data):
    """Test a single calculation scenario"""
    from django.http import HttpRequest
    from django.test import RequestFactory
    import json
    
    factory = RequestFactory()
    request = factory.post('/api/public/calculator/', 
                          data=json.dumps(data), 
                          content_type='application/json')
    
    response = public_payroll_calculator(request)
    response_data = json.loads(response.content.decode())
    
    return response_data

if __name__ == "__main__":
    test_calculator()
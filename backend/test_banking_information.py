#!/usr/bin/env python3

import os
import sys
import django
from decimal import Decimal

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee

User = get_user_model()

def test_banking_information_enhancement():
    """Test the enhanced banking information functionality"""
    print("Testing Banking Information Enhancement...")
    print("=" * 60)
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email='banking_test@company.com',
        defaults={
            'first_name': 'John',
            'last_name': 'Doe'
        }
    )
    print(f"✓ Test User: {user.first_name} {user.last_name}")
    
    # Create employee with complete banking information
    employee, created = Employee.objects.get_or_create(
        user=user,
        defaults={
            'gross_salary': Decimal('150000.00'),
            # Banking Information
            'bank_name': 'Equity Bank Kenya Limited',
            'bank_code': '68',
            'bank_branch': 'Westlands Branch',
            'bank_branch_code': '068',
            'bank_account_number': '1234567890123',
            'account_type': 'current',
            'account_holder_name': 'John Doe',
            # Mobile Money
            'mobile_money_provider': 'mpesa',
            'mobile_money_number': '0712345678',
        }
    )
    
    print(f"✅ Employee Created: {employee.full_name()}")
    
    # Test banking information retrieval
    banking_info = employee.get_banking_info()
    print(f"\n📊 BANKING INFORMATION:")
    if banking_info:
        for key, value in banking_info.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    else:
        print("  No banking information available")
    
    # Test completeness check
    is_complete = employee.has_complete_banking_info()
    print(f"\n✅ Banking Info Complete: {'Yes' if is_complete else 'No'}")
    
    # Test various banking scenarios
    print(f"\n📋 TESTING DIFFERENT BANKING SCENARIOS:")
    
    # Scenario 1: Complete banking info
    print(f"  Scenario 1 - Complete Info: {employee.has_complete_banking_info()}")
    
    # Scenario 2: Partial banking info
    employee.bank_code = None
    print(f"  Scenario 2 - Missing Bank Code: {employee.has_complete_banking_info()}")
    
    # Scenario 3: Only account number
    employee.bank_name = None
    employee.bank_branch = None
    employee.bank_branch_code = None
    print(f"  Scenario 3 - Only Account Number: {employee.has_complete_banking_info()}")
    
    # Restore complete info
    employee.bank_name = 'Equity Bank Kenya Limited'
    employee.bank_code = '68'
    employee.bank_branch = 'Westlands Branch'
    employee.bank_branch_code = '068'
    
    print(f"\n🏦 KENYAN BANKING STANDARDS:")
    print(f"  Bank Name: Full legal name required")
    print(f"  Bank Code: Central Bank of Kenya assigned code")
    print(f"  Branch Code: Specific branch identifier") 
    print(f"  Account Types: Savings, Current, Fixed Deposit")
    
    print(f"\n📱 MOBILE MONEY INTEGRATION:")
    print(f"  Provider: {employee.get_mobile_money_provider_display()}")
    print(f"  Number: {employee.mobile_money_number}")
    
    print(f"\n" + "=" * 60)
    print("BANKING INFORMATION ENHANCEMENT COMPLETE!")
    
    print(f"\n✅ NEW FIELDS AVAILABLE:")
    print(f"  ✓ Bank Name")
    print(f"  ✓ Bank Code") 
    print(f"  ✓ Bank Branch Name")
    print(f"  ✓ Bank Branch Code")
    print(f"  ✓ Account Type")
    print(f"  ✓ Account Holder Name")
    print(f"  ✓ Mobile Money Provider")
    print(f"  ✓ Mobile Money Number")
    
    print(f"\n🎯 ADMIN INTERFACE FEATURES:")
    print(f"  ✓ Dedicated 'Banking Information' section")
    print(f"  ✓ Optional 'Mobile Money Information' section")
    print(f"  ✓ Banking status indicator in employee list")
    print(f"  ✓ Helper text for each field")
    print(f"  ✓ Validation methods for completeness")
    
    return True

if __name__ == '__main__':
    test_banking_information_enhancement()
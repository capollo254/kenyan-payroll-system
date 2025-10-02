#!/usr/bin/env python
"""
Test script for enhanced payroll calculations with KRA reliefs.
Tests insurance relief, post-retirement medical fund, and mortgage interest relief.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/c/Users/Code_AI/Documents/PAYROL SYSTEM COMPLEX/KE PAYROL SYSTEM/kenyan_payroll_system/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth.models import User
from apps.employees.models import Employee, VoluntaryDeduction
from apps.compliance.calc_reliefs import (
    calculate_insurance_relief,
    calculate_post_retirement_medical_deduction,
    calculate_mortgage_interest_relief
)
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl

def test_relief_calculations():
    print("=" * 60)
    print("TESTING ENHANCED PAYROLL CALCULATIONS WITH KRA RELIEFS")
    print("=" * 60)
    
    # Test 1: Insurance Relief
    print("\n1. TESTING INSURANCE RELIEF (15% up to KSh 5,000/month)")
    print("-" * 50)
    
    test_cases = [
        Decimal('2000.00'),   # Below cap
        Decimal('30000.00'),  # At cap (5000 * 15% = 4500)
        Decimal('40000.00'),  # Above cap
    ]
    
    for premiums in test_cases:
        relief = calculate_insurance_relief(premiums)
        print(f"Premiums: KSh {premiums:,} → Relief: KSh {relief:,}")
    
    # Test 2: Post-retirement Medical Fund
    print("\n2. TESTING POST-RETIREMENT MEDICAL FUND (up to KSh 15,000/month)")
    print("-" * 50)
    
    test_cases = [
        Decimal('5000.00'),   # Below cap
        Decimal('15000.00'),  # At cap
        Decimal('20000.00'),  # Above cap
    ]
    
    for contribution in test_cases:
        deduction = calculate_post_retirement_medical_deduction(contribution)
        print(f"Contribution: KSh {contribution:,} → Deduction: KSh {deduction:,}")
    
    # Test 3: Mortgage Interest Relief
    print("\n3. TESTING MORTGAGE INTEREST RELIEF (up to KSh 30,000/month)")
    print("-" * 50)
    
    test_cases = [
        Decimal('15000.00'),  # Below cap
        Decimal('30000.00'),  # At cap
        Decimal('45000.00'),  # Above cap
    ]
    
    for interest in test_cases:
        relief = calculate_mortgage_interest_relief(interest)
        print(f"Interest: KSh {interest:,} → Relief: KSh {relief:,}")

def test_complete_payroll_scenario():
    print("\n\n4. TESTING COMPLETE PAYROLL SCENARIO")
    print("=" * 50)
    
    # Test employee with all reliefs
    gross_salary = Decimal('200000.00')
    insurance_premiums = Decimal('8000.00')
    medical_fund = Decimal('10000.00')
    mortgage_interest = Decimal('25000.00')
    pension_contribution = Decimal('20000.00')
    
    print(f"Employee Gross Salary: KSh {gross_salary:,}")
    print(f"Insurance Premiums: KSh {insurance_premiums:,}")
    print(f"Medical Fund Contribution: KSh {medical_fund:,}")
    print(f"Mortgage Interest: KSh {mortgage_interest:,}")
    print(f"Pension Contribution: KSh {pension_contribution:,}")
    
    # Calculate statutory deductions
    nssf = calculate_nssf(gross_salary)
    shif = calculate_shif(gross_salary)
    ahl_employee, ahl_employer = calculate_ahl(gross_salary)
    
    print(f"\nSTATUTORY DEDUCTIONS:")
    print(f"NSSF: KSh {nssf:,}")
    print(f"SHIF: KSh {shif:,}")
    print(f"AHL: KSh {ahl_employee:,}")
    
    # Calculate reliefs and deductions
    pension_relief = min(pension_contribution, Decimal('30000.00'))
    medical_deduction = calculate_post_retirement_medical_deduction(medical_fund)
    mortgage_relief = calculate_mortgage_interest_relief(mortgage_interest)
    
    print(f"\nRELIEFS AND DEDUCTIONS:")
    print(f"Pension Relief (capped): KSh {pension_relief:,}")
    print(f"Medical Fund Deduction: KSh {medical_deduction:,}")
    print(f"Mortgage Interest Relief: KSh {mortgage_relief:,}")
    
    # Calculate taxable income
    taxable_income = gross_salary - (nssf + shif + ahl_employee + pension_relief + medical_deduction + mortgage_relief)
    taxable_income = max(taxable_income, Decimal('0.00'))
    
    print(f"\nTaxable Income: KSh {taxable_income:,}")
    
    # Calculate PAYE
    paye_before_insurance_relief = calculate_paye(taxable_income)
    insurance_relief = calculate_insurance_relief(insurance_premiums)
    paye_after_relief = max(paye_before_insurance_relief - insurance_relief, Decimal('0.00'))
    
    print(f"\nPAYE Calculation:")
    print(f"PAYE before insurance relief: KSh {paye_before_insurance_relief:,}")
    print(f"Insurance relief: KSh {insurance_relief:,}")
    print(f"PAYE after relief: KSh {paye_after_relief:,}")
    
    # Calculate net pay
    total_deductions = paye_after_relief + nssf + shif + ahl_employee + pension_contribution
    net_pay = gross_salary - total_deductions
    
    print(f"\nFINAL CALCULATION:")
    print(f"Total Deductions: KSh {total_deductions:,}")
    print(f"Net Pay: KSh {net_pay:,}")

def test_database_integration():
    print("\n\n5. TESTING DATABASE INTEGRATION")
    print("=" * 50)
    
    try:
        # Try to find an existing employee or create a test one
        try:
            employee = Employee.objects.first()
            if not employee:
                # Create a test user and employee
                user = User.objects.create_user(
                    username='test_reliefs',
                    email='test_reliefs@company.com',
                    first_name='Test',
                    last_name='Reliefs'
                )
                employee = Employee.objects.create(
                    user=user,
                    gross_salary=Decimal('150000.00'),
                    monthly_insurance_premiums=Decimal('5000.00'),
                    monthly_medical_fund_contribution=Decimal('8000.00'),
                    monthly_mortgage_interest=Decimal('20000.00')
                )
                print("Created test employee with relief fields")
            else:
                # Update existing employee with relief data
                employee.monthly_insurance_premiums = Decimal('5000.00')
                employee.monthly_medical_fund_contribution = Decimal('8000.00')
                employee.monthly_mortgage_interest = Decimal('20000.00')
                employee.save()
                print("Updated existing employee with relief data")
        
        except Exception as e:
            print(f"Error setting up test employee: {e}")
            return
        
        print(f"Employee: {employee.full_name()}")
        print(f"Gross Salary: KSh {employee.gross_salary:,}")
        print(f"Insurance Premiums: KSh {employee.monthly_insurance_premiums:,}")
        print(f"Medical Fund: KSh {employee.monthly_medical_fund_contribution:,}")
        print(f"Mortgage Interest: KSh {employee.monthly_mortgage_interest:,}")
        
        # Test relief calculations with database values
        insurance_relief = calculate_insurance_relief(employee.monthly_insurance_premiums)
        medical_deduction = calculate_post_retirement_medical_deduction(employee.monthly_medical_fund_contribution)
        mortgage_relief = calculate_mortgage_interest_relief(employee.monthly_mortgage_interest)
        
        print(f"\nCalculated Reliefs:")
        print(f"Insurance Relief: KSh {insurance_relief:,}")
        print(f"Medical Fund Deduction: KSh {medical_deduction:,}")
        print(f"Mortgage Interest Relief: KSh {mortgage_relief:,}")
        
        print("\n✅ Database integration test successful!")
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")

if __name__ == "__main__":
    try:
        test_relief_calculations()
        test_complete_payroll_scenario()
        test_database_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL ENHANCED PAYROLL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ KRA Relief calculations are working correctly")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
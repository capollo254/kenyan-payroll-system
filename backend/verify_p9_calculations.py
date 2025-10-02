#!/usr/bin/env python3
"""
Verify P9 Tax Calculations for Kenya
"""

import os
import sys
import django
from decimal import Decimal

# Add backend to path and configure Django
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.reports.models import P9Report, P9MonthlyBreakdown

def verify_kenya_tax_brackets():
    """Verify Kenya tax brackets for 2024"""
    print("=== Kenya Tax Brackets 2024 ===")
    print("Annual Income Tax Brackets:")
    print("  • 0 - KES 288,000: 10%")
    print("  • KES 288,001 - KES 388,000: 25%") 
    print("  • Above KES 388,000: 30%")
    print("\nPersonal Relief: KES 2,400/month (KES 28,800/year)")
    print("AHL (Affordable Housing Levy): 1.5% of gross pay")
    print("Retirement: Lower of 30% basic salary or KES 30,000/month (KES 360,000/year)")
    print()

def calculate_expected_tax(chargeable_pay):
    """Calculate expected PAYE tax based on Kenya brackets"""
    if chargeable_pay <= 0:
        return Decimal('0.00')
    
    # Kenya tax brackets (annual amounts)
    tax = Decimal('0.00')
    remaining = chargeable_pay
    
    # First bracket: Up to 288,000 at 10%
    bracket1 = min(remaining, Decimal('288000'))
    tax += bracket1 * Decimal('0.10')
    remaining -= bracket1
    
    if remaining > 0:
        # Second bracket: Next 100,000 (288,001 - 388,000) at 25%
        bracket2 = min(remaining, Decimal('100000'))
        tax += bracket2 * Decimal('0.25')
        remaining -= bracket2
        
        if remaining > 0:
            # Third bracket: Above 388,000 at 30%
            tax += remaining * Decimal('0.30')
    
    return tax

def verify_p9_calculations():
    print("=== P9 Calculation Verification ===")
    
    p9_reports = P9Report.objects.all()
    
    if not p9_reports:
        print("❌ No P9 reports found in database")
        return False
    
    for p9 in p9_reports:
        print(f"\n📋 Verifying: {p9.employee_name} ({p9.tax_year})")
        print(f"Status: {p9.status}")
        
        # Display current values
        print(f"\n💰 Income Breakdown:")
        print(f"  Basic Salary: KES {p9.total_basic_salary:,.2f}")
        print(f"  Benefits Non-Cash: KES {p9.total_benefits_non_cash:,.2f}")
        print(f"  Value of Quarters: KES {p9.total_value_of_quarters:,.2f}")
        print(f"  TOTAL GROSS PAY: KES {p9.total_gross_pay:,.2f}")
        
        # Verify gross pay calculation
        expected_gross = p9.total_basic_salary + p9.total_benefits_non_cash + p9.total_value_of_quarters
        gross_correct = abs(expected_gross - p9.total_gross_pay) < Decimal('0.01')
        print(f"  ✅ Gross Pay Calculation: {'Correct' if gross_correct else 'INCORRECT'}")
        if not gross_correct:
            print(f"    Expected: KES {expected_gross:,.2f}")
        
        print(f"\n🏠 Deductions:")
        print(f"  Retirement (30% cap): KES {p9.retirement_30_percent:,.2f}")
        print(f"  Retirement (actual): KES {p9.retirement_actual:,.2f}")
        print(f"  AHL (1.5%): KES {p9.total_ahl:,.2f}")
        print(f"  SHIF: KES {p9.total_shif:,.2f}")
        print(f"  TOTAL DEDUCTIONS: KES {p9.total_deductions:,.2f}")
        
        # Verify AHL calculation (1.5% of gross pay)
        expected_ahl = p9.total_gross_pay * Decimal('0.015')
        ahl_correct = abs(expected_ahl - p9.total_ahl) < Decimal('0.01')
        print(f"  ✅ AHL Calculation: {'Correct' if ahl_correct else 'INCORRECT'}")
        if not ahl_correct:
            print(f"    Expected: KES {expected_ahl:,.2f}")
        
        # Verify retirement 30% calculation
        expected_retirement_30 = p9.total_basic_salary * Decimal('0.30')
        retirement_correct = abs(expected_retirement_30 - p9.retirement_30_percent) < Decimal('0.01')
        print(f"  ✅ Retirement 30%: {'Correct' if retirement_correct else 'INCORRECT'}")
        if not retirement_correct:
            print(f"    Expected: KES {expected_retirement_30:,.2f}")
        
        print(f"\n📊 Tax Calculations:")
        print(f"  Chargeable Pay: KES {p9.chargeable_pay:,.2f}")
        print(f"  Tax Charged: KES {p9.tax_charged:,.2f}")
        print(f"  Personal Relief: KES {p9.total_personal_relief:,.2f}")
        print(f"  PAYE Tax: KES {p9.total_paye_tax:,.2f}")
        
        # Verify chargeable pay
        expected_chargeable = p9.total_gross_pay - p9.total_deductions
        chargeable_correct = abs(expected_chargeable - p9.chargeable_pay) < Decimal('0.01')
        print(f"  ✅ Chargeable Pay: {'Correct' if chargeable_correct else 'INCORRECT'}")
        if not chargeable_correct:
            print(f"    Expected: KES {expected_chargeable:,.2f}")
        
        # Verify tax charged using Kenya brackets
        expected_tax_charged = calculate_expected_tax(p9.chargeable_pay)
        tax_charged_correct = abs(expected_tax_charged - p9.tax_charged) < Decimal('0.01')
        print(f"  ✅ Tax Charged: {'Correct' if tax_charged_correct else 'INCORRECT'}")
        if not tax_charged_correct:
            print(f"    Expected: KES {expected_tax_charged:,.2f}")
            print(f"    Difference: KES {abs(expected_tax_charged - p9.tax_charged):,.2f}")
        
        # Verify PAYE tax
        expected_paye = max(Decimal('0.00'), p9.tax_charged - p9.total_personal_relief - p9.total_insurance_relief)
        paye_correct = abs(expected_paye - p9.total_paye_tax) < Decimal('0.01')
        print(f"  ✅ PAYE Tax: {'Correct' if paye_correct else 'INCORRECT'}")
        if not paye_correct:
            print(f"    Expected: KES {expected_paye:,.2f}")
        
        # Overall assessment
        all_correct = all([gross_correct, ahl_correct, retirement_correct, chargeable_correct, tax_charged_correct, paye_correct])
        print(f"\n🎯 Overall: {'✅ ALL CALCULATIONS CORRECT' if all_correct else '❌ ERRORS FOUND'}")
        
        # Manual verification of tax brackets
        print(f"\n🔍 Manual Tax Bracket Verification:")
        print(f"Chargeable Pay: KES {p9.chargeable_pay:,.2f}")
        
        if p9.chargeable_pay <= 288000:
            expected_tax = p9.chargeable_pay * Decimal('0.10')
            print(f"Falls in 10% bracket: KES {expected_tax:,.2f}")
        elif p9.chargeable_pay <= 388000:
            tax_10 = Decimal('288000') * Decimal('0.10')
            tax_25 = (p9.chargeable_pay - Decimal('288000')) * Decimal('0.25')
            expected_tax = tax_10 + tax_25
            print(f"10% bracket: KES {tax_10:,.2f}")
            print(f"25% bracket: KES {tax_25:,.2f}")
            print(f"Total tax: KES {expected_tax:,.2f}")
        else:
            tax_10 = Decimal('288000') * Decimal('0.10')
            tax_25 = Decimal('100000') * Decimal('0.25')
            tax_30 = (p9.chargeable_pay - Decimal('388000')) * Decimal('0.30')
            expected_tax = tax_10 + tax_25 + tax_30
            print(f"10% bracket: KES {tax_10:,.2f}")
            print(f"25% bracket: KES {tax_25:,.2f}")
            print(f"30% bracket: KES {tax_30:,.2f}")
            print(f"Total tax: KES {expected_tax:,.2f}")
        
        return all_correct
    
    return False

def check_monthly_breakdown():
    """Check monthly breakdown consistency"""
    print("\n=== Monthly Breakdown Verification ===")
    
    for p9 in P9Report.objects.all():
        monthly_data = p9.monthly_breakdown.all().order_by('month')
        if not monthly_data:
            print(f"❌ No monthly data for {p9.employee_name}")
            continue
        
        print(f"\n📅 Monthly data for {p9.employee_name}:")
        
        # Calculate totals from monthly data
        total_basic = sum(m.basic_salary for m in monthly_data)
        total_gross = sum(m.gross_pay for m in monthly_data)
        total_paye = sum(m.paye_tax for m in monthly_data)
        
        print(f"Monthly totals:")
        print(f"  Basic Salary: KES {total_basic:,.2f} (P9: KES {p9.total_basic_salary:,.2f})")
        print(f"  Gross Pay: KES {total_gross:,.2f} (P9: KES {p9.total_gross_pay:,.2f})")
        print(f"  PAYE Tax: KES {total_paye:,.2f} (P9: KES {p9.total_paye_tax:,.2f})")
        
        # Check consistency
        basic_match = abs(total_basic - p9.total_basic_salary) < Decimal('0.01')
        gross_match = abs(total_gross - p9.total_gross_pay) < Decimal('0.01')
        paye_match = abs(total_paye - p9.total_paye_tax) < Decimal('0.01')
        
        print(f"  ✅ Basic Salary Match: {'Yes' if basic_match else 'No'}")
        print(f"  ✅ Gross Pay Match: {'Yes' if gross_match else 'No'}")  
        print(f"  ✅ PAYE Tax Match: {'Yes' if paye_match else 'No'}")

if __name__ == '__main__':
    try:
        verify_kenya_tax_brackets()
        calculations_correct = verify_p9_calculations()
        check_monthly_breakdown()
        
        if calculations_correct:
            print("\n🎉 P9 calculations are CORRECT and comply with Kenya tax law!")
        else:
            print("\n⚠️ P9 calculations need review - some errors found")
            
    except Exception as e:
        print(f"❌ Error verifying calculations: {e}")
        import traceback
        traceback.print_exc()
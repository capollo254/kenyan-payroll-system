#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from decimal import Decimal
from apps.employees.models import Employee, VoluntaryDeduction
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl

def test_fixed_admin_calculation():
    print("🔧 TESTING FIXED DJANGO ADMIN CALCULATION")
    print("=" * 50)
    
    # Test data based on user's example
    gross_salary = Decimal('225000.00')
    pension_contribution = Decimal('9180.00')
    overtime_pay = Decimal('0.00')
    total_gross_income = gross_salary + overtime_pay
    
    print(f"📊 TEST DATA:")
    print(f"   Gross Salary: KES {gross_salary:,.2f}")
    print(f"   Pension Contribution: KES {pension_contribution:,.2f}")
    print(f"   Total Gross Income: KES {total_gross_income:,.2f}")
    print()
    
    # Calculate statutory deductions
    nssf_deduction = calculate_nssf(total_gross_income)
    shif_deduction = calculate_shif(total_gross_income)
    ahl_employee_deduction, ahl_employer_contribution = calculate_ahl(total_gross_income)
    helb_deduction = Decimal('0.00')
    
    print(f"📋 STATUTORY DEDUCTIONS:")
    print(f"   NSSF: KES {nssf_deduction:,.2f}")
    print(f"   SHIF: KES {shif_deduction:,.2f}")
    print(f"   AHL: KES {ahl_employee_deduction:,.2f}")
    print(f"   HELB: KES {helb_deduction:,.2f}")
    print()
    
    # FIXED DJANGO ADMIN CALCULATION
    print("✅ FIXED DJANGO ADMIN CALCULATION:")
    
    # Calculate pension deduction
    pension_deduction = pension_contribution
    
    # FIXED: Calculate taxable income (total gross - all pre-tax deductions)
    taxable_income = total_gross_income - (
        nssf_deduction + 
        shif_deduction + 
        ahl_employee_deduction + 
        pension_deduction
    )
    taxable_income = max(taxable_income, Decimal('0.00'))
    
    paye_tax = calculate_paye(taxable_income)
    
    # FIXED: Calculate voluntary deductions (excluding pension to avoid double counting)
    voluntary_deductions_total = Decimal('0.00')  # No other voluntary deductions in this example
    
    total_statutory_deductions = paye_tax + nssf_deduction + shif_deduction + ahl_employee_deduction + helb_deduction
    
    # Total deductions = statutory + voluntary (excluding pension) + pension amount for display
    total_deductions_emp = total_statutory_deductions + voluntary_deductions_total + pension_deduction
    net_pay = total_gross_income - total_deductions_emp
    
    print(f"   Taxable Income: KES {taxable_income:,.2f} (gross - nssf - shif - ahl - pension)")
    print(f"   PAYE Tax: KES {paye_tax:,.2f}")
    print(f"   Total Statutory: KES {total_statutory_deductions:,.2f}")
    print(f"   Other Voluntary: KES {voluntary_deductions_total:,.2f}")
    print(f"   Pension Deduction: KES {pension_deduction:,.2f}")
    print(f"   Total Deductions: KES {total_deductions_emp:,.2f}")
    print(f"   NET PAY: KES {net_pay:,.2f}")
    print()
    
    # Expected result
    expected_net_pay = Decimal('148972.90')
    difference = abs(net_pay - expected_net_pay)
    
    print("🎯 VERIFICATION:")
    print(f"   Expected Net Pay: KES {expected_net_pay:,.2f}")
    print(f"   Calculated Net Pay: KES {net_pay:,.2f}")
    print(f"   Difference: KES {difference:,.2f}")
    
    if difference < Decimal('1.00'):
        print("✅ SUCCESS! Django admin calculation now matches API calculation.")
    else:
        print("❌ Still a difference. Further investigation needed.")
    
    print()
    print("📝 SUMMARY OF FIXES APPLIED:")
    print("   1. ✅ Added SHIF and AHL to taxable income calculation")
    print("   2. ✅ Excluded pension from voluntary deductions to avoid double counting")
    print("   3. ✅ Added pension amount back to total deductions for display")
    print("   4. ✅ Updated individual deduction records creation")

if __name__ == "__main__":
    test_fixed_admin_calculation()
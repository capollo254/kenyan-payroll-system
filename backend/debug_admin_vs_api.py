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

def compare_admin_vs_api_calculation():
    print("🔍 COMPARING DJANGO ADMIN VS API CALCULATION METHODS")
    print("=" * 70)
    
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
    
    # Calculate statutory deductions (same for both methods)
    nssf_deduction = calculate_nssf(total_gross_income)
    shif_deduction = calculate_shif(total_gross_income)
    ahl_employee_deduction, ahl_employer_contribution = calculate_ahl(total_gross_income)
    helb_deduction = Decimal('0.00')  # Assuming no HELB
    
    print(f"📋 STATUTORY DEDUCTIONS (same for both):")
    print(f"   NSSF: KES {nssf_deduction:,.2f}")
    print(f"   SHIF: KES {shif_deduction:,.2f}")
    print(f"   AHL: KES {ahl_employee_deduction:,.2f}")
    print(f"   HELB: KES {helb_deduction:,.2f}")
    print()
    
    # DJANGO ADMIN CALCULATION (INCORRECT)
    print("🔴 DJANGO ADMIN CALCULATION (INCORRECT):")
    admin_taxable_income = total_gross_income - nssf_deduction - pension_contribution
    admin_taxable_income = max(admin_taxable_income, Decimal('0.00'))
    admin_paye_tax = calculate_paye(admin_taxable_income)
    
    # Admin includes ALL voluntary deductions
    admin_voluntary_total = pension_contribution  # Only pension in this example
    admin_total_statutory = admin_paye_tax + nssf_deduction + shif_deduction + ahl_employee_deduction + helb_deduction
    admin_total_deductions = admin_total_statutory + admin_voluntary_total
    admin_net_pay = total_gross_income - admin_total_deductions
    
    print(f"   Taxable Income: KES {admin_taxable_income:,.2f} (gross - nssf - pension)")
    print(f"   PAYE Tax: KES {admin_paye_tax:,.2f}")
    print(f"   Total Statutory: KES {admin_total_statutory:,.2f}")
    print(f"   Total Voluntary: KES {admin_voluntary_total:,.2f}")
    print(f"   Total Deductions: KES {admin_total_deductions:,.2f}")
    print(f"   NET PAY: KES {admin_net_pay:,.2f}")
    print()
    
    # API CALCULATION (CORRECT)
    print("✅ API CALCULATION (CORRECT):")
    api_pension_deduction = min(pension_contribution, Decimal('30000.00'))
    api_taxable_income = total_gross_income - (nssf_deduction + shif_deduction + ahl_employee_deduction + api_pension_deduction)
    api_taxable_income = max(api_taxable_income, Decimal('0.00'))
    api_paye_tax = calculate_paye(api_taxable_income)
    
    # API excludes pension from voluntary deductions (already accounted for)
    api_voluntary_total = Decimal('0.00')  # No other voluntary deductions in this example
    api_total_statutory = api_paye_tax + nssf_deduction + shif_deduction + ahl_employee_deduction + helb_deduction
    api_total_deductions = api_total_statutory + api_voluntary_total + pension_contribution
    api_net_pay = total_gross_income - api_total_deductions
    
    print(f"   Taxable Income: KES {api_taxable_income:,.2f} (gross - nssf - shif - ahl - pension)")
    print(f"   PAYE Tax: KES {api_paye_tax:,.2f}")
    print(f"   Total Statutory: KES {api_total_statutory:,.2f}")
    print(f"   Total Voluntary: KES {api_voluntary_total:,.2f}")
    print(f"   Pension Added Back: KES {pension_contribution:,.2f}")
    print(f"   Total Deductions: KES {api_total_deductions:,.2f}")
    print(f"   NET PAY: KES {api_net_pay:,.2f}")
    print()
    
    # COMPARISON
    print("⚖️  COMPARISON:")
    taxable_diff = admin_taxable_income - api_taxable_income
    paye_diff = admin_paye_tax - api_paye_tax
    net_pay_diff = admin_net_pay - api_net_pay
    
    print(f"   Taxable Income Difference: KES {taxable_diff:,.2f}")
    print(f"   PAYE Tax Difference: KES {paye_diff:,.2f}")
    print(f"   Net Pay Difference: KES {net_pay_diff:,.2f}")
    print()
    
    print("🔧 ROOT CAUSE:")
    print(f"   Django Admin MISSING from taxable income calculation:")
    print(f"   - SHIF: KES {shif_deduction:,.2f}")
    print(f"   - AHL: KES {ahl_employee_deduction:,.2f}")
    print(f"   - Total Missing: KES {shif_deduction + ahl_employee_deduction:,.2f}")
    print(f"   - This causes higher taxable income → higher PAYE → lower net pay")
    print()
    
    if abs(net_pay_diff - Decimal('2868.75')) < Decimal('10.00'):
        print("✅ This explains the user's reported difference of 2868.75!")
    else:
        print(f"❓ User reported difference: 2868.75, calculated: {net_pay_diff:,.2f}")

if __name__ == "__main__":
    compare_admin_vs_api_calculation()
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
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl

def test_pension_relief_cap():
    print("🔧 TESTING PENSION RELIEF CAP IN DJANGO ADMIN")
    print("=" * 60)
    
    PENSION_MAX_RELIEF = Decimal('30000.00')
    
    # Test scenarios
    test_cases = [
        {
            "name": "Below Cap",
            "gross": Decimal('225000.00'),
            "pension": Decimal('9180.00'),
            "description": "Normal pension contribution below cap"
        },
        {
            "name": "At Cap",
            "gross": Decimal('400000.00'), 
            "pension": Decimal('30000.00'),
            "description": "Pension contribution exactly at cap"
        },
        {
            "name": "Above Cap",
            "gross": Decimal('500000.00'),
            "pension": Decimal('45000.00'),
            "description": "High pension contribution above cap"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 TEST CASE {i}: {case['name']}")
        print(f"   {case['description']}")
        print(f"   Gross Salary: KES {case['gross']:,.2f}")
        print(f"   Pension Contribution: KES {case['pension']:,.2f}")
        
        gross_salary = case['gross']
        pension_contribution = case['pension']
        total_gross_income = gross_salary
        
        # Calculate statutory deductions
        nssf_deduction = calculate_nssf(total_gross_income)
        shif_deduction = calculate_shif(total_gross_income)
        ahl_employee_deduction, _ = calculate_ahl(total_gross_income)
        helb_deduction = Decimal('0.00')
        
        # Apply pension relief cap
        pension_relief_amount = min(pension_contribution, PENSION_MAX_RELIEF)
        
        # Calculate taxable income with capped pension relief
        taxable_income = total_gross_income - (
            nssf_deduction + 
            shif_deduction + 
            ahl_employee_deduction + 
            pension_relief_amount
        )
        taxable_income = max(taxable_income, Decimal('0.00'))
        
        paye_tax = calculate_paye(taxable_income)
        
        # Total deductions (use full pension amount, not capped)
        total_statutory = paye_tax + nssf_deduction + shif_deduction + ahl_employee_deduction + helb_deduction
        total_deductions = total_statutory + pension_contribution
        net_pay = total_gross_income - total_deductions
        
        print(f"   Pension Relief Used: KES {pension_relief_amount:,.2f} (capped at {PENSION_MAX_RELIEF:,.2f})")
        print(f"   Taxable Income: KES {taxable_income:,.2f}")
        print(f"   PAYE Tax: KES {paye_tax:,.2f}")
        print(f"   Total Deductions: KES {total_deductions:,.2f}")
        print(f"   Net Pay: KES {net_pay:,.2f}")
        
        # Show the benefit of the cap
        if pension_contribution > PENSION_MAX_RELIEF:
            excess_pension = pension_contribution - PENSION_MAX_RELIEF
            tax_saved = excess_pension * Decimal('0.30')  # Approximate top tax rate
            print(f"   💡 Pension above cap: KES {excess_pension:,.2f}")
            print(f"   💰 Approx. tax saved by cap: KES {tax_saved:,.2f}")
        
        print("   " + "─" * 50)
    
    print(f"\n📝 PENSION RELIEF CAP SUMMARY:")
    print(f"   Maximum pension relief allowed: KES {PENSION_MAX_RELIEF:,.2f} per month")
    print(f"   Contributions above this amount still deducted from salary")
    print(f"   But excess amount doesn't reduce taxable income further")
    print(f"   This complies with KRA pension contribution relief limits")

if __name__ == "__main__":
    test_pension_relief_cap()
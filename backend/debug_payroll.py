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
from apps.employees.models import Employee
from apps.payroll.models import PayrollRun, Payslip, PayslipDeduction
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl

def debug_payroll_calculation():
    print("🔍 DEBUGGING PAYROLL CALCULATION ISSUES")
    print("=" * 50)
    
    try:
        # Get latest payslip to analyze
        latest_payslip = Payslip.objects.order_by('-payroll_run__run_date').first()
        if not latest_payslip:
            print("❌ No payslips found")
            return
            
        employee = latest_payslip.employee
        print(f"📊 ANALYZING PAYSLIP FOR: {employee.user.get_full_name()}")
        print(f"💰 Employee Gross Salary: KES {employee.gross_salary:,.2f}")
        print(f"📅 Payroll Period: {latest_payslip.payroll_run.period_start_date} to {latest_payslip.payroll_run.period_end_date}")
        print()
        
        # Show current payslip values
        print("🧾 CURRENT PAYSLIP VALUES:")
        print(f"   Gross Salary: KES {latest_payslip.gross_salary:,.2f}")
        print(f"   Overtime Pay: KES {latest_payslip.overtime_pay:,.2f}")
        print(f"   Total Gross Income: KES {latest_payslip.total_gross_income:,.2f}")
        print(f"   PAYE Tax: KES {latest_payslip.paye_tax:,.2f}")
        print(f"   NSSF: KES {latest_payslip.nssf_deduction:,.2f}")
        print(f"   SHIF: KES {latest_payslip.shif_deduction:,.2f}")
        print(f"   AHL: KES {latest_payslip.ahl_deduction:,.2f}")
        print(f"   HELB: KES {latest_payslip.helb_deduction:,.2f}")
        print(f"   Total Deductions: KES {latest_payslip.total_deductions:,.2f}")
        print(f"   Net Pay: KES {latest_payslip.net_pay:,.2f}")
        print()
        
        # Show individual deduction items
        print("📝 INDIVIDUAL DEDUCTION ITEMS:")
        deduction_items = latest_payslip.deduction_items.all()
        total_from_items = Decimal('0.00')
        for item in deduction_items:
            print(f"   {item.deduction_type}: KES {item.amount:,.2f} ({'Statutory' if item.is_statutory else 'Voluntary'})")
            total_from_items += item.amount
        print(f"   TOTAL FROM ITEMS: KES {total_from_items:,.2f}")
        print()
        
        # Manual recalculation
        print("🧮 MANUAL RECALCULATION:")
        gross_salary = employee.gross_salary
        overtime_pay = Decimal('0.00')  # Assuming no overtime for debugging
        total_gross_income = gross_salary + overtime_pay
        print(f"   Total Gross Income: KES {total_gross_income:,.2f}")
        
        # Calculate statutory deductions
        nssf_deduction = calculate_nssf(total_gross_income)
        shif_deduction = calculate_shif(total_gross_income)
        ahl_employee_deduction, ahl_employer_contribution = calculate_ahl(total_gross_income)
        helb_deduction = employee.helb_monthly_deduction if employee.helb_monthly_deduction else Decimal('0.00')
        
        print(f"   NSSF Calculation: KES {nssf_deduction:,.2f}")
        print(f"   SHIF Calculation: KES {shif_deduction:,.2f}")
        print(f"   AHL Calculation: KES {ahl_employee_deduction:,.2f}")
        print(f"   HELB: KES {helb_deduction:,.2f}")
        
        # Check pension contributions
        pension_contributions = employee.voluntary_deductions.filter(
            deduction_type__icontains='pension',
            is_active=True
        ).first()
        
        pension_deduction = Decimal('0.00')
        if pension_contributions:
            pension_deduction = min(pension_contributions.amount, Decimal('30000.00'))
            print(f"   Pension Contribution: KES {pension_deduction:,.2f}")
        
        # Calculate taxable income
        taxable_income = total_gross_income - (
            nssf_deduction + 
            shif_deduction + 
            ahl_employee_deduction + 
            pension_deduction
        )
        taxable_income = max(taxable_income, Decimal('0.00'))
        print(f"   Taxable Income: KES {taxable_income:,.2f}")
        
        # Calculate PAYE
        paye_tax = calculate_paye(taxable_income)
        print(f"   PAYE Calculation: KES {paye_tax:,.2f}")
        
        # Other voluntary deductions
        other_voluntary_total = Decimal('0.00')
        other_voluntary_deductions = employee.voluntary_deductions.filter(is_active=True).exclude(deduction_type__icontains='pension')
        for deduction in other_voluntary_deductions:
            other_voluntary_total += deduction.amount
            print(f"   Other Voluntary ({deduction.deduction_type}): KES {deduction.amount:,.2f}")
        
        # Calculate totals
        total_statutory = paye_tax + nssf_deduction + shif_deduction + ahl_employee_deduction + helb_deduction
        total_deductions_calc = total_statutory + other_voluntary_total + pension_deduction
        net_pay_calc = total_gross_income - total_deductions_calc
        
        print()
        print("📋 CALCULATION SUMMARY:")
        print(f"   Total Statutory Deductions: KES {total_statutory:,.2f}")
        print(f"   Total Voluntary Deductions: KES {other_voluntary_total + pension_deduction:,.2f}")
        print(f"   CALCULATED Total Deductions: KES {total_deductions_calc:,.2f}")
        print(f"   CALCULATED Net Pay: KES {net_pay_calc:,.2f}")
        print()
        
        # Compare with stored values
        print("⚖️  COMPARISON:")
        deduction_diff = abs(latest_payslip.total_deductions - total_deductions_calc)
        net_pay_diff = abs(latest_payslip.net_pay - net_pay_calc)
        items_diff = abs(latest_payslip.total_deductions - total_from_items)
        
        print(f"   Stored vs Calculated Deductions: KES {deduction_diff:,.2f} difference")
        print(f"   Stored vs Calculated Net Pay: KES {net_pay_diff:,.2f} difference")
        print(f"   Stored vs Items Total: KES {items_diff:,.2f} difference")
        
        if deduction_diff > Decimal('0.01') or net_pay_diff > Decimal('0.01'):
            print("❌ CALCULATION MISMATCH DETECTED!")
            print("   Issues found:")
            if deduction_diff > Decimal('0.01'):
                print(f"   - Deductions don't match (diff: KES {deduction_diff:,.2f})")
            if net_pay_diff > Decimal('0.01'):
                print(f"   - Net pay doesn't match (diff: KES {net_pay_diff:,.2f})")
            if items_diff > Decimal('0.01'):
                print(f"   - Deduction items don't sum to total (diff: KES {items_diff:,.2f})")
        else:
            print("✅ Calculations appear correct")
        
        # Check for specific issues
        print()
        print("🔍 SPECIFIC ISSUE ANALYSIS:")
        
        # Check if PAYE matches
        if abs(latest_payslip.paye_tax - paye_tax) > Decimal('0.01'):
            print(f"   ❌ PAYE mismatch: Stored KES {latest_payslip.paye_tax:,.2f} vs Calculated KES {paye_tax:,.2f}")
        
        # Check if statutory deductions match
        if abs(latest_payslip.nssf_deduction - nssf_deduction) > Decimal('0.01'):
            print(f"   ❌ NSSF mismatch: Stored KES {latest_payslip.nssf_deduction:,.2f} vs Calculated KES {nssf_deduction:,.2f}")
        
        if abs(latest_payslip.shif_deduction - shif_deduction) > Decimal('0.01'):
            print(f"   ❌ SHIF mismatch: Stored KES {latest_payslip.shif_deduction:,.2f} vs Calculated KES {shif_deduction:,.2f}")
            
        if abs(latest_payslip.ahl_deduction - ahl_employee_deduction) > Decimal('0.01'):
            print(f"   ❌ AHL mismatch: Stored KES {latest_payslip.ahl_deduction:,.2f} vs Calculated KES {ahl_employee_deduction:,.2f}")
        
        print("\n✅ Debugging completed!")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_payroll_calculation()
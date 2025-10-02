#!/usr/bin/env python
"""
Test P9 Report Generation
Create demo P9 reports to validate the system
"""
import os
import django
from datetime import date
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.employees.models import Employee
from apps.reports.models import P9Report, P9MonthlyBreakdown
from apps.reports.p9_utils import P9Generator

def test_p9_generation():
    """Test P9 report generation functionality"""
    
    print("🧪 Testing P9 Report Generation System...")
    
    # Check if we have employees
    employees = Employee.objects.all()
    if not employees.exists():
        print("❌ No employees found. Please create employees first.")
        return
    
    print(f"📊 Found {employees.count()} employees")
    
    # Test with first employee
    employee = employees.first()
    test_year = 2024
    
    print(f"\n🔍 Testing P9 generation for {employee.user.get_full_name()}")
    
    # Create a sample P9 report manually
    p9_report, created = P9Report.objects.get_or_create(
        employee=employee,
        tax_year=test_year,
        defaults={
            'total_basic_salary': Decimal('600000.00'),  # KES 50,000 per month
            'total_benefits_non_cash': Decimal('120000.00'),  # KES 10,000 per month
            'total_value_of_quarters': Decimal('0.00'),
            'retirement_actual': Decimal('72000.00'),  # KES 6,000 per month
            'total_prmf': Decimal('0.00'),
            'total_owner_occupied_interest': Decimal('0.00'),
            'status': 'draft'
        }
    )
    
    if created:
        print("✅ Created new P9 report")
    else:
        print("ℹ️  Using existing P9 report")
    
    # Calculate all totals
    print("\n🧮 Calculating P9 totals...")
    p9_report.calculate_totals()
    p9_report.save()
    
    # Display results
    print(f"\n📋 P9 REPORT SUMMARY for {p9_report.employee_name} ({test_year}):")
    print(f"   Employee PIN: {p9_report.employee_pin}")
    print(f"   Employer: {p9_report.employer_name}")
    print(f"   Employer PIN: {p9_report.employer_pin}")
    
    print(f"\n💰 INCOME:")
    print(f"   Basic Salary (A): KES {p9_report.total_basic_salary:,.2f}")
    print(f"   Benefits Non-Cash (B): KES {p9_report.total_benefits_non_cash:,.2f}")
    print(f"   Value of Quarters (C): KES {p9_report.total_value_of_quarters:,.2f}")
    print(f"   Total Gross Pay (D): KES {p9_report.total_gross_pay:,.2f}")
    
    print(f"\n🏦 RETIREMENT CONTRIBUTIONS (E):")
    print(f"   30% of Basic (E1): KES {p9_report.retirement_30_percent:,.2f}")
    print(f"   Actual Contribution (E2): KES {p9_report.retirement_actual:,.2f}")
    print(f"   Fixed Cap (E3): KES {p9_report.retirement_fixed_cap:,.2f}")
    print(f"   Effective Deduction: KES {p9_report.effective_retirement_deduction:,.2f}")
    
    print(f"\n📊 STATUTORY DEDUCTIONS:")
    print(f"   AHL 1.5% (F): KES {p9_report.total_ahl:,.2f}")
    print(f"   SHIF (G): KES {p9_report.total_shif:,.2f}")
    print(f"   PRMF (H): KES {p9_report.total_prmf:,.2f}")
    print(f"   Owner Occupied (I): KES {p9_report.total_owner_occupied_interest:,.2f}")
    
    print(f"\n💸 TAX CALCULATIONS:")
    print(f"   Total Deductions (J): KES {p9_report.total_deductions:,.2f}")
    print(f"   Chargeable Pay (K): KES {p9_report.chargeable_pay:,.2f}")
    print(f"   Tax Charged (L): KES {p9_report.tax_charged:,.2f}")
    print(f"   Personal Relief (M): KES {p9_report.total_personal_relief:,.2f}")
    print(f"   Insurance Relief (N): KES {p9_report.total_insurance_relief:,.2f}")
    print(f"   PAYE Tax (O): KES {p9_report.total_paye_tax:,.2f}")
    
    print(f"\n📈 REPORT STATUS:")
    print(f"   Status: {p9_report.get_status_display()}")
    print(f"   Complete: {'✅ Yes' if p9_report.is_complete else '❌ No'}")
    print(f"   Generated: {p9_report.generated_date}")
    
    # Create sample monthly breakdown
    print(f"\n📅 Creating sample monthly breakdown...")
    create_sample_monthly_breakdown(p9_report)
    
    # Show monthly breakdown
    monthly_data = p9_report.monthly_breakdown.all().order_by('month')
    if monthly_data.exists():
        print(f"\n📊 MONTHLY BREAKDOWN:")
        print(f"{'Month':<12} {'Basic':<12} {'Gross':<12} {'AHL':<10} {'SHIF':<10} {'PAYE':<10}")
        print("-" * 70)
        
        for month_data in monthly_data:
            month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_name = month_names[month_data.month]
            
            print(f"{month_name:<12} {month_data.basic_salary:<12,.0f} {month_data.gross_pay:<12,.0f} "
                  f"{month_data.ahl:<10,.0f} {month_data.shif:<10,.0f} {month_data.paye_tax:<10,.0f}")
    
    print(f"\n🎉 P9 Report System Test Completed!")
    print(f"📍 View in Django Admin: http://127.0.0.1:8000/admin/reports/p9report/")
    
    return p9_report

def create_sample_monthly_breakdown(p9_report):
    """Create sample monthly breakdown data"""
    
    # Clear existing data
    p9_report.monthly_breakdown.all().delete()
    
    # Sample monthly data (12 months)
    monthly_basic = p9_report.total_basic_salary / 12
    monthly_benefits = p9_report.total_benefits_non_cash / 12
    monthly_gross = (p9_report.total_basic_salary + p9_report.total_benefits_non_cash) / 12
    monthly_ahl = monthly_gross * Decimal('0.015')
    monthly_shif = Decimal('750.00')  # Sample SHIF amount
    monthly_retirement = p9_report.retirement_actual / 12
    monthly_personal_relief = Decimal('2400.00')
    
    for month in range(1, 13):
        # Calculate monthly tax
        monthly_deductions = monthly_retirement + monthly_ahl + monthly_shif
        monthly_chargeable = monthly_gross - monthly_deductions
        monthly_tax_charged = calculate_monthly_tax(monthly_chargeable)
        monthly_paye = max(Decimal('0.00'), monthly_tax_charged - monthly_personal_relief)
        
        P9MonthlyBreakdown.objects.create(
            p9_report=p9_report,
            month=month,
            basic_salary=monthly_basic,
            benefits_non_cash=monthly_benefits,
            gross_pay=monthly_gross,
            retirement_contribution=monthly_retirement,
            ahl=monthly_ahl,
            shif=monthly_shif,
            total_deductions=monthly_deductions,
            chargeable_pay=monthly_chargeable,
            tax_charged=monthly_tax_charged,
            personal_relief=monthly_personal_relief,
            paye_tax=monthly_paye
        )

def calculate_monthly_tax(monthly_chargeable_pay):
    """Calculate monthly PAYE tax using Kenya tax brackets"""
    if monthly_chargeable_pay <= 0:
        return Decimal('0.00')
    
    # 2024 Kenya Tax Brackets (monthly)
    monthly_brackets = [
        (24000, Decimal('0.10')),     # Up to KES 24,000 at 10%
        (8333, Decimal('0.25')),      # Next KES 8,333 at 25%
        (float('inf'), Decimal('0.30'))  # Above at 30%
    ]
    
    tax = Decimal('0.00')
    remaining = monthly_chargeable_pay
    
    for bracket_limit, rate in monthly_brackets:
        if remaining <= 0:
            break
        
        taxable_in_bracket = min(remaining, Decimal(str(bracket_limit)))
        tax += taxable_in_bracket * rate
        remaining -= taxable_in_bracket
    
    return tax

if __name__ == "__main__":
    test_p9_generation()
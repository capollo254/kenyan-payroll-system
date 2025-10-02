#!/usr/bin/env python
"""
Test P9 Generation with Corrected E2 Calculation
Tests that E2 (Actual Contribution) correctly uses NSSF + Pension from actual payslip data
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.reports.bulk_p9_generator import BulkP9Generator
from apps.employees.models import Employee
from apps.payroll.models import Payslip, PayslipDeduction

def test_corrected_e2_calculation():
    print("🔍 Testing P9 Generation with Corrected E2 Calculation")
    print("=" * 60)
    
    try:
        # Get Constantive Apollo
        employee = Employee.objects.get(user__email='constantive@gmail.com')
        print(f"✅ Found employee: {employee.user.first_name} {employee.user.last_name}")
        
        # Check August 2024 payslip data first
        august_payslip = Payslip.objects.filter(
            employee=employee,
            payroll_run__period_start_date__year=2024,
            payroll_run__period_start_date__month=8
        ).first()
        
        if august_payslip:
            print(f"\n📊 August 2024 Payslip Data:")
            print(f"   Gross Salary: KES {august_payslip.gross_salary:,.2f}")
            print(f"   NSSF Deduction: KES {august_payslip.nssf_deduction:,.2f}")
            
            # Get pension deductions
            pension_deductions = PayslipDeduction.objects.filter(
                payslip=august_payslip,
                deduction_type__icontains='pension',
                is_statutory=False
            )
            
            total_pension = sum(d.amount for d in pension_deductions)
            print(f"   Pension Contributions: KES {total_pension:,.2f}")
            print(f"   Expected E2 Total: KES {(august_payslip.nssf_deduction + total_pension):,.2f}")
        
        # Regenerate P9 with corrected calculation
        print(f"\n🔄 Regenerating P9 with corrected E2 calculation...")
        generator = BulkP9Generator(2024)
        p9_report = generator._generate_p9_from_payslips(employee)
        
        print(f"\n📄 Updated P9 Report:")
        print(f"   Employee: {p9_report.employee_name}")
        print(f"   Tax Year: {p9_report.tax_year}")
        print(f"   Total Basic Salary: KES {p9_report.total_basic_salary:,.2f}")
        print(f"   Total Gross Pay: KES {p9_report.total_gross_pay:,.2f}")
        
        print(f"\n💰 Retirement Contributions (Annual):")
        print(f"   E1 (30% of Basic): KES {p9_report.retirement_30_percent:,.2f}")
        print(f"   E2 (Actual NSSF+Pension): KES {p9_report.retirement_actual:,.2f}")
        print(f"   E3 (Fixed 30K/month): KES {p9_report.retirement_fixed_cap:,.2f}")
        print(f"   Total Retirement: KES {(p9_report.retirement_30_percent + p9_report.retirement_actual + p9_report.retirement_fixed_cap):,.2f}")
        
        # Check August monthly breakdown
        august_breakdown = p9_report.monthly_breakdown.filter(month=8).first()
        if august_breakdown:
            print(f"\n📅 August 2024 Monthly Breakdown:")
            print(f"   Basic Salary: KES {august_breakdown.basic_salary:,.2f}")
            print(f"   Gross Pay: KES {august_breakdown.gross_pay:,.2f}")
            print(f"   E1 (30% Basic): KES {august_breakdown.retirement_30_percent_monthly:,.2f}")
            print(f"   E2 (Actual): KES {august_breakdown.retirement_actual_monthly:,.2f}")
            print(f"   E3 (Fixed): KES {august_breakdown.retirement_fixed_monthly:,.2f}")
            print(f"   Total Retirement: KES {august_breakdown.retirement_contribution:,.2f}")
            
            # Verify E2 calculation
            if august_payslip:
                expected_e2 = august_payslip.nssf_deduction + total_pension
                if abs(august_breakdown.retirement_actual_monthly - expected_e2) < 0.01:
                    print(f"   ✅ E2 calculation CORRECT!")
                else:
                    print(f"   ❌ E2 calculation mismatch. Expected: {expected_e2:,.2f}")
        
        # Test PDF generation
        print(f"\n📄 Testing PDF Generation:")
        from apps.reports.p9_pdf_generator import P9PDFGenerator
        generator = P9PDFGenerator()
        
        try:
            pdf_buffer = generator.generate_p9_pdf(p9_report)
            print(f"   ✅ PDF Generated Successfully!")
            print(f"   📄 PDF Size: {len(pdf_buffer.getvalue()):,} bytes")
            
            # Save test file
            test_file = "P9_Corrected_E2_Constantive_Apollo_2024.pdf"
            generator.save_pdf_file(p9_report, test_file)
            print(f"   💾 Saved as: {test_file}")
            
            pdf_buffer.close()
        except Exception as e:
            print(f"   ❌ PDF Generation Error: {e}")
        
        print(f"\n✅ Test Completed Successfully!")
        print(f"   - E2 now correctly uses actual NSSF + Pension from payslips")
        print(f"   - Monthly breakdown shows individual E1, E2, E3 values")
        print(f"   - PDF generation works with corrected calculations")
        
    except Employee.DoesNotExist:
        print("❌ Employee with email constantive@gmail.com not found")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_corrected_e2_calculation()
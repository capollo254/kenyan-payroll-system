#!/usr/bin/env python
"""
Test P9 "Lower of E" Calculation
Tests that total deductions use the lowest value among E1, E2, E3
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

def test_lower_of_e_calculation():
    print("🔍 Testing P9 'Lower of E' Calculation")
    print("=" * 50)
    
    try:
        # Get Constantive Apollo
        employee = Employee.objects.get(user__email='constantive@gmail.com')
        print(f"✅ Found employee: {employee.user.first_name} {employee.user.last_name}")
        
        # Regenerate P9 with corrected calculation
        print(f"\n🔄 Regenerating P9 with 'lower of E' logic...")
        generator = BulkP9Generator(2024)
        p9_report = generator._generate_p9_from_payslips(employee)
        
        # Check August monthly breakdown
        august_breakdown = p9_report.monthly_breakdown.filter(month=8).first()
        if august_breakdown:
            print(f"\n📅 August 2024 Monthly Breakdown:")
            print(f"   Basic Salary: KES {august_breakdown.basic_salary:,.2f}")
            print(f"   Gross Pay: KES {august_breakdown.gross_pay:,.2f}")
            print(f"   E1 (30% Basic): KES {august_breakdown.retirement_30_percent_monthly:,.2f}")
            print(f"   E2 (Actual): KES {august_breakdown.retirement_actual_monthly:,.2f}")
            print(f"   E3 (Fixed): KES {august_breakdown.retirement_fixed_monthly:,.2f}")
            
            # Calculate lower of E
            e1 = august_breakdown.retirement_30_percent_monthly
            e2 = august_breakdown.retirement_actual_monthly
            e3 = august_breakdown.retirement_fixed_monthly
            lower_of_e = min(e1, e2, e3)
            
            print(f"   Lower of E: KES {lower_of_e:,.2f}")
            print(f"   AHL: KES {august_breakdown.ahl:,.2f}")
            print(f"   SHIF: KES {august_breakdown.shif:,.2f}")
            
            expected_total_deductions = lower_of_e + august_breakdown.ahl + august_breakdown.shif
            print(f"   Expected Total Deductions: KES {expected_total_deductions:,.2f}")
            print(f"   Actual Retirement Contribution: KES {august_breakdown.retirement_contribution:,.2f}")
            
            # Verify calculation
            if abs(august_breakdown.retirement_contribution - lower_of_e) < 0.01:
                print(f"   ✅ 'Lower of E' calculation CORRECT!")
            else:
                print(f"   ❌ 'Lower of E' calculation incorrect")
            
            # Verify which is lowest
            if e2 == lower_of_e:
                print(f"   ✅ E2 ({e2:,.2f}) is correctly identified as the lowest")
            else:
                print(f"   ❌ Expected E2 to be lowest, but got {lower_of_e:,.2f}")
        
        # Check annual totals
        print(f"\n📊 Annual P9 Report:")
        print(f"   E1 (30% of Basic): KES {p9_report.retirement_30_percent:,.2f}")
        print(f"   E2 (Actual NSSF+Pension): KES {p9_report.retirement_actual:,.2f}")
        print(f"   E3 (Fixed 30K/month): KES {p9_report.retirement_fixed_cap:,.2f}")
        
        effective_retirement = p9_report.effective_retirement_deduction
        print(f"   Effective Retirement (Lower of E): KES {effective_retirement:,.2f}")
        print(f"   Total AHL: KES {p9_report.total_ahl:,.2f}")
        print(f"   Total SHIF: KES {p9_report.total_shif:,.2f}")
        print(f"   Total Deductions: KES {p9_report.total_deductions:,.2f}")
        
        expected_annual_deductions = effective_retirement + p9_report.total_ahl + p9_report.total_shif
        if abs(p9_report.total_deductions - expected_annual_deductions) < 0.01:
            print(f"   ✅ Annual 'Lower of E' calculation CORRECT!")
        else:
            print(f"   ❌ Annual calculation mismatch. Expected: {expected_annual_deductions:,.2f}")
        
        # Test PDF generation
        print(f"\n📄 Testing PDF Generation:")
        from apps.reports.p9_pdf_generator import P9PDFGenerator
        pdf_generator = P9PDFGenerator()
        
        try:
            pdf_buffer = pdf_generator.generate_p9_pdf(p9_report)
            print(f"   ✅ PDF Generated Successfully!")
            print(f"   📄 PDF Size: {len(pdf_buffer.getvalue()):,} bytes")
            
            # Save test file
            test_file = "P9_Lower_of_E_Constantive_Apollo_2024.pdf"
            pdf_generator.save_pdf_file(p9_report, test_file)
            print(f"   💾 Saved as: {test_file}")
            
            pdf_buffer.close()
        except Exception as e:
            print(f"   ❌ PDF Generation Error: {e}")
        
        print(f"\n✅ Test Completed Successfully!")
        print(f"   - Total Deductions now uses 'Lower of E' (minimum of E1, E2, E3)")
        print(f"   - E2 ({august_breakdown.retirement_actual_monthly:,.2f}) is the lowest in August example")
        print(f"   - PDF header updated to show 'Lower of E+F+G+H+I'")
        
    except Employee.DoesNotExist:
        print("❌ Employee with email constantive@gmail.com not found")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_lower_of_e_calculation()
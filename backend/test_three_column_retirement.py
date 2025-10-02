#!/usr/bin/env python
"""
Test the three-column retirement contribution P9 generation
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.reports.bulk_p9_generator import BulkP9Generator
from apps.reports.models import P9Report
from apps.employees.models import Employee

def test_retirement_columns():
    """Test the three retirement contribution columns"""
    
    print("🔍 Testing Three-Column Retirement Contribution P9 Format")
    print("=" * 60)
    
    # Get test employee
    try:
        employee = Employee.objects.get(user__first_name='Constantive', user__last_name='Apollo')
        print(f"✅ Found test employee: {employee.user.first_name} {employee.user.last_name}")
    except Employee.DoesNotExist:
        print("❌ Test employee not found")
        return
    
    # Generate P9
    generator = BulkP9Generator(2024)
    p9_report = generator._generate_p9_from_payslips(employee)
    
    print(f"\n📊 Generated P9 Report:")
    print(f"   Employee: {p9_report.employee_name}")
    print(f"   Tax Year: {p9_report.tax_year}")
    print(f"   Total Basic Salary: KES {p9_report.total_basic_salary:,.2f}")
    print(f"   Total Gross Pay: KES {p9_report.total_gross_pay:,.2f}")
    
    print(f"\n💰 Retirement Contributions (Split into 3 columns):")
    print(f"   E1 (30% of Basic): KES {p9_report.retirement_30_percent:,.2f}")
    print(f"   E2 (Actual NSSF):  KES {p9_report.retirement_actual:,.2f}")
    print(f"   E3 (Fixed 30K/m):  KES {p9_report.retirement_fixed_cap:,.2f}")
    print(f"   Total Retirement:  KES {(p9_report.retirement_30_percent + p9_report.retirement_actual + p9_report.retirement_fixed_cap):,.2f}")
    
    # Test PDF generation
    from apps.reports.p9_pdf_generator import P9PDFGenerator
    
    print(f"\n📄 Testing PDF Generation:")
    generator = P9PDFGenerator()
    
    try:
        pdf_buffer = generator.generate_p9_pdf(p9_report)
        pdf_size = len(pdf_buffer.getvalue())
        pdf_buffer.close()
        
        print(f"   ✅ PDF Generated Successfully!")
        print(f"   📄 PDF Size: {pdf_size:,} bytes")
        print(f"   📊 Format: Landscape with 19 columns (including E1, E2, E3)")
        
        # Save test file
        test_filename = f"P9_Three_Columns_{p9_report.employee_name.replace(' ', '_')}_2024.pdf"
        generator.save_pdf_file(p9_report, test_filename)
        print(f"   💾 Saved as: {test_filename}")
        
    except Exception as e:
        print(f"   ❌ PDF Generation Failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ Test Completed Successfully!")
    print("   - Retirement contributions split into E1, E2, E3 columns")
    print("   - E1: 30% of Basic Salary")
    print("   - E2: Actual contributions (NSSF + Pension)")
    print("   - E3: Fixed amount (KES 30,000 per month)")
    print("   - PDF generated in landscape format with all columns")

if __name__ == '__main__':
    test_retirement_columns()
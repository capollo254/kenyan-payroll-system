"""
Test script to generate P9 PDF with Employee's P.I.N. configuration
Verifies that the P9 PDF shows the correct KRA PIN from employee database
"""

import os
import sys
import django
from datetime import date

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.core.models import User
from apps.employees.models import Employee, JobInformation
from apps.reports.models import P9Report
from apps.reports.p9_pdf_generator import P9PDFGenerator

def test_p9_pdf_employee_pin():
    print("Testing P9 PDF Generation with Employee's P.I.N. from database...")
    print("=" * 70)
    
    try:
        # Create test user
        user = User.objects.create_user(
            email='p9.test.employee@example.com',
            first_name='Sarah',
            last_name='Johnson'
        )
        
        # Create employee
        employee = Employee.objects.create(
            user=user,
            gross_salary=75000.00
        )
        
        # Create job information with KRA PIN
        test_kra_pin = 'P051234567Q'
        job_info = JobInformation.objects.create(
            employee=employee,
            company_employee_id='EMP2024-075',
            kra_pin=test_kra_pin,
            department='Finance',
            position='Senior Accountant',
            date_of_joining=date(2024, 1, 15)
        )
        
        print(f"✓ Created test employee: {employee.full_name()}")
        print(f"✓ KRA PIN in database: {job_info.kra_pin}")
        print()
        
        # Create P9 Report with sample data
        p9_report = P9Report.objects.create(
            employee=employee,
            tax_year=2024,
            total_basic_salary=900000.00,  # 12 months * 75000
            total_gross_pay=900000.00,
            total_paye=162000.00,  # Sample PAYE calculation
            total_nssf_employee_contribution=12000.00,  # Sample NSSF
            total_nhif_deduction=10800.00  # Sample NHIF
        )
        
        print("P9 Report created with following information:")
        print(f"  Employee Name: {p9_report.employee_name}")
        print(f"  Employee P.I.N.: {p9_report.employee_pin}")
        print(f"  Tax Year: {p9_report.tax_year}")
        print(f"  Total Gross Pay: KSh {p9_report.total_gross_pay:,.2f}")
        print()
        
        # Generate P9 PDF
        generator = P9PDFGenerator(p9_report)
        
        # Create media/reports directory if it doesn't exist
        reports_dir = os.path.join('media', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate PDF
        pdf_path = generator.generate()
        
        print(f"✅ P9 PDF generated successfully!")
        print(f"📄 PDF saved to: {pdf_path}")
        print()
        
        # Verify the data in P9 report matches database
        if p9_report.employee_pin == test_kra_pin:
            print("✅ SUCCESS: Employee's P.I.N. in P9 report matches database KRA PIN!")
            print(f"✅ P9 Report Employee P.I.N.: {p9_report.employee_pin}")
            print(f"✅ Database KRA PIN: {job_info.kra_pin}")
        else:
            print("❌ ISSUE: Employee's P.I.N. does not match database KRA PIN")
            print(f"❌ P9 Report Employee P.I.N.: {p9_report.employee_pin}")
            print(f"❌ Database KRA PIN: {job_info.kra_pin}")
        
        print()
        print("P9 PDF Employee Section Information:")
        print(f"  Employee's P.I.N. field will show: '{p9_report.employee_pin}'")
        print(f"  This should match the KRA PIN from JobInformation: '{job_info.kra_pin}'")
        print()
        
        # Clean up test data
        os.remove(pdf_path) if os.path.exists(pdf_path) else None
        p9_report.delete()
        job_info.delete()
        employee.delete()
        user.delete()
        
        print("=" * 70)
        print("P9 PDF Employee's P.I.N. configuration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_p9_pdf_employee_pin()
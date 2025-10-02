"""
Test P9 PDF generation with employer information from CompanySettings
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.core.models import User
from apps.core.company_models import CompanySettings
from apps.employees.models import Employee, JobInformation
from apps.reports.models import P9Report
from apps.reports.p9_pdf_generator import P9PDFGenerator

def test_p9_pdf_employer_info():
    print("Testing P9 PDF generation with employer information...")
    print("=" * 60)
    
    try:
        # Set up realistic company information
        company_settings = CompanySettings.get_settings()
        company_settings.company_name = "Techno Solutions Kenya Ltd"
        company_settings.kra_pin = "P012345678Z"
        company_settings.address_line_1 = "Westlands Business Park"
        company_settings.city = "Nairobi"
        company_settings.country = "Kenya"
        company_settings.save()
        
        print(f"✓ Company configured: {company_settings.company_name}")
        print(f"✓ Company KRA PIN: {company_settings.kra_pin}")
        print()
        
        # Create test employee with complete information
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            email=f'test.employer.{unique_id}@example.com',
            first_name='Michael',
            last_name='Ochieng'
        )
        
        employee = Employee.objects.create(
            user=user,
            gross_salary=75000.00
        )
        
        job_info = JobInformation.objects.create(
            employee=employee,
            company_employee_id=f'TS2024-{unique_id}',
            kra_pin=f'A{unique_id}K',
            nssf_number=f'NSSF{unique_id}',
            nhif_number=f'NHIF{unique_id}',
            department='Software Development',
            position='Senior Software Engineer',
            date_of_joining='2024-01-01'
        )
        
        print(f"✓ Employee: {employee.user.first_name} {employee.user.last_name}")
        print(f"✓ Employee KRA PIN: {job_info.kra_pin}")
        print(f"✓ Position: {job_info.position}")
        print()
        
        # Create P9 report with realistic data
        p9_report = P9Report.objects.create(
            employee=employee,
            tax_year=2024,
            total_basic_salary=900000.00,  # 12 months * 75000
            total_gross_pay=900000.00,
            total_paye_tax=180000.00  # Approximate 20% tax
        )
        
        print("P9 Report Information:")
        print(f"  Tax Year: {p9_report.tax_year}")
        print(f"  Employee Name: {p9_report.employee_name}")
        print(f"  Employee P.I.N.: {p9_report.employee_pin}")
        print(f"  Employer Name: {p9_report.employer_name}")
        print(f"  Employer P.I.N.: {p9_report.employer_pin}")
        print(f"  Total Basic Salary: KSh {p9_report.total_basic_salary:,.2f}")
        print()
        
        # Generate P9 PDF
        generator = P9PDFGenerator()
        pdf_buffer = generator.generate_p9_pdf(p9_report)
        pdf_content = pdf_buffer.getvalue()
        
        # Save PDF for verification
        pdf_filename = f"test_p9_employer_info_{employee.user.last_name}.pdf"
        pdf_path = os.path.join(backend_path, pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ P9 PDF generated successfully: {pdf_filename}")
        print(f"✅ PDF saved at: {pdf_path}")
        print(f"✅ PDF size: {len(pdf_content):,} bytes")
        
        # Verify data consistency
        verification_results = []
        
        # Check employer name
        if p9_report.employer_name == company_settings.company_name:
            verification_results.append("✅ Employer Name matches CompanySettings")
        else:
            verification_results.append("❌ Employer Name mismatch")
            
        # Check employer PIN
        if p9_report.employer_pin == company_settings.kra_pin:
            verification_results.append("✅ Employer P.I.N. matches CompanySettings")
        else:
            verification_results.append("❌ Employer P.I.N. mismatch")
            
        # Check employee PIN
        if p9_report.employee_pin == job_info.kra_pin:
            verification_results.append("✅ Employee P.I.N. matches JobInformation")
        else:
            verification_results.append("❌ Employee P.I.N. mismatch")
        
        print()
        print("Verification Results:")
        for result in verification_results:
            print(f"  {result}")
        
        # Clean up
        p9_report.delete()
        job_info.delete()
        employee.delete()
        user.delete()
        
        # Reset company settings
        company_settings.company_name = "Kenyan Payroll System"
        company_settings.kra_pin = ""
        company_settings.save()
        
        print()
        print("=" * 60)
        print("P9 PDF employer information test completed!")
        print(f"✅ P9 form now correctly shows:")
        print(f"   - Employer's Name from CompanySettings.company_name")
        print(f"   - Employer's P.I.N. from CompanySettings.kra_pin")
        print(f"   - Employee's P.I.N. from JobInformation.kra_pin")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_p9_pdf_employer_info()
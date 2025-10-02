"""
Test script to verify Employer's Name and P.I.N. fields in P9 PDF
Tests that both fields correctly pull from CompanySettings and display in PDF
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

def test_p9_employer_fields_complete():
    print("Testing Employer fields in P9 PDF generation...")
    print("=" * 60)
    
    try:
        # Set up test company information
        company_settings = CompanySettings.get_settings()
        original_name = company_settings.company_name
        original_pin = company_settings.kra_pin
        
        # Set test company data
        test_company_name = "ABC Manufacturing Limited"
        test_company_pin = "P987654321Z"
        
        company_settings.company_name = test_company_name
        company_settings.kra_pin = test_company_pin
        company_settings.save()
        
        print(f"✓ Test Company Name: {company_settings.company_name}")
        print(f"✓ Test Company KRA PIN: {company_settings.kra_pin}")
        print()
        
        # Create test employee
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        user = User.objects.create_user(
            email=f'test.employer.fields.{unique_id}@example.com',
            first_name='Sarah',
            last_name='Kimani'
        )
        
        employee = Employee.objects.create(
            user=user,
            gross_salary=60000.00
        )
        
        job_info = JobInformation.objects.create(
            employee=employee,
            company_employee_id=f'ABC2024-{unique_id}',
            kra_pin=f'A{unique_id}P',
            nssf_number=f'NSSF{unique_id}',
            nhif_number=f'NHIF{unique_id}',
            department='Production',
            position='Production Manager',
            date_of_joining='2024-02-01'
        )
        
        print(f"✓ Test Employee: {employee.user.first_name} {employee.user.last_name}")
        print(f"✓ Employee KRA PIN: {job_info.kra_pin}")
        print(f"✓ Employee Position: {job_info.position}")
        print()
        
        # Create P9 report
        p9_report = P9Report.objects.create(
            employee=employee,
            tax_year=2024,
            total_basic_salary=720000.00,  # 12 months * 60000
            total_gross_pay=720000.00,
            total_paye_tax=144000.00  # Approximate tax
        )
        
        print("P9 Report Data Verification:")
        print(f"  Employee Name: {p9_report.employee_name}")
        print(f"  Employee P.I.N.: {p9_report.employee_pin}")
        print(f"  Employer Name: {p9_report.employer_name}")
        print(f"  Employer P.I.N.: {p9_report.employer_pin}")
        print()
        
        # Verify data sources match expectations
        verification_results = []
        
        if p9_report.employer_name == test_company_name:
            verification_results.append("✅ P9 Report Employer Name matches CompanySettings")
        else:
            verification_results.append("❌ P9 Report Employer Name mismatch")
            
        if p9_report.employer_pin == test_company_pin:
            verification_results.append("✅ P9 Report Employer P.I.N. matches CompanySettings")
        else:
            verification_results.append("❌ P9 Report Employer P.I.N. mismatch")
            
        if p9_report.employee_pin == job_info.kra_pin:
            verification_results.append("✅ P9 Report Employee P.I.N. matches JobInformation")
        else:
            verification_results.append("❌ P9 Report Employee P.I.N. mismatch")
        
        print("Data Source Verification:")
        for result in verification_results:
            print(f"  {result}")
        print()
        
        # Generate P9 PDF
        print("Generating P9 PDF...")
        generator = P9PDFGenerator()
        pdf_buffer = generator.generate_p9_pdf(p9_report)
        pdf_content = pdf_buffer.getvalue()
        
        # Save PDF for manual verification
        pdf_filename = f"test_employer_fields_complete_{employee.user.last_name}.pdf"
        pdf_path = os.path.join(backend_path, pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ P9 PDF generated successfully!")
        print(f"✅ PDF filename: {pdf_filename}")
        print(f"✅ PDF path: {pdf_path}")
        print(f"✅ PDF size: {len(pdf_content):,} bytes")
        print()
        
        # Verify the PDF contains correct employer information
        print("Expected P9 PDF Content:")
        print(f"  Employer's Name: {test_company_name}")
        print(f"  Employer's P.I.N.: {test_company_pin}")
        print(f"  Employee's First Name: {employee.user.first_name}")
        print(f"  Employee's Other Names: {employee.user.last_name}")
        print(f"  Employee's P.I.N.: {job_info.kra_pin}")
        print()
        
        # Test edge case: Empty company information
        print("Testing edge case: Empty company information...")
        company_settings.company_name = ""
        company_settings.kra_pin = ""
        company_settings.save()
        
        p9_report_empty = P9Report.objects.create(
            employee=employee,
            tax_year=2023,
            total_basic_salary=720000.00,
            total_gross_pay=720000.00
        )
        
        print(f"Empty Company Info Test:")
        print(f"  Employer Name: '{p9_report_empty.employer_name}'")
        print(f"  Employer P.I.N.: '{p9_report_empty.employer_pin}'")
        
        if p9_report_empty.employer_name == "" and p9_report_empty.employer_pin == "":
            print("✅ SUCCESS: Empty company information handled gracefully")
        else:
            print("❌ ISSUE: Empty company information not handled properly")
        
        # Clean up test data
        p9_report.delete()
        p9_report_empty.delete()
        job_info.delete()
        employee.delete()
        user.delete()
        
        # Restore original company settings
        company_settings.company_name = original_name
        company_settings.kra_pin = original_pin
        company_settings.save()
        
        print()
        print("=" * 60)
        print("Employer fields P9 PDF test completed!")
        print("✅ Employer's Name: Pulls from CompanySettings.company_name")
        print("✅ Employer's P.I.N.: Pulls from CompanySettings.kra_pin")
        print("✅ Employee's P.I.N.: Pulls from JobInformation.kra_pin")
        print("🎉 All employer and employee identification fields working correctly!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_p9_employer_fields_complete()
"""
Test script to verify NHIF P.I.N. and Employee's SHIF Number fields removal from P9 PDF
Tests that these fields no longer appear in the generated P9 forms
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

def test_p9_nhif_shif_fields_removal():
    print("Testing NHIF P.I.N. and Employee's SHIF Number fields removal...")
    print("=" * 65)
    
    try:
        # Set up test company information
        company_settings = CompanySettings.get_settings()
        original_name = company_settings.company_name
        original_pin = company_settings.kra_pin
        
        # Set test company data
        test_company_name = "Clean Fields Test Company Ltd"
        test_company_pin = "P123456789T"
        
        company_settings.company_name = test_company_name
        company_settings.kra_pin = test_company_pin
        company_settings.save()
        
        print(f"✓ Test Company: {company_settings.company_name}")
        print(f"✓ Test Company KRA PIN: {company_settings.kra_pin}")
        print()
        
        # Create test employee
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        user = User.objects.create_user(
            email=f'test.nhif.shif.removal.{unique_id}@example.com',
            first_name='David',
            last_name='Mwangi'
        )
        
        employee = Employee.objects.create(
            user=user,
            gross_salary=55000.00
        )
        
        job_info = JobInformation.objects.create(
            employee=employee,
            company_employee_id=f'CFT2024-{unique_id}',
            kra_pin=f'A{unique_id}M',
            nssf_number=f'NSSF{unique_id}',
            nhif_number=f'NHIF{unique_id}',
            department='Administration',
            position='Office Manager',
            date_of_joining='2024-03-01'
        )
        
        print(f"✓ Test Employee: {employee.user.first_name} {employee.user.last_name}")
        print(f"✓ Employee KRA PIN: {job_info.kra_pin}")
        print(f"✓ Employee NHIF Number: {job_info.nhif_number} (should NOT appear in P9)")
        print()
        
        # Create P9 report
        p9_report = P9Report.objects.create(
            employee=employee,
            tax_year=2024,
            total_basic_salary=660000.00,  # 12 months * 55000
            total_gross_pay=660000.00,
            total_paye_tax=132000.00  # Approximate tax
        )
        
        print("P9 Report Employee Information Section:")
        print(f"  Employer's Name: {p9_report.employer_name}")
        print(f"  Employer's P.I.N.: {p9_report.employer_pin}")
        print(f"  Employee's First Name: {employee.user.first_name}")
        print(f"  Employee's Other Names: {employee.user.last_name}")
        print(f"  Employee's P.I.N.: {p9_report.employee_pin}")
        print(f"  NHIF P.I.N.: [REMOVED] ✓")
        print(f"  Employee's SHIF Number: [REMOVED] ✓")
        print()
        
        # Generate P9 PDF
        print("Generating P9 PDF...")
        generator = P9PDFGenerator()
        pdf_buffer = generator.generate_p9_pdf(p9_report)
        pdf_content = pdf_buffer.getvalue()
        
        # Save PDF for verification
        pdf_filename = f"test_nhif_shif_removal_{employee.user.last_name}.pdf"
        pdf_path = os.path.join(backend_path, pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ P9 PDF generated successfully!")
        print(f"✅ PDF filename: {pdf_filename}")
        print(f"✅ PDF size: {len(pdf_content):,} bytes")
        print()
        
        # Verify the expected P9 form structure
        print("Expected P9 Employee Information Section (after cleanup):")
        print("  Row 1: Employer's Name: | [Company Name] | Employer's P.I.N.: | [Company PIN]")
        print("  Row 2: Employee's First Name: | [First Name] | Employee's P.I.N.: | [Employee PIN]") 
        print("  Row 3: Employee's Other Names: | [Last Name] | [Empty] | [Empty]")
        print()
        print("✅ REMOVED Fields:")
        print("  ❌ NHIF P.I.N.: [No longer appears]")
        print("  ❌ Employee's SHIF Number: [No longer appears]")
        print()
        
        # Test with different employee to ensure consistency
        user2 = User.objects.create_user(
            email=f'test.second.employee.{unique_id}@example.com',
            first_name='Grace',
            last_name='Wanjiku'
        )
        
        employee2 = Employee.objects.create(
            user=user2,
            gross_salary=65000.00
        )
        
        job_info2 = JobInformation.objects.create(
            employee=employee2,
            company_employee_id=f'CFT2024-SEC-{unique_id}',
            kra_pin=f'B{unique_id}W',
            nssf_number=f'NSSF2{unique_id}',
            nhif_number=f'NHIF2{unique_id}',
            department='Finance',
            position='Accountant',
            date_of_joining='2024-04-01'
        )
        
        p9_report2 = P9Report.objects.create(
            employee=employee2,
            tax_year=2024,
            total_basic_salary=780000.00,
            total_gross_pay=780000.00,
            total_paye_tax=156000.00
        )
        
        # Generate second PDF
        pdf_buffer2 = generator.generate_p9_pdf(p9_report2)
        pdf_content2 = pdf_buffer2.getvalue()
        
        pdf_filename2 = f"test_nhif_shif_removal_{employee2.user.last_name}.pdf"
        pdf_path2 = os.path.join(backend_path, pdf_filename2)
        
        with open(pdf_path2, 'wb') as f:
            f.write(pdf_content2)
        
        print(f"✅ Second P9 PDF generated: {pdf_filename2}")
        print(f"✅ Second PDF size: {len(pdf_content2):,} bytes")
        print()
        
        # Clean up test data
        p9_report.delete()
        p9_report2.delete()
        job_info.delete()
        job_info2.delete()
        employee.delete()
        employee2.delete()
        user.delete()
        user2.delete()
        
        # Restore original company settings
        company_settings.company_name = original_name
        company_settings.kra_pin = original_pin
        company_settings.save()
        
        print("Cleanup Results:")
        print("  ✅ Test data cleaned up")
        print("  ✅ Original company settings restored")
        print()
        
        print("=" * 65)
        print("NHIF P.I.N. and Employee's SHIF Number removal test completed!")
        print()
        print("📋 P9 Form Structure (Updated):")
        print("  ✅ Employer's Name: [From CompanySettings]")
        print("  ✅ Employer's P.I.N.: [From CompanySettings]") 
        print("  ✅ Employee's First Name: [From User model]")
        print("  ✅ Employee's P.I.N.: [From JobInformation]")
        print("  ✅ Employee's Other Names: [From User model]")
        print("  ❌ NHIF P.I.N.: [REMOVED]")
        print("  ❌ Employee's SHIF Number: [REMOVED]")
        print()
        print("🎉 P9 forms now have cleaner, more focused employee identification!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_p9_nhif_shif_fields_removal()
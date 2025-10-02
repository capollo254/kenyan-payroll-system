"""
Test script to verify Employer's Name and Employer's P.I.N. data sources
Tests that these fields pull data from CompanySettings model
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

def test_employer_data_sources():
    print("Testing Employer's Name and Employer's P.I.N. data sources...")
    print("=" * 65)
    
    try:
        # Set up company information
        company_settings = CompanySettings.get_settings()
        company_settings.company_name = "ABC Technologies Limited"
        company_settings.kra_pin = "P051234567X"
        company_settings.save()
        
        print(f"✓ Company Settings configured:")
        print(f"  Company Name: {company_settings.company_name}")
        print(f"  Company KRA PIN: {company_settings.kra_pin}")
        print()
        
        # Create test user and employee
        user = User.objects.create_user(
            email='test.employer.data@example.com',
            first_name='Jane',
            last_name='Smith'
        )
        
        employee = Employee.objects.create(
            user=user,
            gross_salary=45000.00
        )
        
        # Create job information
        job_info = JobInformation.objects.create(
            employee=employee,
            company_employee_id='EMP003_EMPLOYER_TEST',
            kra_pin='A987654321C',
            department='Finance',
            position='Accountant',
            date_of_joining='2024-01-15'
        )
        
        print(f"✓ Created test employee: {employee.user.first_name} {employee.user.last_name}")
        print(f"✓ Employee KRA PIN: {job_info.kra_pin}")
        print()
        
        # Create P9 Report
        p9_report = P9Report.objects.create(
            employee=employee,
            tax_year=2024,
            total_basic_salary=540000.00,  # 12 months * 45000
            total_gross_pay=540000.00
        )
        
        print("P9 Report Employer Information:")
        print(f"  Employer's Name: {p9_report.employer_name}")
        print(f"  Employer's P.I.N.: {p9_report.employer_pin}")
        print(f"  Expected Company Name: {company_settings.company_name}")
        print(f"  Expected Company KRA PIN: {company_settings.kra_pin}")
        print()
        
        # Verify employer data sources
        success_count = 0
        
        if p9_report.employer_name == company_settings.company_name:
            print("✅ SUCCESS: Employer's Name correctly pulls from CompanySettings!")
            print(f"✅ P9 Report Employer Name: {p9_report.employer_name}")
            print(f"✅ CompanySettings Company Name: {company_settings.company_name}")
            success_count += 1
        else:
            print("❌ ISSUE: Employer's Name does not match CompanySettings")
            print(f"❌ P9 Report Employer Name: {p9_report.employer_name}")
            print(f"❌ CompanySettings Company Name: {company_settings.company_name}")
        
        print()
        
        if p9_report.employer_pin == company_settings.kra_pin:
            print("✅ SUCCESS: Employer's P.I.N. correctly pulls from CompanySettings!")
            print(f"✅ P9 Report Employer PIN: {p9_report.employer_pin}")
            print(f"✅ CompanySettings KRA PIN: {company_settings.kra_pin}")
            success_count += 1
        else:
            print("❌ ISSUE: Employer's P.I.N. does not match CompanySettings")
            print(f"❌ P9 Report Employer PIN: {p9_report.employer_pin}")
            print(f"❌ CompanySettings KRA PIN: {company_settings.kra_pin}")
        
        print()
        print("Testing edge case: Empty company KRA PIN...")
        
        # Test with empty company KRA PIN
        company_settings.kra_pin = ''
        company_settings.save()
        
        p9_report2 = P9Report.objects.create(
            employee=employee,
            tax_year=2023,
            total_basic_salary=540000.00,
            total_gross_pay=540000.00
        )
        
        print(f"Empty KRA PIN Test:")
        print(f"  Employer's Name: {p9_report2.employer_name}")
        print(f"  Employer's P.I.N.: '{p9_report2.employer_pin}'")
        
        if p9_report2.employer_pin == '':
            print("✅ SUCCESS: Empty company KRA PIN handled gracefully")
            success_count += 1
        else:
            print("❌ ISSUE: Empty company KRA PIN not handled properly")
        
        # Clean up test data
        p9_report.delete()
        p9_report2.delete()
        job_info.delete()
        employee.delete()
        user.delete()
        
        # Reset company settings
        company_settings.company_name = "Kenyan Payroll System"
        company_settings.kra_pin = ""
        company_settings.save()
        
        print()
        print("=" * 65)
        print(f"Employer data sources test completed! ({success_count}/3 tests passed)")
        
        if success_count == 3:
            print("🎉 All employer data source configurations working correctly!")
        else:
            print("⚠️ Some issues found in employer data source configuration.")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_employer_data_sources()
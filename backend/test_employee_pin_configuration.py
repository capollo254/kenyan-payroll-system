"""
Test script to verify Employee's P.I.N. field configuration
Tests that Employee's P.I.N. pulls actual KRA PIN from employee database
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
from apps.employees.models import Employee, JobInformation
from apps.reports.models import P9Report

def test_employee_pin_configuration():
    print("Testing Employee's P.I.N. configuration...")
    print("=" * 60)
    
    # Create or get a test user
    try:
        user = User.objects.filter(email='test.employee.pin@example.com').first()
        if not user:
            user = User.objects.create_user(
                email='test.employee.pin@example.com',
                first_name='John',
                last_name='Doe'
            )
        
        # Create or get employee
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'gross_salary': 50000.00
            }
        )
        
        # Create or update job information with KRA PIN
        test_kra_pin = 'A123456789B'
        job_info, created = JobInformation.objects.get_or_create(
            employee=employee,
            defaults={
                'company_employee_id': 'EMP001_PIN_TEST',
                'kra_pin': test_kra_pin,
                'department': 'IT',
                'position': 'Software Developer',
                'date_of_joining': '2024-01-01'
            }
        )
        
        if not created:
            job_info.kra_pin = test_kra_pin
            job_info.save()
        
        print(f"✓ Created test employee: {employee.user.first_name} {employee.user.last_name}")
        print(f"✓ Company Employee ID: {job_info.company_employee_id}")
        print(f"✓ KRA PIN in JobInformation: {job_info.kra_pin}")
        print()
        
        # Create P9 Report
        p9_report = P9Report.objects.create(
            employee=employee,
            tax_year=2024,
            total_basic_salary=600000.00,  # 12 months * 50000
            total_gross_pay=600000.00
        )
        
        print("P9 Report Employee Information:")
        print(f"  Employee Name: {p9_report.employee_name}")
        print(f"  Employee P.I.N.: {p9_report.employee_pin}")
        print(f"  Expected KRA PIN: {test_kra_pin}")
        print()
        
        # Verify the Employee's P.I.N. field matches the database KRA PIN
        if p9_report.employee_pin == test_kra_pin:
            print("✅ SUCCESS: Employee's P.I.N. correctly pulls from employee database!")
            print(f"✅ P9 Report Employee P.I.N.: {p9_report.employee_pin}")
            print(f"✅ Database KRA PIN: {job_info.kra_pin}")
        else:
            print("❌ ISSUE: Employee's P.I.N. does not match database KRA PIN")
            print(f"❌ P9 Report Employee P.I.N.: {p9_report.employee_pin}")
            print(f"❌ Database KRA PIN: {job_info.kra_pin}")
        
        print()
        print("Testing edge case: Employee without JobInformation...")
        
        # Test with employee without job info
        user2 = User.objects.create_user(
            email='test.no.job.info@example.com',
            first_name='Jane',
            last_name='Smith'
        )
        
        employee2 = Employee.objects.create(
            user=user2,
            gross_salary=40000.00
        )
        # Intentionally not creating JobInformation
        
        p9_report2 = P9Report.objects.create(
            employee=employee2,
            tax_year=2024,
            total_basic_salary=480000.00,
            total_gross_pay=480000.00
        )
        
        print(f"Employee without JobInformation:")
        print(f"  Employee Name: {p9_report2.employee_name}")
        print(f"  Employee P.I.N.: '{p9_report2.employee_pin}'")
        
        if p9_report2.employee_pin == '':
            print("✅ SUCCESS: Employee without JobInformation shows empty P.I.N. (handled gracefully)")
        else:
            print("❌ ISSUE: Employee without JobInformation should show empty P.I.N.")
        
        # Clean up test data
        p9_report.delete()
        p9_report2.delete()
        employee.delete()
        employee2.delete()
        user.delete()
        user2.delete()
        
        print()
        print("=" * 60)
        print("Employee's P.I.N. configuration test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_employee_pin_configuration()
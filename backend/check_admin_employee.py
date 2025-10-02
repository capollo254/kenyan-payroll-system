import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.core.models import User
from apps.employees.models import Employee

def check_admin_employee():
    try:
        admin_user = User.objects.get(email='admin@test.com')
        print(f"✅ Admin user found: {admin_user}")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Staff: {admin_user.is_staff}")
        print(f"   Superuser: {admin_user.is_superuser}")
        
        try:
            employee = Employee.objects.get(user=admin_user)
            print(f"✅ Employee record found: {employee}")
            print(f"   Employee ID: {employee.id}")
            print(f"   First Name: {employee.first_name}")
            print(f"   Last Name: {employee.last_name}")
        except Employee.DoesNotExist:
            print("❌ No Employee record found for admin user")
            print("Creating Employee record...")
            
            # Create employee record with minimal required fields
            employee = Employee.objects.create(
                user=admin_user,
                gross_salary=100000.00  # Default salary for admin
            )
            print(f"✅ Employee record created: {employee}")
            print(f"   Employee ID: {employee.id}")
            print(f"   Full Name: {employee.full_name()}")
            print(f"   Gross Salary: {employee.gross_salary}")
            
    except User.DoesNotExist:
        print("❌ Admin user not found")

if __name__ == "__main__":
    check_admin_employee()
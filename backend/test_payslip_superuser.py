#!/usr/bin/env python3
"""
Test script to verify that superusers can access payslips correctly.
"""

import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')

# Initialize Django
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from apps.payroll.models import Payslip
from apps.payroll.views import PayslipViewSet
from django.test import RequestFactory
from django.http import HttpRequest

User = get_user_model()

def test_superuser_payslip_access():
    """Test that superusers can access payslips correctly"""
    print("TESTING SUPERUSER PAYSLIP ACCESS")
    print("="*50)
    
    # Get all users and identify superusers
    all_users = User.objects.all()
    superusers = [u for u in all_users if u.is_superuser]
    
    print(f"Total users in system: {all_users.count()}")
    print(f"Superusers found: {len(superusers)}")
    
    for user in superusers:
        print(f"\nTesting superuser: {user.email}")
        print(f"- Is superuser: {user.is_superuser}")
        print(f"- Is staff: {user.is_staff}")
        print(f"- Is active: {user.is_active}")
        
        # Check if user has employee profile
        has_employee_profile = hasattr(user, 'employee_profile')
        print(f"- Has employee profile: {has_employee_profile}")
        
        if has_employee_profile:
            try:
                employee = user.employee_profile
                print(f"  - Employee ID: {employee.id}")
                print(f"  - Employee name: {employee.full_name()}")
            except Exception as e:
                print(f"  - Error accessing employee profile: {e}")
        
        # Test the PayslipViewSet queryset logic
        factory = RequestFactory()
        request = factory.get('/api/v1/payroll/payslips/')
        request.user = user
        
        viewset = PayslipViewSet()
        viewset.request = request
        queryset = viewset.get_queryset()
        
        print(f"- Payslips accessible: {queryset.count()}")
        
        if queryset.count() > 0:
            print("  SUCCESS: Superuser can access payslips")
            # Show first few payslips
            for i, payslip in enumerate(queryset[:3]):
                print(f"    - Payslip {i+1}: {payslip.employee.full_name()} - {payslip.payroll_run.run_date}")
        else:
            print("  WARNING: Superuser has no payslips accessible")
    
    # Also check total payslips in system
    total_payslips = Payslip.objects.count()
    print(f"\nTotal payslips in system: {total_payslips}")
    
    # Check regular employees too
    regular_employees = User.objects.filter(is_superuser=False, is_active=True)
    employees_with_payslips = 0
    
    for user in regular_employees[:5]:  # Test first 5 regular users
        if hasattr(user, 'employee_profile'):
            factory = RequestFactory()
            request = factory.get('/api/v1/payroll/payslips/')
            request.user = user
            
            viewset = PayslipViewSet()
            viewset.request = request
            queryset = viewset.get_queryset()
            
            if queryset.count() > 0:
                employees_with_payslips += 1
    
    print(f"Regular employees with payslips (sample): {employees_with_payslips}/5")
    
    return True

if __name__ == "__main__":
    test_superuser_payslip_access()
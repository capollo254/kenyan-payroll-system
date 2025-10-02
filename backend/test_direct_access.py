#!/usr/bin/env python
import os
import sys
import django
from django.test import Client
from django.contrib.auth import authenticate, get_user_model

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

User = get_user_model()

def test_direct_api_access():
    """Test direct API access by examining the PayslipViewSet logic"""
    print("TESTING DIRECT API ACCESS (PayslipViewSet)")
    print("=" * 50)
    
    from apps.payroll.views import PayslipViewSet
    from django.http import HttpRequest
    from rest_framework.request import Request
    
    # Get a superuser
    superuser = User.objects.filter(is_superuser=True, is_active=True).first()
    if not superuser:
        print("❌ No active superusers found")
        return
    
    print(f"Testing with superuser: {superuser.email}")
    
    # Create a mock request with the superuser
    http_request = HttpRequest()
    http_request.user = superuser
    request = Request(http_request)
    
    # Create viewset instance and test get_queryset
    viewset = PayslipViewSet()
    viewset.request = request
    
    try:
        queryset = viewset.get_queryset()
        count = queryset.count()
        print(f"✅ SUCCESS: Superuser can access {count} payslips directly")
        
        # Show some sample payslips
        if count > 0:
            sample_payslips = queryset[:3]
            print("Sample payslips:")
            for i, payslip in enumerate(sample_payslips):
                print(f"  - Payslip {i+1}: {payslip.employee.user.get_full_name() or payslip.employee.user.email} - {payslip.pay_date}")
    except Exception as e:
        print(f"❌ FAILED: Error accessing payslips: {e}")
        import traceback
        traceback.print_exc()

def test_employee_profile_check():
    """Test employee profile relationships"""
    print("\nTESTING EMPLOYEE PROFILE RELATIONSHIPS")
    print("=" * 50)
    
    superusers = User.objects.filter(is_superuser=True, is_active=True)
    for user in superusers:
        print(f"\nUser: {user.email}")
        print(f"  - Is superuser: {user.is_superuser}")
        print(f"  - Is staff: {user.is_staff}")
        
        # Check employee profile
        try:
            profile = user.employee_profile
            print(f"  - Has employee profile: Yes (ID: {profile.id})")
        except:
            print(f"  - Has employee profile: No")
        
        # Check hasattr approach (what the fixed code uses)
        has_profile = hasattr(user, 'employee_profile')
        print(f"  - hasattr(user, 'employee_profile'): {has_profile}")
        
        # Test the actual logic from the fixed get_queryset
        if user.is_superuser:
            from apps.payroll.models import Payslip
            all_payslips = Payslip.objects.all()
            print(f"  - Payslips available to superuser: {all_payslips.count()}")

if __name__ == '__main__':
    test_direct_api_access()
    test_employee_profile_check()
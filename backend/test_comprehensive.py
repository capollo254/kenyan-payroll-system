#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.payroll.models import Payslip
from apps.payroll.views import PayslipViewSet
from rest_framework.test import APIRequestFactory, force_authenticate

User = get_user_model()

def comprehensive_test():
    """Comprehensive test of superuser payslip access"""
    print("COMPREHENSIVE SUPERUSER PAYSLIP ACCESS TEST")
    print("=" * 60)
    
    # Get a superuser
    superuser = User.objects.filter(is_superuser=True, is_active=True).first()
    print(f"Testing superuser: {superuser.email}")
    print(f"  - is_superuser: {superuser.is_superuser}")
    print(f"  - is_active: {superuser.is_active}")
    
    # Test 1: Direct model query
    print(f"\n1. DIRECT MODEL QUERY:")
    all_payslips = Payslip.objects.all()
    print(f"   Total payslips in database: {all_payslips.count()}")
    
    # Test 2: ViewSet get_queryset method
    print(f"\n2. PAYSLIP VIEWSET get_queryset():")
    factory = APIRequestFactory()
    request = factory.get('/api/v1/payroll/payslips/')
    request.user = superuser
    
    viewset = PayslipViewSet()
    viewset.request = request
    
    queryset = viewset.get_queryset()
    print(f"   Queryset count: {queryset.count()}")
    
    if queryset.count() > 0:
        print("   Sample payslips from queryset:")
        for i, payslip in enumerate(queryset[:3]):
            print(f"     - {payslip.employee.user.get_full_name() or payslip.employee.user.email} - {payslip.payroll_run.run_date}")
    
    # Test 3: API endpoint via DRF test client
    print(f"\n3. DRF API CLIENT TEST:")
    from rest_framework.test import APIClient
    
    client = APIClient()
    client.force_authenticate(user=superuser)
    
    response = client.get('/api/v1/payroll/payslips/')
    print(f"   API response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        results = data.get('results', [])
        print(f"   API returned {count} total payslips")
        print(f"   Current page has {len(results)} results")
        
        if results:
            print("   Sample payslips from API:")
            for i, payslip in enumerate(results[:3]):
                employee_name = payslip.get('employee_name', 'N/A')
                pay_date = payslip.get('pay_date', 'N/A')
                print(f"     - {employee_name} - {pay_date}")
    else:
        print(f"   API error: {response.content}")
    
    # Test 4: Check if there are any filters or permissions
    print(f"\n4. PERMISSION CHECKS:")
    print(f"   User authenticated: {superuser.is_authenticated}")
    print(f"   Permission classes: {PayslipViewSet.permission_classes}")
    
    # Test 5: Database integrity check
    print(f"\n5. DATABASE INTEGRITY:")
    active_employees = User.objects.filter(is_active=True).count()
    print(f"   Active users: {active_employees}")
    
    from apps.employees.models import Employee
    employees = Employee.objects.all().count()
    print(f"   Employee profiles: {employees}")
    
    from apps.payroll.models import PayrollRun
    payroll_runs = PayrollRun.objects.all().count()
    print(f"   Payroll runs: {payroll_runs}")
    
    print(f"   Payslips: {all_payslips.count()}")

if __name__ == '__main__':
    comprehensive_test()
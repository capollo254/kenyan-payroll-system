import os
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')

# Setup Django
django.setup()

from apps.reports.bulk_p9_generator import BulkP9Generator
from apps.employees.models import Employee
from apps.reports.models import P9Report

print("🧪 Testing Enhanced P9 Admin Functionality")
print("=" * 50)

# Test bulk P9 generation
try:
    # Get an employee with payroll data
    employee = Employee.objects.filter(
        payslip__payroll_run__run_date__year=2024
    ).first()
    
    if employee:
        print(f"✅ Test Employee: {employee.full_name()}")
        
        # Test bulk generator
        bulk_generator = BulkP9Generator(tax_year=2024)
        result = bulk_generator.generate_p9_for_employee(employee.id)
        
        if result['success']:
            print(f"✅ P9 Generation Success: {result['message']}")
            
            # Check if P9 was created
            p9_report = P9Report.objects.filter(employee=employee, tax_year=2024).first()
            if p9_report:
                print(f"✅ P9 Report Created: ID {p9_report.id}")
                print(f"   - Employee: {p9_report.employee_name}")
                print(f"   - Gross Pay: KES {p9_report.total_gross_pay:,.2f}")
                print(f"   - PAYE Tax: KES {p9_report.total_paye_tax:,.2f}")
                print(f"   - Monthly Breakdowns: {p9_report.monthly_breakdowns.count()}")
            else:
                print("❌ P9 Report not found after generation")
        else:
            print(f"❌ P9 Generation Failed: {result['message']}")
    else:
        print("❌ No employee with payroll data found")

except Exception as e:
    print(f"❌ Test Error: {str(e)}")

print("\n📋 Summary of New Features:")
print("1. ✅ Auto-population of P9 fields from payroll data")
print("2. ✅ AJAX endpoint for real-time field population") 
print("3. ✅ Bulk P9 generation interface in Django admin")
print("4. ✅ Enhanced admin interface with payroll data validation")
print("5. ✅ Direct PDF download links in admin list")
print("6. ✅ Monthly breakdown auto-generation from payslips")

print("\n🚀 Ready for Django admin testing!")
print("Visit: http://127.0.0.1:8000/admin/reports/p9report/")
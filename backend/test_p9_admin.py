#!/usr/bin/env python
"""
Test P9 Admin Registration
Check if P9 models are properly registered in Django admin
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib import admin
from apps.reports.models import P9Report, P9MonthlyBreakdown

def test_admin_registration():
    """Test that P9 models are registered in Django admin"""
    
    print("🔍 Testing P9 Admin Registration...")
    
    # Check if P9Report is registered
    if P9Report in admin.site._registry:
        print("✅ P9Report is registered in Django admin")
        admin_class = admin.site._registry[P9Report]
        print(f"   Admin class: {admin_class.__class__.__name__}")
    else:
        print("❌ P9Report not registered in Django admin")
    
    # Check if P9MonthlyBreakdown is registered
    if P9MonthlyBreakdown in admin.site._registry:
        print("✅ P9MonthlyBreakdown is registered in Django admin")
        admin_class = admin.site._registry[P9MonthlyBreakdown]
        print(f"   Admin class: {admin_class.__class__.__name__}")
    else:
        print("❌ P9MonthlyBreakdown not registered in Django admin")
    
    # List all registered models from reports app
    print(f"\n📋 All registered models from reports app:")
    reports_models = [model for model in admin.site._registry.keys() 
                     if model._meta.app_label == 'reports']
    
    for model in reports_models:
        print(f"   - {model._meta.verbose_name} ({model.__name__})")
    
    # Check P9 data
    p9_count = P9Report.objects.count()
    print(f"\n📊 P9 Reports in database: {p9_count}")
    
    if p9_count > 0:
        latest_p9 = P9Report.objects.latest('generated_date')
        print(f"   Latest P9: {latest_p9.employee_name} ({latest_p9.tax_year})")
        print(f"   Status: {latest_p9.get_status_display()}")
        print(f"   PAYE Tax: KES {latest_p9.total_paye_tax:,.2f}")
    
    # Provide direct access instructions
    print(f"\n🌐 Django Admin Access:")
    print(f"   1. Start Django server: python manage.py runserver")
    print(f"   2. Open: http://127.0.0.1:8000/admin/")
    print(f"   3. Navigate to: Reports > P9 reports")
    print(f"   4. Direct URL: http://127.0.0.1:8000/admin/reports/p9report/")
    
    # Check Django settings
    from django.conf import settings
    print(f"\n⚙️ Django Configuration:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   INSTALLED_APPS includes reports: {'apps.reports' in settings.INSTALLED_APPS}")
    
    return True

if __name__ == "__main__":
    test_admin_registration()
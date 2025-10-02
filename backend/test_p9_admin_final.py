#!/usr/bin/env python3
"""
Test Django Admin P9 Registration
"""

import os
import sys
import django

# Add backend to path and configure Django
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib import admin
from apps.reports.models import P9Report, P9MonthlyBreakdown

def test_admin_registration():
    print("=== Django Admin P9 Registration Test ===")
    
    # Check if P9Report is registered
    if P9Report in admin.site._registry:
        print("✅ P9Report is registered in Django admin")
        admin_class = admin.site._registry[P9Report]
        print(f"   Admin class: {admin_class.__class__.__name__}")
    else:
        print("❌ P9Report is NOT registered in Django admin")
    
    # Check if P9MonthlyBreakdown is registered
    if P9MonthlyBreakdown in admin.site._registry:
        print("✅ P9MonthlyBreakdown is registered in Django admin")
        admin_class = admin.site._registry[P9MonthlyBreakdown]
        print(f"   Admin class: {admin_class.__class__.__name__}")
    else:
        print("❌ P9MonthlyBreakdown is NOT registered in Django admin")
    
    print(f"\n📋 Total registered models: {len(admin.site._registry)}")
    
    # List all registered models
    print("\n📝 All registered models:")
    for model, admin_class in admin.site._registry.items():
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        print(f"  • {app_label}.{model_name} -> {admin_class.__class__.__name__}")
    
    return True

if __name__ == '__main__':
    try:
        test_admin_registration()
        print("\n🎯 Django server should be running at: http://127.0.0.1:8000/")
        print("🔗 P9 Admin URL: http://127.0.0.1:8000/admin/reports/p9report/")
        print("🔐 Make sure you have superuser access to view admin interface")
        
    except Exception as e:
        print(f"❌ Error testing admin registration: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
Test and Force Django Admin Reload
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
from django.apps import apps
from apps.reports.models import P9Report, P9MonthlyBreakdown

def force_admin_reload():
    print("=== Force Django Admin Reload ===")
    
    # Clear admin registry for reports models
    models_to_clear = [P9Report, P9MonthlyBreakdown]
    for model in models_to_clear:
        if model in admin.site._registry:
            print(f"🗑️  Removing {model._meta.label} from admin registry")
            del admin.site._registry[model]
    
    # Force reimport of admin module
    try:
        import importlib
        import apps.reports.admin
        importlib.reload(apps.reports.admin)
        print("✅ Reloaded apps.reports.admin")
        
        # Re-register models
        from apps.reports.admin import P9ReportAdmin, P9MonthlyBreakdownAdmin
        admin.site.register(P9Report, P9ReportAdmin)
        admin.site.register(P9MonthlyBreakdown, P9MonthlyBreakdownAdmin)
        print("✅ Re-registered P9 models in admin")
        
    except Exception as e:
        print(f"❌ Error reloading admin: {e}")
        import traceback
        traceback.print_exc()
    
    # Check current registration status
    print("\n=== Current Admin Registration ===")
    reports_models = 0
    for model, admin_class in admin.site._registry.items():
        if model._meta.app_label == 'reports':
            reports_models += 1
            print(f"✅ {model._meta.label} -> {admin_class.__class__.__name__}")
    
    print(f"\n📊 Total Reports models in admin: {reports_models}")
    
    if reports_models > 0:
        print("🎉 Reports app should now appear in Django admin!")
        print("🔄 Please restart Django server and refresh browser")
    else:
        print("❌ Reports models still not registered")
    
    return reports_models > 0

if __name__ == '__main__':
    try:
        success = force_admin_reload()
        if success:
            print("\n✅ Admin reload successful!")
            print("🌐 Restart Django server: python manage.py runserver")
            print("🔗 Then visit: http://127.0.0.1:8000/admin/")
        else:
            print("\n❌ Admin reload failed - check for errors above")
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
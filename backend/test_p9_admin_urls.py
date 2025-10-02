#!/usr/bin/env python3
"""
Test P9 Admin Registration by Direct Import
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
from django.urls import reverse
from django.test import RequestFactory
from apps.reports.models import P9Report, P9MonthlyBreakdown
from apps.reports.admin import P9ReportAdmin

def test_p9_admin_urls():
    print("=== Testing P9 Admin URL Generation ===")
    
    try:
        # Test reverse URL lookup
        p9_list_url = reverse('admin:reports_p9report_changelist')
        p9_add_url = reverse('admin:reports_p9report_add')
        
        print(f"✅ P9 List URL: {p9_list_url}")
        print(f"✅ P9 Add URL: {p9_add_url}")
        
        # Test if admin is properly registered
        if P9Report in admin.site._registry:
            admin_instance = admin.site._registry[P9Report]
            print(f"✅ P9Report admin class: {admin_instance.__class__.__name__}")
            print(f"✅ P9Report app label: {P9Report._meta.app_label}")
            print(f"✅ P9Report model name: {P9Report._meta.model_name}")
        else:
            print("❌ P9Report not registered in admin")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing admin URLs: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_all_admin_urls():
    print("\n=== All Admin URLs ===")
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        
        admin_patterns = []
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'app_name') and pattern.app_name == 'admin':
                admin_patterns.append(pattern)
        
        print(f"Found {len(admin_patterns)} admin patterns")
        
        # List all registered models
        print("\n📋 All Registered Admin Models:")
        for model, admin_class in admin.site._registry.items():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            url_name = f"admin:{app_label}_{model_name}_changelist"
            try:
                url = reverse(url_name)
                print(f"  • {app_label}.{model_name} -> {url}")
            except Exception as e:
                print(f"  ❌ {app_label}.{model_name} -> URL generation failed: {e}")
                
    except Exception as e:
        print(f"❌ Error listing admin URLs: {e}")

if __name__ == '__main__':
    print("🧪 Testing P9 Admin Configuration")
    
    try:
        success = test_p9_admin_urls()
        show_all_admin_urls()
        
        if success:
            print("\n✅ P9 Admin should be accessible!")
            print("🌐 Make sure Django server is running at: http://127.0.0.1:8000/")
            print("🔗 Try: http://127.0.0.1:8000/admin/reports/p9report/")
        else:
            print("\n❌ P9 Admin configuration has issues")
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
Comprehensive P9 Admin Diagnosis
"""

import os
import sys
import django

# Add backend to path and configure Django
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

def diagnose_p9_admin():
    print("=== P9 Admin Diagnosis ===")
    
    # 1. Check if models exist and can be imported
    try:
        from apps.reports.models import P9Report, P9MonthlyBreakdown
        print("✅ P9 models imported successfully")
        print(f"   P9Report: {P9Report}")
        print(f"   P9MonthlyBreakdown: {P9MonthlyBreakdown}")
    except Exception as e:
        print(f"❌ Error importing P9 models: {e}")
        return False
    
    # 2. Check if admin classes exist
    try:
        from apps.reports.admin import P9ReportAdmin, P9MonthlyBreakdownAdmin
        print("✅ P9 admin classes imported successfully")
        print(f"   P9ReportAdmin: {P9ReportAdmin}")
        print(f"   P9MonthlyBreakdownAdmin: {P9MonthlyBreakdownAdmin}")
    except Exception as e:
        print(f"❌ Error importing P9 admin classes: {e}")
        return False
    
    # 3. Check Django admin registration
    from django.contrib import admin
    
    print(f"\n📋 Django admin registry has {len(admin.site._registry)} models")
    
    reports_models = []
    for model, admin_class in admin.site._registry.items():
        if model._meta.app_label == 'reports':
            reports_models.append(f"{model._meta.model_name} -> {admin_class.__class__.__name__}")
    
    if reports_models:
        print("✅ Reports models in admin:")
        for model_info in reports_models:
            print(f"   • {model_info}")
    else:
        print("❌ NO Reports models found in admin registry!")
    
    # 4. Check URL generation
    try:
        from django.urls import reverse
        p9_url = reverse('admin:reports_p9report_changelist')
        print(f"✅ P9 admin URL: {p9_url}")
    except Exception as e:
        print(f"❌ Error generating P9 admin URL: {e}")
        return False
    
    # 5. Check apps configuration
    from django.apps import apps
    reports_app = apps.get_app_config('reports')
    print(f"✅ Reports app config: {reports_app}")
    print(f"   Name: {reports_app.name}")
    print(f"   Verbose name: {reports_app.verbose_name}")
    
    # 6. Check data existence
    p9_count = P9Report.objects.count()
    print(f"📊 P9 Reports in database: {p9_count}")
    
    if p9_count > 0:
        sample = P9Report.objects.first()
        print(f"   Sample: {sample.employee_name} ({sample.tax_year})")
    
    return len(reports_models) > 0

def show_admin_sections():
    """Show what sections will appear in Django admin"""
    from django.contrib import admin
    
    sections = {}
    for model, admin_class in admin.site._registry.items():
        app_label = model._meta.app_label
        app_name = model._meta.app_config.verbose_name if hasattr(model._meta, 'app_config') else app_label.upper()
        
        if app_name not in sections:
            sections[app_name] = []
        
        sections[app_name].append({
            'model': model._meta.model_name,
            'verbose_name': model._meta.verbose_name,
            'admin_class': admin_class.__class__.__name__
        })
    
    print("\n=== Django Admin Sections ===")
    for app_name, models in sections.items():
        print(f"📁 {app_name.upper()}")
        for model_info in models:
            print(f"   • {model_info['verbose_name']} ({model_info['model']})")

if __name__ == '__main__':
    try:
        print("🔍 Running P9 Admin Diagnosis...")
        success = diagnose_p9_admin()
        show_admin_sections()
        
        if success:
            print("\n✅ P9 Admin should be visible in Django Admin!")
            print("🌐 Server: http://127.0.0.1:8001/admin/ (or 8000)")
            print("📍 Look for 'REPORTS' section with 'P9 Tax Reports'")
        else:
            print("\n❌ P9 Admin has configuration issues")
            
    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
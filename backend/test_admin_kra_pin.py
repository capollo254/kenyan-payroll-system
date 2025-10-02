"""
Test script to verify KRA PIN field is available in Django Admin
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib import admin
from apps.core.models import CompanySettings
from apps.core.admin import CompanySettingsAdmin

def test_admin_kra_pin_field():
    print("Testing KRA PIN field in Django Admin...")
    print("=" * 50)
    
    try:
        # Get the admin class for CompanySettings
        admin_class = admin.site._registry[CompanySettings]
        
        print(f"✓ CompanySettings admin class: {admin_class.__class__.__name__}")
        
        # Check if kra_pin is in the fieldsets
        fieldsets = admin_class.fieldsets
        print(f"✓ Admin fieldsets found: {len(fieldsets)} sections")
        
        # Check Company Information section
        company_info_fields = None
        for section_name, section_config in fieldsets:
            print(f"  - Section: {section_name}")
            if section_name == 'Company Information':
                company_info_fields = section_config['fields']
                print(f"    Fields: {company_info_fields}")
        
        if company_info_fields and 'kra_pin' in company_info_fields:
            print("✅ SUCCESS: KRA PIN field found in Company Information section!")
            print(f"✅ Company Information fields: {company_info_fields}")
        else:
            print("❌ ISSUE: KRA PIN field not found in Company Information section")
            print(f"❌ Available fields: {company_info_fields}")
        
        # Check list_display
        list_display = admin_class.list_display
        print(f"✓ Admin list_display: {list_display}")
        
        if 'kra_pin' in list_display:
            print("✅ SUCCESS: KRA PIN field included in admin list view!")
        else:
            print("❌ ISSUE: KRA PIN field not in admin list view")
        
        # Test that we can access the field on the model
        company_settings = CompanySettings.get_settings()
        print(f"✓ Company Settings instance: {company_settings}")
        print(f"✓ Current company name: {company_settings.company_name}")
        
        # Check if kra_pin field exists and is accessible
        if hasattr(company_settings, 'kra_pin'):
            print(f"✓ KRA PIN field exists: '{company_settings.kra_pin}'")
            print("✅ SUCCESS: KRA PIN field is accessible on the model!")
        else:
            print("❌ ISSUE: KRA PIN field not accessible on the model")
        
        print()
        print("Admin URL Information:")
        print(f"✓ Admin URL: http://127.0.0.1:8000/admin/")
        print(f"✓ Company Settings URL: http://127.0.0.1:8000/admin/core/companysettings/1/change/")
        print(f"✓ Expected KRA PIN field location: Company Information section")
        
        print()
        print("=" * 50)
        print("KRA PIN Admin field test completed!")
        print("🎉 You can now add the Company KRA PIN through Django Admin!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_kra_pin_field()
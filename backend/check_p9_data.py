#!/usr/bin/env python3
"""
Check P9 Reports data in the database
"""

import os
import sys
import django

# Add backend to path and configure Django
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.reports.models import P9Report, P9MonthlyBreakdown

def check_p9_data():
    print("=== P9 Data Check ===")
    
    # Check P9 Reports
    p9_reports = P9Report.objects.all()
    print(f"📊 Total P9 Reports: {p9_reports.count()}")
    
    if p9_reports.exists():
        print("\n📋 P9 Reports:")
        for report in p9_reports:
            print(f"  • {report.employee_name} ({report.tax_year})")
            print(f"    - Gross Pay: KES {report.total_gross_pay:,.2f}")
            print(f"    - PAYE Tax: KES {report.total_paye_tax:,.2f}")
            print(f"    - Status: {report.status}")
            print(f"    - Monthly Breakdowns: {report.monthly_breakdown.count()}")
            print()
    else:
        print("❌ No P9 reports found in database")
    
    # Check Monthly Breakdowns
    monthly_breakdowns = P9MonthlyBreakdown.objects.all()
    print(f"📅 Total Monthly Breakdowns: {monthly_breakdowns.count()}")
    
    return p9_reports.count() > 0

if __name__ == '__main__':
    try:
        has_data = check_p9_data()
        if has_data:
            print("✅ P9 system has data and should be accessible in Django Admin")
            print("🔗 Visit: http://127.0.0.1:8000/admin/reports/p9report/")
        else:
            print("⚠️  P9 system exists but has no data yet")
            print("💡 Run test_p9_generation.py to create sample data")
            
    except Exception as e:
        print(f"❌ Error checking P9 data: {e}")
        import traceback
        traceback.print_exc()
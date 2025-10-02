#!/usr/bin/env python3
"""
Bulk P9 Generation Script
Run this script to generate P9 forms for all employees with payroll data
"""

import os
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')

# Setup Django
django.setup()

from apps.reports.bulk_p9_generator import BulkP9Generator
from apps.employees.models import Employee
from apps.payroll.models import Payslip

def generate_all_p9_reports(tax_year=2025):
    """Generate P9 reports for all employees with payroll data"""
    
    print(f"🚀 Bulk P9 Generation for {tax_year}")
    print("=" * 50)
    
    # Initialize bulk generator
    bulk_generator = BulkP9Generator(tax_year=tax_year)
    
    try:
        # Get all employees with payroll data for the tax year
        employees_with_payroll = Employee.objects.filter(
            payslips__payroll_run__run_date__year=tax_year
        ).distinct()
        
        print(f"📊 Found {employees_with_payroll.count()} employees with payroll data for {tax_year}")
        
        # Generate P9 for all employees
        results = []
        successful = 0
        failed = 0
        
        for employee in employees_with_payroll:
            print(f"\n🔄 Processing: {employee.full_name()}")
            
            # Check if P9 already exists
            from apps.reports.models import P9Report
            existing_p9 = P9Report.objects.filter(employee=employee, tax_year=tax_year).first()
            
            if existing_p9:
                print(f"   ⏭️  P9 already exists (ID: {existing_p9.id})")
                continue
            
            # Generate P9
            result = bulk_generator.generate_p9_for_employee(employee.id)
            
            if result['success']:
                print(f"   ✅ SUCCESS: {result['message']}")
                successful += 1
            else:
                print(f"   ❌ FAILED: {result['message']}")
                failed += 1
            
            results.append(result)
        
        # Summary
        print(f"\n📋 BULK GENERATION COMPLETE!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total Processed: {len(results)}")
        
        # Show generated P9s
        from apps.reports.models import P9Report
        all_p9s = P9Report.objects.filter(tax_year=tax_year)
        print(f"\n📄 Total P9 Reports for {tax_year}: {all_p9s.count()}")
        
        for p9 in all_p9s:
            print(f"   • {p9.employee_name}: KES {p9.total_gross_pay:,.2f} gross, KES {p9.total_paye_tax:,.2f} PAYE")
        
        return results
        
    except Exception as e:
        print(f"❌ Bulk generation failed: {str(e)}")
        return []

if __name__ == "__main__":
    # Run bulk generation for 2025 (current payroll data year)
    results = generate_all_p9_reports(tax_year=2025)
    
    print(f"\n🎉 Bulk P9 generation completed!")
    print(f"Visit Django admin to view/download generated P9s:")
    print(f"http://127.0.0.1:8000/admin/reports/p9report/")
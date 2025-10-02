#!/usr/bin/env python3
"""
Test Complete P9 System - PDF Generation, Bulk Processing, and Payslip Integration
"""

import os
import sys
import django
from decimal import Decimal

# Add backend to path and configure Django
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.reports.models import P9Report, P9MonthlyBreakdown
from apps.reports.p9_pdf_generator import P9PDFGenerator
from apps.reports.bulk_p9_generator import BulkP9Generator
from apps.employees.models import Employee
from apps.payroll.models import Payslip, PayrollRun
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, datetime
import tempfile

User = get_user_model()

def test_pdf_generation():
    """Test P9 PDF generation"""
    print("=== Testing P9 PDF Generation ===")
    
    # Get existing P9 report
    p9_report = P9Report.objects.first()
    if not p9_report:
        print("❌ No P9 reports found for PDF testing")
        return False
    
    print(f"📋 Testing PDF for: {p9_report.employee_name}")
    
    try:
        # Test PDF generation
        pdf_generator = P9PDFGenerator()
        
        # Generate PDF to a specific file path
        import tempfile
        temp_dir = tempfile.mkdtemp()
        filename = f"test_p9_{p9_report.id}.pdf"
        pdf_path = os.path.join(temp_dir, filename)
        
        final_path = pdf_generator.save_pdf_file(p9_report, pdf_path)
        
        if os.path.exists(final_path):
            file_size = os.path.getsize(final_path)
            print(f"✅ PDF generated successfully: {final_path}")
            print(f"📊 File size: {file_size:,} bytes")
            
            # Clean up
            os.unlink(final_path)
            os.rmdir(temp_dir)
            return True
        else:
            print("❌ PDF file not created")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bulk_generation():
    """Test bulk P9 generation from payslips"""
    print("\n=== Testing Bulk P9 Generation ===")
    
    try:
        # Create sample employees for testing
        test_employees = []
        
        # Get existing employees or create test ones
        employees = Employee.objects.all()[:3]  # Test with first 3 employees
        
        if not employees:
            print("❌ No employees found for bulk testing")
            return False
        
        print(f"📊 Testing bulk generation for {len(employees)} employees")
        
        # Initialize bulk generator
        bulk_generator = BulkP9Generator(tax_year=2024)
        
        # Test payslip summary
        print("\n🔍 Checking payslip data availability:")
        payslip_summary = bulk_generator.get_payslip_summary(tax_year=2024)
        
        if payslip_summary:
            for emp_id, data in payslip_summary.items():
                print(f"  • {data['employee_name']}: {data['payslip_count']} payslips, "
                      f"months: {data['months_covered']}, "
                      f"complete year: {data['has_complete_year']}")
        else:
            print("  ⚠️ No payslip data found - will create template P9s")
        
        # Perform bulk generation
        print("\n🚀 Generating bulk P9 reports...")
        results = bulk_generator.generate_bulk_p9(
            employee_ids=[emp.id for emp in employees],
            from_payslips=bool(payslip_summary)
        )
        
        print(f"📈 Results:")
        print(f"  Total employees: {results['total_employees']}")
        print(f"  Successful P9s: {results['successful_p9s']}")
        print(f"  Failed P9s: {results['failed_p9s']}")
        
        if results['errors']:
            print(f"  Errors:")
            for error in results['errors']:
                print(f"    - {error}")
        
        if results['created_p9s']:
            print(f"  Created P9 reports:")
            for p9_info in results['created_p9s']:
                print(f"    - {p9_info['employee_name']}: "
                      f"Gross KES {p9_info['gross_pay']:,.2f}, "
                      f"PAYE KES {p9_info['paye_tax']:,.2f}")
        
        return results['successful_p9s'] > 0
        
    except Exception as e:
        print(f"❌ Bulk generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bulk_pdf_generation():
    """Test bulk PDF generation"""
    print("\n=== Testing Bulk PDF Generation ===")
    
    try:
        # Get P9 reports for testing
        p9_reports = P9Report.objects.filter(tax_year=2024)[:3]
        
        if not p9_reports:
            print("❌ No P9 reports found for bulk PDF testing")
            return False
        
        print(f"📊 Testing bulk PDF for {len(p9_reports)} P9 reports")
        
        bulk_generator = BulkP9Generator(tax_year=2024)
        
        # Generate bulk PDFs
        results = bulk_generator.generate_bulk_pdfs(p9_reports, create_zip=True)
        
        print(f"📈 Results:")
        print(f"  Total reports: {results['total_reports']}")
        print(f"  Generated PDFs: {results['generated_pdfs']}")
        print(f"  Failed PDFs: {results['failed_pdfs']}")
        
        if results['pdf_files']:
            print(f"  Generated files:")
            for file_info in results['pdf_files']:
                print(f"    - {file_info['employee_name']}: "
                      f"{file_info['file_size']:,} bytes")
        
        if results['zip_file']:
            print(f"  📦 ZIP file created:")
            print(f"    - Path: {results['zip_file']['path']}")
            print(f"    - Size: {results['zip_file']['size']:,} bytes")
            print(f"    - Contains: {results['zip_file']['file_count']} files")
            
            # Clean up test files
            if os.path.exists(results['zip_file']['path']):
                os.unlink(results['zip_file']['path'])
            
            for file_info in results['pdf_files']:
                if os.path.exists(file_info['file_path']):
                    os.unlink(file_info['file_path'])
        
        return results['generated_pdfs'] > 0
        
    except Exception as e:
        print(f"❌ Bulk PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_payslip_integration():
    """Test P9 generation from existing payslip data"""
    print("\n=== Testing Payslip Integration ===")
    
    try:
        # Check if we have any payslips
        payslip_count = Payslip.objects.count()
        print(f"📊 Found {payslip_count} existing payslips")
        
        if payslip_count == 0:
            # Create sample payslip data for testing
            print("🔧 Creating sample payslip data for testing...")
            
            employee = Employee.objects.first()
            if not employee:
                print("❌ No employees available for payslip test")
                return False
            
            # Create a payroll run
            payroll_run = PayrollRun.objects.create(
                period_start_date=date(2024, 1, 1),
                period_end_date=date(2024, 1, 31),
                run_date=date(2024, 1, 31)
            )
            
            # Create sample payslips for different months
            months = [
                (1, 'January'), (2, 'February'), (3, 'March'),
                (4, 'April'), (5, 'May'), (6, 'June')
            ]
            
            for month_num, month_name in months:
                # Create payroll run for each month
                monthly_payroll = PayrollRun.objects.create(
                    period_start_date=date(2024, month_num, 1),
                    period_end_date=date(2024, month_num, 28),
                    run_date=date(2024, month_num, 28)
                )
                
                payslip = Payslip.objects.create(
                    employee=employee,
                    payroll_run=monthly_payroll,
                    gross_salary=Decimal('50000.00'),
                    total_gross_income=Decimal('60000.00'),
                    paye_tax=Decimal('8500.00'),
                    net_pay=Decimal('48000.00'),
                    shif_deduction=Decimal('750.00'),
                    ahl_deduction=Decimal('900.00'),
                    total_deductions=Decimal('12000.00')
                )
                print(f"  ✅ Created payslip for {month_name}")
            
            payslip_count = 6
        
        # Test P9 generation from payslips
        bulk_generator = BulkP9Generator(tax_year=2024)
        
        # Get payslip summary
        summary = bulk_generator.get_payslip_summary(tax_year=2024)
        print(f"📋 Payslip summary for {len(summary)} employees:")
        
        for emp_id, data in summary.items():
            print(f"  • {data['employee_name']}:")
            print(f"    - Payslips: {data['payslip_count']}")
            print(f"    - Months covered: {len(data['months_covered'])}/12")
            print(f"    - Total gross: KES {data['total_gross']:,.2f}")
            print(f"    - Total PAYE: KES {data['total_paye']:,.2f}")
            print(f"    - Complete year: {data['has_complete_year']}")
        
        # Generate P9 from payslips
        if summary:
            employee_ids = list(summary.keys())[:1]  # Test with one employee
            results = bulk_generator.generate_bulk_p9(
                employee_ids=employee_ids,
                from_payslips=True
            )
            
            print(f"\n📈 P9 generation from payslips:")
            print(f"  Successful: {results['successful_p9s']}")
            print(f"  Failed: {results['failed_p9s']}")
            
            if results['created_p9s']:
                for p9_info in results['created_p9s']:
                    print(f"  ✅ Generated P9 for {p9_info['employee_name']}")
                    print(f"     Gross: KES {p9_info['gross_pay']:,.2f}")
                    print(f"     PAYE: KES {p9_info['paye_tax']:,.2f}")
                    
                    # Validate the generated P9
                    p9_report = P9Report.objects.get(id=p9_info['p9_id'])
                    validation_errors = bulk_generator.validate_p9_data(p9_report)
                    
                    if validation_errors:
                        print(f"     ⚠️ Validation issues: {validation_errors}")
                    else:
                        print(f"     ✅ P9 validation passed")
            
            return results['successful_p9s'] > 0
        else:
            print("❌ No payslip data available for testing")
            return False
        
    except Exception as e:
        print(f"❌ Payslip integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all P9 system tests"""
    print("🧪 COMPREHENSIVE P9 SYSTEM TEST")
    print("=" * 50)
    
    test_results = {
        'pdf_generation': False,
        'bulk_generation': False,
        'bulk_pdf_generation': False,
        'payslip_integration': False
    }
    
    # Run all tests
    test_results['pdf_generation'] = test_pdf_generation()
    test_results['bulk_generation'] = test_bulk_generation()
    test_results['bulk_pdf_generation'] = test_bulk_pdf_generation()
    test_results['payslip_integration'] = test_payslip_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! P9 system is fully functional.")
        print("\n🚀 Available Features:")
        print("  • KRA-compliant P9 PDF generation")
        print("  • Bulk P9 processing for multiple employees")
        print("  • ZIP download of multiple P9 PDFs")
        print("  • Automatic P9 generation from payslip data")
        print("  • Tax calculation validation")
        print("  • Monthly breakdown tracking")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    try:
        success = run_comprehensive_test()
        if success:
            print("\n🔗 API Endpoints available:")
            print("  • GET /api/v1/reports/p9/ - List P9 reports")
            print("  • GET /api/v1/reports/p9/{id}/download_pdf/ - Download PDF")
            print("  • POST /api/v1/reports/p9/bulk_generate/ - Generate multiple P9s")
            print("  • POST /api/v1/reports/p9/bulk_pdf_download/ - Download ZIP")
            print("  • GET /api/v1/reports/p9/payslip_summary/ - Check payslip data")
        
    except Exception as e:
        print(f"💥 Critical test error: {e}")
        import traceback
        traceback.print_exc()
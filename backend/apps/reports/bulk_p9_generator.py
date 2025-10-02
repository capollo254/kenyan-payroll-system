"""
Bulk P9 Generation System
Automatically generate P9 reports for all employees from payslip data
"""

from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from apps.reports.models import P9Report, P9MonthlyBreakdown
from apps.employees.models import Employee
from apps.payroll.models import Payslip, PayrollRun, PayslipDeduction
from apps.reports.p9_pdf_generator import P9PDFGenerator
import os
from django.conf import settings
import zipfile
from io import BytesIO


class BulkP9Generator:
    """Generate P9 reports for multiple employees from payslip data"""
    
    def __init__(self, tax_year=None):
        self.tax_year = tax_year or timezone.now().year
        self.pdf_generator = P9PDFGenerator()
        self.errors = []
        self.success_count = 0
        
    def generate_bulk_p9(self, employee_ids=None, from_payslips=True):
        """
        Generate P9 reports for multiple employees
        
        Args:
            employee_ids: List of employee IDs to process (None = all employees)
            from_payslips: Whether to generate from existing payslip data
        
        Returns:
            dict: Results summary with success/error counts
        """
        
        employees = Employee.objects.all()
        if employee_ids:
            employees = employees.filter(id__in=employee_ids)
        
        results = {
            'total_employees': employees.count(),
            'successful_p9s': 0,
            'failed_p9s': 0,
            'errors': [],
            'created_p9s': []
        }
        
        for employee in employees:
            try:
                if from_payslips:
                    p9_report = self._generate_p9_from_payslips(employee)
                else:
                    p9_report = self._generate_empty_p9(employee)
                
                if p9_report:
                    results['successful_p9s'] += 1
                    results['created_p9s'].append({
                        'employee_id': employee.id,
                        'employee_name': f"{employee.user.first_name} {employee.user.last_name}",
                        'p9_id': p9_report.id,
                        'gross_pay': float(p9_report.total_gross_pay),
                        'paye_tax': float(p9_report.total_paye_tax)
                    })
                
            except Exception as e:
                results['failed_p9s'] += 1
                error_msg = f"Employee {employee.user.first_name} {employee.user.last_name}: {str(e)}"
                results['errors'].append(error_msg)
                self.errors.append(error_msg)
        
        return results

    def _generate_p9_from_payslips(self, employee):
        """Generate P9 report from existing payslip data"""
        
        # Get or create P9 report
        p9_report, created = P9Report.objects.get_or_create(
            employee=employee,
            tax_year=self.tax_year,
            defaults={
                'generated_by': None,  # System generated
                'status': 'generated'
            }
        )
        
        # Get payslips for the tax year
        payslips = Payslip.objects.filter(
            employee=employee,
            payroll_run__period_start_date__year=self.tax_year
        ).select_related('payroll_run').order_by('payroll_run__run_date')
        
        if not payslips.exists():
            # Create empty P9 if no payslips
            return self._generate_empty_p9(employee, p9_report)
        
        # Aggregate data from payslips
        total_basic_salary = Decimal('0.00')
        total_gross_pay = Decimal('0.00')
        total_paye_tax = Decimal('0.00')
        total_benefits = Decimal('0.00')
        
        monthly_data = {}
        
        for payslip in payslips:
            month = payslip.payroll_run.period_start_date.month
            
            # Aggregate totals
            basic_salary = payslip.gross_salary or Decimal('0.00')  # Using gross_salary as basic
            gross_pay = payslip.total_gross_income or Decimal('0.00')
            paye_tax = payslip.paye_tax or Decimal('0.00')
            
            total_basic_salary += basic_salary
            total_gross_pay += gross_pay
            total_paye_tax += paye_tax
            
            # Store monthly data
            if month not in monthly_data:
                monthly_data[month] = {
                    'basic_salary': Decimal('0.00'),
                    'gross_pay': Decimal('0.00'),
                    'paye_tax': Decimal('0.00'),
                    'benefits': Decimal('0.00'),
                    'ahl': Decimal('0.00'),
                    'shif': Decimal('0.00'),
                }
            
            monthly_data[month]['basic_salary'] += basic_salary
            monthly_data[month]['gross_pay'] += gross_pay  
            monthly_data[month]['paye_tax'] += paye_tax
            
            # Calculate AHL (1.5% of gross)
            monthly_data[month]['ahl'] += gross_pay * Decimal('0.015')
            
            # Add SHIF if available
            monthly_data[month]['shif'] += payslip.shif_deduction or Decimal('0.00')
            
            # Calculate benefits as difference between total gross and basic
            benefits = (gross_pay - basic_salary) if gross_pay > basic_salary else Decimal('0.00')
            total_benefits += benefits
            monthly_data[month]['benefits'] += benefits
        
        # Update P9 report with calculated values
        p9_report.total_basic_salary = total_basic_salary
        p9_report.total_benefits_non_cash = total_benefits
        p9_report.total_gross_pay = total_gross_pay
        p9_report.total_paye_tax = total_paye_tax
        
        # Set SHIF total
        p9_report.total_shif = sum(payslip.shif_deduction or Decimal('0.00') for payslip in payslips)
        
        # Calculate retirement contributions (E1, E2, E3)
        # E1: 30% of Basic Salary
        p9_report.retirement_30_percent = total_basic_salary * Decimal('0.30')
        
        # E2: Actual contributions (NSSF + Pension from voluntary deductions)
        total_nssf = Decimal('0.00')
        total_pension = Decimal('0.00')
        
        for payslip in payslips:
            # Get actual NSSF deduction from payslip
            total_nssf += payslip.nssf_deduction or Decimal('0.00')
            
            # Get pension contributions from voluntary deductions
            pension_deductions = PayslipDeduction.objects.filter(
                payslip=payslip,
                deduction_type__icontains='pension',
                is_statutory=False
            )
            
            for pension_deduction in pension_deductions:
                total_pension += pension_deduction.amount or Decimal('0.00')
        
        p9_report.retirement_actual = total_nssf + total_pension
        
        # E3: Fixed amount (30,000 per month = 360,000 per year)
        months_worked = len([m for m in monthly_data.keys() if monthly_data[m]['basic_salary'] > 0])
        p9_report.retirement_fixed_cap = Decimal('30000.00') * months_worked
        
        # Calculate other required fields
        p9_report.calculate_totals()
        p9_report.save()
        
        # Create/update monthly breakdown
        self._create_monthly_breakdown(p9_report, monthly_data)
        
        return p9_report

    def _generate_empty_p9(self, employee, p9_report=None):
        """Generate empty P9 report template"""
        
        if p9_report is None:
            p9_report, created = P9Report.objects.get_or_create(
                employee=employee,
                tax_year=self.tax_year,
                defaults={
                    'generated_by': None,
                    'status': 'draft'
                }
            )
        
        # Set basic information
        p9_report.employee_name = f"{employee.user.first_name} {employee.user.last_name}"
        p9_report.save()
        
        return p9_report

    def _create_monthly_breakdown(self, p9_report, monthly_data):
        """Create monthly breakdown records"""
        
        # Delete existing monthly data
        p9_report.monthly_breakdown.all().delete()
        
        # Get payslips to calculate actual monthly retirement contributions
        payslips = Payslip.objects.filter(
            employee=p9_report.employee,
            payroll_run__period_start_date__year=p9_report.tax_year
        ).select_related('payroll_run')
        
        # Create payslip lookup by month
        payslip_by_month = {}
        for payslip in payslips:
            month = payslip.payroll_run.period_start_date.month
            payslip_by_month[month] = payslip
        
        # Create new monthly records
        for month, data in monthly_data.items():
            # Get actual payslip for this month
            payslip = payslip_by_month.get(month)
            
            # Calculate retirement contributions for this month
            basic_salary = data['basic_salary']
            
            # E1: 30% of Basic Salary
            e1_monthly = basic_salary * Decimal('0.30')
            
            # E2: Actual contributions (NSSF + Pension from payslip)
            e2_monthly = Decimal('0.00')
            if payslip:
                # Get NSSF from payslip
                e2_monthly += payslip.nssf_deduction or Decimal('0.00')
                
                # Get pension contributions from voluntary deductions
                pension_deductions = PayslipDeduction.objects.filter(
                    payslip=payslip,
                    deduction_type__icontains='pension',
                    is_statutory=False
                )
                
                for pension_deduction in pension_deductions:
                    e2_monthly += pension_deduction.amount or Decimal('0.00')
            
            # E3: Fixed amount
            e3_monthly = Decimal('30000.00')
            
            # Calculate effective retirement (lower of E1, E2, E3) for monthly deductions
            effective_retirement_monthly = min(e1_monthly, e2_monthly, e3_monthly)
            
            P9MonthlyBreakdown.objects.create(
                p9_report=p9_report,
                month=month,
                basic_salary=data['basic_salary'],
                gross_pay=data['gross_pay'],
                paye_tax=data['paye_tax'],
                ahl=data['ahl'],
                shif=data['shif'],
                benefits_non_cash=data.get('benefits', Decimal('0.00')),
                personal_relief=Decimal('2400.00'),  # Standard monthly relief
                retirement_30_percent_monthly=e1_monthly,
                retirement_actual_monthly=e2_monthly,
                retirement_fixed_monthly=e3_monthly,
                retirement_contribution=effective_retirement_monthly  # Use lower of E1, E2, E3
            )

    def generate_bulk_pdfs(self, p9_reports=None, create_zip=True):
        """
        Generate PDF files for multiple P9 reports
        
        Args:
            p9_reports: QuerySet of P9Report objects (None = all for current year)
            create_zip: Whether to create a zip file of all PDFs
            
        Returns:
            dict: Results with file paths and download info
        """
        
        if p9_reports is None:
            p9_reports = P9Report.objects.filter(tax_year=self.tax_year)
        
        results = {
            'total_reports': p9_reports.count(),
            'generated_pdfs': 0,
            'failed_pdfs': 0,
            'pdf_files': [],
            'zip_file': None,
            'errors': []
        }
        
        # Create directory for PDFs
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'p9_reports', str(self.tax_year))
        os.makedirs(pdf_dir, exist_ok=True)
        
        pdf_files = []
        
        for p9_report in p9_reports:
            try:
                # Generate PDF
                pdf_path = self.pdf_generator.save_pdf_file(p9_report, pdf_dir)
                pdf_files.append(pdf_path)
                results['generated_pdfs'] += 1
                results['pdf_files'].append({
                    'employee_name': p9_report.employee_name,
                    'file_path': pdf_path,
                    'file_size': os.path.getsize(pdf_path)
                })
                
            except Exception as e:
                results['failed_pdfs'] += 1
                error_msg = f"PDF for {p9_report.employee_name}: {str(e)}"
                results['errors'].append(error_msg)
        
        # Create ZIP file if requested
        if create_zip and pdf_files:
            zip_path = os.path.join(pdf_dir, f'P9_Reports_{self.tax_year}_All.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for pdf_file in pdf_files:
                    zipf.write(pdf_file, os.path.basename(pdf_file))
            
            results['zip_file'] = {
                'path': zip_path,
                'size': os.path.getsize(zip_path),
                'file_count': len(pdf_files)
            }
        
        return results

    def get_payslip_summary(self, employee_id=None, tax_year=None):
        """Get summary of available payslip data for P9 generation"""
        
        year = tax_year or self.tax_year
        
        # Use payroll_run date fields since Payslip doesn't have direct date fields
        payslips_query = Payslip.objects.filter(payroll_run__run_date__year=year)
        if employee_id:
            payslips_query = payslips_query.filter(employee_id=employee_id)
        
        # Group by employee
        summary = {}
        for payslip in payslips_query.select_related('employee__user', 'payroll_run'):
            emp_id = payslip.employee.id
            emp_name = f"{payslip.employee.user.first_name} {payslip.employee.user.last_name}"
            
            if emp_id not in summary:
                summary[emp_id] = {
                    'employee_name': emp_name,
                    'payslip_count': 0,
                    'months_covered': set(),
                    'total_gross': Decimal('0.00'),
                    'total_paye': Decimal('0.00'),
                    'has_complete_year': False
                }
            
            summary[emp_id]['payslip_count'] += 1
            summary[emp_id]['months_covered'].add(payslip.payroll_run.run_date.month)
            summary[emp_id]['total_gross'] += payslip.total_gross_income or Decimal('0.00')
            summary[emp_id]['total_paye'] += payslip.paye_tax or Decimal('0.00')
        
        # Check for complete year coverage
        for emp_data in summary.values():
            emp_data['has_complete_year'] = len(emp_data['months_covered']) == 12
            emp_data['months_covered'] = sorted(list(emp_data['months_covered']))
        
        return summary

    def validate_p9_data(self, p9_report):
        """Validate P9 report data for accuracy"""
        
        validation_errors = []
        
        # Check basic calculations
        expected_gross = (p9_report.total_basic_salary + 
                         p9_report.total_benefits_non_cash + 
                         p9_report.total_value_of_quarters)
        
        if abs(expected_gross - p9_report.total_gross_pay) > Decimal('0.01'):
            validation_errors.append("Gross pay calculation error")
        
        # Check AHL calculation (1.5%)
        expected_ahl = p9_report.total_gross_pay * Decimal('0.015')
        if abs(expected_ahl - p9_report.total_ahl) > Decimal('0.01'):
            validation_errors.append("AHL calculation error")
        
        # Check chargeable pay
        expected_chargeable = p9_report.total_gross_pay - p9_report.total_deductions
        if abs(expected_chargeable - p9_report.chargeable_pay) > Decimal('0.01'):
            validation_errors.append("Chargeable pay calculation error")
        
        # Check if monthly breakdown matches totals
        monthly_total_gross = sum(
            breakdown.gross_pay for breakdown in p9_report.monthly_breakdown.all()
        )
        if abs(monthly_total_gross - p9_report.total_gross_pay) > Decimal('0.01'):
            validation_errors.append("Monthly breakdown doesn't match annual totals")
        
        return validation_errors
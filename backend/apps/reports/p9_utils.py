"""
P9 Report Generation Utilities
Handles automatic P9 generation from payslip data
"""

from decimal import Decimal
from django.db.models import Sum
from apps.payroll.models import Payslip
from apps.reports.models import P9Report, P9MonthlyBreakdown


class P9Generator:
    """Service class for generating P9 reports from payslip data"""
    
    def __init__(self, employee, tax_year):
        self.employee = employee
        self.tax_year = tax_year
        self.payslips = None
    
    def generate_p9_report(self, created_by=None):
        """
        Generate complete P9 report from payslip data
        Returns: P9Report instance
        """
        # Get or create P9 report
        p9_report, created = P9Report.objects.get_or_create(
            employee=self.employee,
            tax_year=self.tax_year,
            defaults={'generated_by': created_by}
        )
        
        if not created:
            # Clear existing data for regeneration
            p9_report.monthly_breakdown.all().delete()
        
        # Get payslips for the year
        self.payslips = Payslip.objects.filter(
            employee=self.employee,
            pay_date__year=self.tax_year
        ).order_by('pay_date')
        
        if not self.payslips.exists():
            raise ValueError(f"No payslips found for {self.employee} in {self.tax_year}")
        
        # Populate P9 from payslip data
        self._populate_annual_totals(p9_report)
        self._create_monthly_breakdown(p9_report)
        
        # Calculate all derived fields
        p9_report.calculate_totals()
        p9_report.status = 'generated'
        p9_report.save()
        
        return p9_report
    
    def _populate_annual_totals(self, p9_report):
        """Populate annual totals from payslip aggregation"""
        
        # Aggregate payslip data
        totals = self.payslips.aggregate(
            total_basic=Sum('basic_salary'),
            total_gross=Sum('gross_salary'),
            total_ahl=Sum('ahl_deduction'),
            total_shif=Sum('shif_deduction'),
            total_paye=Sum('paye_tax'),
            total_personal_relief=Sum('personal_relief'),
            total_insurance_relief=Sum('insurance_relief')
        )
        
        # Map to P9 fields
        p9_report.total_basic_salary = totals['total_basic'] or Decimal('0.00')
        p9_report.total_gross_pay = totals['total_gross'] or Decimal('0.00')
        p9_report.total_ahl = totals['total_ahl'] or Decimal('0.00')
        p9_report.total_shif = totals['total_shif'] or Decimal('0.00')
        p9_report.total_paye_tax = totals['total_paye'] or Decimal('0.00')
        p9_report.total_personal_relief = totals['total_personal_relief'] or Decimal('28800.00')
        p9_report.total_insurance_relief = totals['total_insurance_relief'] or Decimal('0.00')
        
        # Set defaults for fields not in current payslips
        if not p9_report.total_benefits_non_cash:
            p9_report.total_benefits_non_cash = Decimal('0.00')
        if not p9_report.total_value_of_quarters:
            p9_report.total_value_of_quarters = Decimal('0.00')
        if not p9_report.retirement_actual:
            p9_report.retirement_actual = Decimal('0.00')
        if not p9_report.total_prmf:
            p9_report.total_prmf = Decimal('0.00')
        if not p9_report.total_owner_occupied_interest:
            p9_report.total_owner_occupied_interest = Decimal('0.00')
    
    def _create_monthly_breakdown(self, p9_report):
        """Create monthly breakdown records from payslips"""
        
        monthly_breakdowns = []
        
        for payslip in self.payslips:
            breakdown = P9MonthlyBreakdown(
                p9_report=p9_report,
                month=payslip.pay_date.month,
                basic_salary=payslip.basic_salary,
                gross_pay=payslip.gross_salary,
                ahl=payslip.ahl_deduction or Decimal('0.00'),
                shif=payslip.shif_deduction or Decimal('0.00'),
                paye_tax=payslip.paye_tax,
                personal_relief=payslip.personal_relief,
                insurance_relief=payslip.insurance_relief or Decimal('0.00')
            )
            
            # Calculate monthly derived fields
            breakdown.total_deductions = (
                breakdown.ahl + 
                breakdown.shif + 
                breakdown.prmf + 
                breakdown.retirement_contribution + 
                breakdown.owner_occupied_interest
            )
            
            breakdown.chargeable_pay = breakdown.gross_pay - breakdown.total_deductions
            breakdown.tax_charged = self._calculate_monthly_tax(breakdown.chargeable_pay)
            
            monthly_breakdowns.append(breakdown)
        
        # Bulk create monthly breakdowns
        P9MonthlyBreakdown.objects.bulk_create(monthly_breakdowns)
    
    def _calculate_monthly_tax(self, monthly_chargeable_pay):
        """Calculate monthly PAYE tax using Kenya tax brackets"""
        if monthly_chargeable_pay <= 0:
            return Decimal('0.00')
        
        # 2024 Kenya Tax Brackets (monthly)
        monthly_brackets = [
            (24000, Decimal('0.10')),     # Up to KES 24,000 at 10%
            (8333, Decimal('0.25')),      # Next KES 8,333 at 25% (100k annual / 12)
            (float('inf'), Decimal('0.30'))  # Above at 30%
        ]
        
        tax = Decimal('0.00')
        remaining = monthly_chargeable_pay
        
        for bracket_limit, rate in monthly_brackets:
            if remaining <= 0:
                break
            
            taxable_in_bracket = min(remaining, Decimal(str(bracket_limit)))
            tax += taxable_in_bracket * rate
            remaining -= taxable_in_bracket
        
        return tax
    
    @staticmethod
    def generate_bulk_p9_reports(tax_year, employees=None, created_by=None):
        """
        Generate P9 reports for multiple employees
        Args:
            tax_year: Year to generate reports for
            employees: List of employees (if None, generates for all with payslips)
            created_by: User who initiated the generation
        Returns:
            Dict with success/error counts and details
        """
        from apps.employees.models import Employee
        
        if employees is None:
            # Get all employees who have payslips for the year
            employees = Employee.objects.filter(
                payslips__pay_date__year=tax_year
            ).distinct()
        
        results = {
            'success_count': 0,
            'error_count': 0,
            'generated_reports': [],
            'errors': []
        }
        
        for employee in employees:
            try:
                generator = P9Generator(employee, tax_year)
                p9_report = generator.generate_p9_report(created_by=created_by)
                
                results['success_count'] += 1
                results['generated_reports'].append(p9_report)
                
            except Exception as e:
                results['error_count'] += 1
                results['errors'].append({
                    'employee': str(employee),
                    'error': str(e)
                })
        
        return results


class P9Validator:
    """Utility class for validating P9 report data"""
    
    @staticmethod
    def validate_p9_report(p9_report):
        """
        Validate P9 report for completeness and accuracy
        Returns: Dict with validation results
        """
        errors = []
        warnings = []
        
        # Required field validation
        if not p9_report.employee_pin:
            errors.append("Employee KRA PIN is required")
        
        if not p9_report.employer_pin:
            warnings.append("Employer KRA PIN is missing")
        
        if p9_report.total_basic_salary <= 0:
            errors.append("Basic salary must be greater than zero")
        
        # Calculation validation
        expected_gross = (
            p9_report.total_basic_salary +
            p9_report.total_benefits_non_cash +
            p9_report.total_value_of_quarters
        )
        
        if abs(p9_report.total_gross_pay - expected_gross) > Decimal('0.01'):
            errors.append(f"Gross pay calculation mismatch: Expected {expected_gross}, got {p9_report.total_gross_pay}")
        
        # AHL calculation validation
        expected_ahl = p9_report.total_gross_pay * Decimal('0.015')
        if abs(p9_report.total_ahl - expected_ahl) > Decimal('0.01'):
            warnings.append(f"AHL calculation may be incorrect: Expected {expected_ahl}, got {p9_report.total_ahl}")
        
        # Retirement contribution validation
        max_retirement = min(
            p9_report.retirement_30_percent,
            p9_report.retirement_fixed_cap
        )
        
        if p9_report.retirement_actual > max_retirement:
            warnings.append("Retirement contribution exceeds allowable limits")
        
        # Personal relief validation
        expected_personal_relief = Decimal('28800.00')  # KES 2,400 * 12 months
        if p9_report.total_personal_relief != expected_personal_relief:
            warnings.append(f"Personal relief should be {expected_personal_relief} per year")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'completeness_score': p9_report.is_complete
        }
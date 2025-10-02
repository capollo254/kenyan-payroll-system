# apps/reports/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class ReportGenerationLog(models.Model):
    """
    A log of generated reports, to be used for an audit trail and download history.
    """
    REPORT_TYPES = (
        ('payslip', 'Payslip Report'),
        ('nssf', 'NSSF Report'),
        ('nhif', 'NHIF Report'),
        ('paye', 'PAYE Report'),
        ('p9', 'P9 Tax Report'),
        ('general', 'General Report'),
    )

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    file_path = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.get_report_type_display()} generated on {self.generation_date.strftime('%Y-%m-%d')}"


class P9Report(models.Model):
    """
    P9 Tax Deduction Card - KRA Annual Tax Report
    Based on Kenya Revenue Authority P9 Form template
    """
    
    # Basic Information
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='p9_reports')
    tax_year = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2050)],
        help_text="Tax year for this P9 report"
    )
    
    # Company Information (from employee's company)
    employer_name = models.CharField(max_length=200, blank=True)
    employer_pin = models.CharField(max_length=20, blank=True, help_text="Employer's KRA PIN")
    
    # Employee Information
    employee_name = models.CharField(max_length=200)
    employee_main_name = models.CharField(max_length=100, blank=True)
    employee_other_names = models.CharField(max_length=100, blank=True) 
    employee_pin = models.CharField(max_length=20, blank=True, help_text="Employee's KRA PIN")
    
    # P9 COLUMNS - Annual Totals
    
    # Column A: Basic Salary
    total_basic_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column A - Total Basic Salary for the year"
    )
    
    # Column B: Benefits Non-Cash
    total_benefits_non_cash = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column B - Total Benefits Non-Cash (company car, housing, etc.)"
    )
    
    # Column C: Value of Quarters
    total_value_of_quarters = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column C - Value of accommodation provided by employer"
    )
    
    # Column D: Total Gross Pay
    total_gross_pay = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column D - Total Gross Pay (A+B+C)"
    )
    
    # Column E: Defined Contribution Retirement Scheme (3 sub-columns)
    # E1: 30% of Basic Salary
    retirement_30_percent = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column E1 - 30% of Basic Salary"
    )
    
    # E2: Actual contributions made
    retirement_actual = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column E2 - Actual retirement contributions made"
    )
    
    # E3: Fixed amount (30,000 per month cap)
    retirement_fixed_cap = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('360000.00'),
        help_text="Column E3 - Fixed annual cap (KES 360,000)"
    )
    
    # Column F: Affordable Housing Levy (AHL) - 1.5% of gross pay
    total_ahl = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column F - Affordable Housing Levy (1.5% of gross pay)"
    )
    
    # Column G: Social Health Insurance Fund (SHIF)
    total_shif = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column G - Social Health Insurance Fund"
    )
    
    # Column H: Post Retirement Medical Fund (PRMF)
    total_prmf = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column H - Post Retirement Medical Fund"
    )
    
    # Column I: Owner Occupied Interest
    total_owner_occupied_interest = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column I - Owner Occupied mortgage interest"
    )
    
    # Column J: Total Deductions (Lower of E+F+G+H+I)
    total_deductions = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column J - Total allowable deductions"
    )
    
    # Column K: Chargeable Pay (D-J)
    chargeable_pay = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column K - Chargeable Pay (Gross Pay - Deductions)"
    )
    
    # Column L: Tax Charged
    tax_charged = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column L - Tax charged on chargeable pay"
    )
    
    # Column M: Personal Relief
    total_personal_relief = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('28800.00'),
        help_text="Column M - Personal Relief (KES 2,400 per month)"
    )
    
    # Column N: Insurance Relief
    total_insurance_relief = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column N - Insurance Relief"
    )
    
    # Column O: PAYE Tax (L-M-N)
    total_paye_tax = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        help_text="Column O - PAYE Tax (Tax Charged - Personal Relief - Insurance Relief)"
    )
    
    # System fields
    generated_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('issued', 'Issued to Employee'),
        ('submitted', 'Submitted to KRA'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Notes and comments
    notes = models.TextField(blank=True, help_text="Internal notes about this P9")
    
    class Meta:
        unique_together = ['employee', 'tax_year']
        ordering = ['-tax_year', 'employee__user__first_name']
        verbose_name = "P9 Tax Report"
        verbose_name_plural = "P9 Tax Reports"
    
    def __str__(self):
        return f"P9 {self.tax_year} - {self.employee_name}"
    
    def save(self, *args, **kwargs):
        # Auto-populate employee information
        if self.employee:
            self.employee_name = f"{self.employee.user.first_name} {self.employee.user.last_name}"
            self.employee_main_name = self.employee.user.last_name
            self.employee_other_names = self.employee.user.first_name
            
            # Get KRA PIN from JobInformation model
            try:
                self.employee_pin = self.employee.job_info.kra_pin or ''
            except AttributeError:
                self.employee_pin = ''
            
            # Get company information from CompanySettings
            from apps.core.company_models import CompanySettings
            company_settings = CompanySettings.get_settings()
            self.employer_name = company_settings.company_name
            self.employer_pin = company_settings.kra_pin or ''
        
        super().save(*args, **kwargs)
    
    @property
    def is_complete(self):
        """Check if all required fields are populated"""
        required_fields = [
            self.total_basic_salary,
            self.total_gross_pay,
            self.chargeable_pay,
            self.total_paye_tax
        ]
        return all(field > 0 for field in required_fields)
    
    @property
    def effective_retirement_deduction(self):
        """Calculate the effective retirement deduction (lower of actual or caps)"""
        return min(
            self.retirement_actual,
            self.retirement_30_percent,
            self.retirement_fixed_cap
        )
    
    def calculate_totals(self):
        """Calculate all derived fields based on basic inputs"""
        # Column D: Total Gross Pay
        self.total_gross_pay = (
            self.total_basic_salary + 
            self.total_benefits_non_cash + 
            self.total_value_of_quarters
        )
        
        # Column E1: 30% of Basic Salary
        self.retirement_30_percent = self.total_basic_salary * Decimal('0.30')
        
        # Column F: AHL (1.5% of gross pay)
        self.total_ahl = self.total_gross_pay * Decimal('0.015')
        
        # Column J: Total Deductions
        effective_retirement = self.effective_retirement_deduction
        self.total_deductions = (
            effective_retirement +
            self.total_ahl +
            self.total_shif +
            self.total_prmf +
            self.total_owner_occupied_interest
        )
        
        # Column K: Chargeable Pay
        self.chargeable_pay = self.total_gross_pay - self.total_deductions
        
        # Column L: Tax Charged (would need tax brackets)
        self.tax_charged = self._calculate_tax_on_chargeable_pay()
        
        # Column O: PAYE Tax
        self.total_paye_tax = max(
            Decimal('0.00'),
            self.tax_charged - self.total_personal_relief - self.total_insurance_relief
        )
        
        return self
    
    def _calculate_tax_on_chargeable_pay(self):
        """Calculate tax using Kenya tax brackets"""
        if self.chargeable_pay <= 0:
            return Decimal('0.00')
        
        # 2024 Kenya Tax Brackets (annual)
        brackets = [
            (288000, Decimal('0.10')),    # Up to KES 288,000 at 10%
            (100000, Decimal('0.25')),    # Next KES 100,000 at 25% 
            (float('inf'), Decimal('0.30'))  # Above KES 388,000 at 30%
        ]
        
        tax = Decimal('0.00')
        remaining = self.chargeable_pay
        
        for bracket_limit, rate in brackets:
            if remaining <= 0:
                break
            
            taxable_in_bracket = min(remaining, Decimal(str(bracket_limit)))
            tax += taxable_in_bracket * rate
            remaining -= taxable_in_bracket
        
        return tax


class P9MonthlyBreakdown(models.Model):
    """
    Monthly breakdown data for P9 report
    Links to the main P9Report and stores month-by-month details
    """
    
    p9_report = models.ForeignKey(P9Report, on_delete=models.CASCADE, related_name='monthly_breakdown')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    
    # Monthly values for each P9 column
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    benefits_non_cash = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    value_of_quarters = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Retirement contribution breakdown (E1, E2, E3)
    retirement_30_percent_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="E1: 30% of Basic Salary")
    retirement_actual_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="E2: Actual contributions (NSSF + Pension)")
    retirement_fixed_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('30000.00'), help_text="E3: Fixed amount (30,000)")
    
    retirement_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ahl = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shif = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    prmf = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    owner_occupied_interest = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    chargeable_pay = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_charged = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    personal_relief = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2400.00'))
    insurance_relief = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paye_tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        unique_together = ['p9_report', 'month']
        ordering = ['p9_report', 'month']
        verbose_name = "P9 Monthly Breakdown"
        verbose_name_plural = "P9 Monthly Breakdowns"
    
    def __str__(self):
        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return f"{self.p9_report.employee_name} - {month_names[self.month]} {self.p9_report.tax_year}"
# apps/employees/models.py

from django.db import models
from django.conf import settings
from decimal import Decimal

class Employee(models.Model):
    """
    Core employee profile containing general and payroll-specific information.
    Personal details are kept on the User model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    # Fields from the user's original Employee model
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    helb_monthly_deduction = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Fields from the user's original JobInformation model
    company_employee_id = models.CharField(max_length=50, unique=True, help_text="Company-assigned employee ID", null=True, blank=True)
    kra_pin = models.CharField(max_length=20, unique=True, help_text="Kenya Revenue Authority PIN", null=True, blank=True)
    nssf_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nhif_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)

    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def __str__(self):
        return self.full_name()
class JobInformation(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='job_info')
    company_employee_id = models.CharField(max_length=50, unique=True, help_text="Company-assigned employee ID")
    kra_pin = models.CharField(max_length=20, unique=True, help_text="Kenya Revenue Authority PIN")
    nssf_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nhif_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.employee.full_name()} - {self.position}"

class VoluntaryDeduction(models.Model):
    """
    Represents an optional deduction from an employee's salary.
    """
    DEDUCTION_TYPES = (
        ('sacco', 'Sacco Contribution'),
        ('loan', 'Check-off Loan'),
        ('other', 'Other'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='voluntary_deductions')
    deduction_type = models.CharField(max_length=50, choices=DEDUCTION_TYPES)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.employee.full_name()}'s {self.get_deduction_type_display()}"
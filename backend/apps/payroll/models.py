from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

from apps.employees.models import Employee

class PayrollRun(models.Model):
    run_date = models.DateField(default=timezone.now)
    run_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='payroll_runs')
    period_start_date = models.DateField()
    period_end_date = models.DateField()
    total_net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"Payroll Run for {self.period_start_date} to {self.period_end_date}"

    class Meta:
        ordering = ['-run_date']
        verbose_name_plural = "Payroll Runs"

class Payslip(models.Model):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='payslips')
    
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_gross_income = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    paye_tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    nssf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shif_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ahl_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    helb_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"Payslip for {self.employee.user.first_name} {self.employee.user.last_name} ({self.payroll_run.run_date})"

    class Meta:
        ordering = ['-payroll_run__run_date', 'employee__user__first_name']

class PayslipDeduction(models.Model):
    payslip = models.ForeignKey(Payslip, on_delete=models.CASCADE, related_name='deduction_items')
    deduction_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_statutory = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.deduction_type} on {self.payslip}"

    class Meta:
        verbose_name_plural = "Payslip Deductions"
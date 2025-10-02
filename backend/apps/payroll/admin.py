# apps/payroll/admin.py

from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import PayrollRun, Payslip, PayslipDeduction
from apps.employees.models import Employee, VoluntaryDeduction

# Import the calculation functions
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl
from apps.compliance.calc_overtime import calculate_overtime_pay
from apps.compliance.calc_reliefs import (
    calculate_insurance_relief,
    calculate_post_retirement_medical_deduction,
    calculate_mortgage_interest_relief
)

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ('run_date', 'period_start_date', 'period_end_date', 'run_by', 'payslip_count')
    list_filter = ('run_date',)
    search_fields = ('run_by__email',)
    readonly_fields = ('total_net_pay', 'total_deductions')
    
    def payslip_count(self, obj):
        """Display the number of payslips generated for this run"""
        return obj.payslips.count()
    payslip_count.short_description = 'Payslips Generated'
    
    def save_model(self, request, obj, form, change):
        """Override save to automatically generate payslips when payroll run is saved"""
        
        # Set the run_by field to the current user if not already set
        if not obj.run_by:
            obj.run_by = request.user
            
        # Save the payroll run first
        super().save_model(request, obj, form, change)
        
        # Generate payslips if this is a new payroll run or if no payslips exist
        if not change or obj.payslips.count() == 0:
            self.generate_payslips(request, obj)
    
    @transaction.atomic
    def generate_payslips(self, request, payroll_run):
        """Generate payslips for all active employees"""
        try:
            employees = Employee.objects.filter(is_active=True)
            if not employees.exists():
                messages.warning(request, "No active employees found to generate payslips.")
                return
            
            payslips_created = 0
            total_net_pay = Decimal('0.00')
            total_deductions = Decimal('0.00')
            
            for employee in employees:
                # Check if payslip already exists for this employee and payroll run
                if Payslip.objects.filter(payroll_run=payroll_run, employee=employee).exists():
                    continue
                    
                gross_salary = employee.gross_salary
                
                # Default overtime to 0 since we can't get this from admin interface
                overtime_pay = Decimal('0.00')
                total_gross_income = gross_salary + overtime_pay
                
                # --- BEGIN PAYROLL CALCULATION LOGIC ---
                nssf_deduction = calculate_nssf(total_gross_income)
                shif_deduction = calculate_shif(total_gross_income)
                ahl_employee_deduction, ahl_employer_contribution = calculate_ahl(total_gross_income)
                helb_deduction = employee.helb_monthly_deduction if employee.helb_monthly_deduction else Decimal('0.00')
                
                # Calculate pension deduction (if any) with KRA relief cap
                PENSION_MAX_RELIEF = Decimal('30000.00')
                pension_deduction = Decimal('0.00')
                pension_deductions = employee.voluntary_deductions.filter(
                    deduction_type__icontains='pension',
                    is_active=True
                )
                for pension in pension_deductions:
                    pension_deduction += pension.amount
                
                # Apply the tax-deductible cap of KES 30,000 per month for tax calculation
                pension_relief_amount = min(pension_deduction, PENSION_MAX_RELIEF)
                
                # Calculate additional reliefs as per KRA PAYE document
                medical_fund_deduction = calculate_post_retirement_medical_deduction(
                    employee.monthly_medical_fund_contribution
                )
                mortgage_interest_relief = calculate_mortgage_interest_relief(
                    employee.monthly_mortgage_interest
                )
                
                # FIXED: Calculate taxable income (total gross - all pre-tax deductions)
                # Include NSSF, SHIF, AHL, pension contributions (capped), medical fund, and mortgage interest
                taxable_income = total_gross_income - (
                    nssf_deduction + 
                    shif_deduction + 
                    ahl_employee_deduction + 
                    pension_relief_amount +
                    medical_fund_deduction +
                    mortgage_interest_relief
                )
                taxable_income = max(taxable_income, Decimal('0.00'))
                
                paye_tax = calculate_paye(taxable_income)
                
                # Calculate insurance relief (reduces PAYE tax)
                insurance_relief = calculate_insurance_relief(employee.monthly_insurance_premiums)
                paye_tax_after_relief = max(paye_tax - insurance_relief, Decimal('0.00'))
                
                # FIXED: Calculate voluntary deductions (excluding pension to avoid double counting)
                # Pension is already deducted from taxable income, so don't include it again
                voluntary_deductions_total = Decimal('0.00')
                voluntary_deductions = employee.voluntary_deductions.filter(is_active=True).exclude(deduction_type__icontains='pension')
                for deduction in voluntary_deductions:
                    voluntary_deductions_total += deduction.amount
                
                total_statutory_deductions = paye_tax_after_relief + nssf_deduction + shif_deduction + ahl_employee_deduction + helb_deduction
                
                # Total deductions = statutory + voluntary (excluding pension) + actual pension amount for display
                # Note: Use full pension_deduction amount for total deductions, not the capped relief amount
                total_deductions_emp = total_statutory_deductions + voluntary_deductions_total + pension_deduction
                net_pay = total_gross_income - total_deductions_emp
                
                # --- Create Payslip Record ---
                payslip = Payslip.objects.create(
                    payroll_run=payroll_run,
                    employee=employee,
                    gross_salary=gross_salary,
                    overtime_pay=overtime_pay,
                    total_gross_income=total_gross_income,
                    paye_tax=paye_tax,
                    nssf_deduction=nssf_deduction,
                    shif_deduction=shif_deduction,
                    ahl_deduction=ahl_employee_deduction,
                    helb_deduction=helb_deduction,
                    total_deductions=total_deductions_emp,
                    net_pay=net_pay
                )
                
                # Create individual deduction records for the payslip
                if paye_tax > 0:
                    PayslipDeduction.objects.create(payslip=payslip, deduction_type='PAYE Tax', amount=paye_tax, is_statutory=True)
                if nssf_deduction > 0:
                    PayslipDeduction.objects.create(payslip=payslip, deduction_type='NSSF', amount=nssf_deduction, is_statutory=True)
                if shif_deduction > 0:
                    PayslipDeduction.objects.create(payslip=payslip, deduction_type='SHIF', amount=shif_deduction, is_statutory=True)
                if ahl_employee_deduction > 0:
                    PayslipDeduction.objects.create(payslip=payslip, deduction_type='AHL', amount=ahl_employee_deduction, is_statutory=True)
                if helb_deduction > 0:
                    PayslipDeduction.objects.create(payslip=payslip, deduction_type='HELB', amount=helb_deduction, is_statutory=True)
                
                # Create pension deduction records
                for pension in pension_deductions:
                    PayslipDeduction.objects.create(
                        payslip=payslip,
                        deduction_type=pension.deduction_type,
                        amount=pension.amount,
                        is_statutory=False
                    )
                
                # Create other voluntary deduction records (excluding pension)
                for deduction in voluntary_deductions:
                    PayslipDeduction.objects.create(
                        payslip=payslip,
                        deduction_type=deduction.deduction_type,
                        amount=deduction.amount,
                        is_statutory=False
                    )
                
                total_net_pay += net_pay
                total_deductions += total_deductions_emp
                payslips_created += 1
            
            # Update payroll run totals
            payroll_run.total_net_pay = total_net_pay
            payroll_run.total_deductions = total_deductions
            payroll_run.save(update_fields=['total_net_pay', 'total_deductions'])
            
            messages.success(request, f"Successfully generated {payslips_created} payslips for payroll run.")
            
        except Exception as e:
            messages.error(request, f"Error generating payslips: {str(e)}")
            # Re-raise the exception to ensure the transaction is rolled back
            raise

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll_run', 'total_gross_income', 'total_deductions', 'net_pay')
    list_filter = ('payroll_run', 'payroll_run__run_date')
    search_fields = ('employee__user__email', 'employee__user__first_name', 'employee__user__last_name')
    readonly_fields = ('gross_salary', 'overtime_pay', 'total_gross_income', 'paye_tax', 
                      'nssf_deduction', 'shif_deduction', 'ahl_deduction', 'helb_deduction',
                      'total_deductions', 'net_pay')

@admin.register(PayslipDeduction)
class PayslipDeductionAdmin(admin.ModelAdmin):
    list_display = ('payslip', 'deduction_type', 'amount', 'is_statutory')
    list_filter = ('deduction_type', 'is_statutory')
    search_fields = ('payslip__employee__user__email',)
    search_fields = ('payslip__employee__user__email',)
# apps/employees/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Employee, JobInformation, VoluntaryDeduction, EmployeeBenefit

class JobInformationInline(admin.StackedInline):
    model = JobInformation
    can_delete = False
    verbose_name_plural = 'Job Information'

class VoluntaryDeductionInline(admin.TabularInline):
    model = VoluntaryDeduction
    extra = 1

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'is_active',
        'job_info_department',
        'job_info_position',
        'gross_salary',
        'banking_status',
        'view_employee_link'
    )
    list_filter = (
        'is_active',
        'job_info__department',
        'job_info__position'
    )
    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__email',
        'job_info__company_employee_id'
    )
    
    inlines = [JobInformationInline, VoluntaryDeductionInline]

    fieldsets = (
        ('Personal Information', {
            'fields': (('user', 'is_active'),)
        }),
        ('Payroll Information', {
            'fields': ('gross_salary', 'helb_monthly_deduction')
        }),
        ('Banking Information', {
            'fields': (
                ('bank_name', 'bank_code'),
                ('bank_branch', 'bank_branch_code'),
                ('account_holder_name', 'account_type'),
                'bank_account_number',
            ),
            'description': 'Complete banking details required for salary payments and direct deposits.'
        }),
        ('Mobile Money Information', {
            'fields': (
                ('mobile_money_provider', 'mobile_money_number'),
            ),
            'description': 'Optional mobile money details for alternative payment methods.',
            'classes': ('collapse',)  # Make this section collapsible
        }),
        ('KRA Tax Reliefs', {
            'fields': (
                'monthly_insurance_premiums',
                'monthly_medical_fund_contribution', 
                'monthly_mortgage_interest'
            ),
            'description': 'Tax reliefs as per KRA PAYE regulations. Insurance relief: 15% up to KSh 5,000/month. Medical fund: up to KSh 15,000/month. Mortgage interest: up to KSh 30,000/month.'
        }),
    )

    @admin.display(description='Name')
    def full_name(self, obj):
        return obj.full_name()
    
    @admin.display(description='Email')
    def email(self, obj):
        return obj.user.email

    @admin.display(description='Department')
    def job_info_department(self, obj):
        return obj.job_info.department if hasattr(obj, 'job_info') else 'N/A'
    
    @admin.display(description='Position')
    def job_info_position(self, obj):
        return obj.job_info.position if hasattr(obj, 'job_info') else 'N/A'
    
    @admin.display(description='Banking Status')
    def banking_status(self, obj):
        if obj.has_complete_banking_info():
            return format_html('<span style="color: green; font-weight: bold;">✓ Complete</span>')
        elif obj.bank_account_number:
            return format_html('<span style="color: orange; font-weight: bold;">⚠ Partial</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ Missing</span>')
    
    @admin.display(description='View Details')
    def view_employee_link(self, obj):
        return format_html(
            '<a href="/admin/employees/employee/{}/change/">View</a>',
            obj.pk
        )
    
@admin.register(JobInformation)
class JobInformationAdmin(admin.ModelAdmin):
    list_display = (
        'company_employee_id',
        'employee_name',
        'date_of_joining',
        'department',
        'position',
        'kra_pin',
    )
    list_filter = ('department', 'position', 'is_active')
    search_fields = ('employee__user__email', 'company_employee_id', 'department', 'position')

    @admin.display(description='Employee Name')
    def employee_name(self, obj):
        return obj.employee.full_name()
    
@admin.register(VoluntaryDeduction)
class VoluntaryDeductionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name', 'deduction_type', 'calculation_type', 'amount', 'start_date', 'end_date', 'is_active')
    list_filter = ('deduction_type', 'calculation_type', 'is_active')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'name', 'deduction_type')

@admin.register(EmployeeBenefit)
class EmployeeBenefitAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name', 'benefit_type', 'calculation_type', 'amount', 'is_taxable', 'is_active')
    list_filter = ('benefit_type', 'calculation_type', 'is_taxable', 'is_active')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'name', 'benefit_type')
# apps/employees/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Employee, JobInformation, VoluntaryDeduction

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'is_active',
        'department',
        'position',
        'gross_salary',
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
    
    fieldsets = (
        ('Personal Information', {
            'fields': (('user', 'is_active'),)
        }),
        ('Payroll Information', {
            'fields': ('gross_salary', 'bank_account_number', 'helb_monthly_deduction')
        }),
    )

    @admin.display(description='Name')
    def full_name(self, obj):
        return obj.full_name()
    
    @admin.display(description='Email')
    def email(self, obj):
        return obj.user.email

    @admin.display(description='Department')
    def department(self, obj):
        return obj.job_info.department if hasattr(obj, 'job_info') else 'N/A'
    
    @admin.display(description='Position')
    def position(self, obj):
        return obj.job_info.position if hasattr(obj, 'job_info') else 'N/A'
    
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
    list_display = ('employee', 'deduction_type', 'monthly_amount', 'start_date', 'end_date', 'is_active')
    list_filter = ('deduction_type', 'is_active')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'deduction_type')
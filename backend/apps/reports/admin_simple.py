from django.contrib import admin
from django.utils.html import format_html
from .models import ReportGenerationLog, P9Report, P9MonthlyBreakdown


@admin.register(ReportGenerationLog)
class ReportGenerationLogAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_by', 'generation_date', 'start_date', 'end_date')
    list_filter = ('report_type', 'generation_date')
    search_fields = ('generated_by__user__email', 'file_path')
    readonly_fields = ('generation_date',)
    date_hierarchy = 'generation_date'


class P9MonthlyBreakdownInline(admin.TabularInline):
    model = P9MonthlyBreakdown
    extra = 0
    fields = (
        'month', 'basic_salary', 'gross_pay', 'ahl', 'shif', 
        'total_deductions', 'chargeable_pay', 'paye_tax'
    )


@admin.register(P9Report)
class P9ReportAdmin(admin.ModelAdmin):
    """Django Admin interface for P9 Tax Reports"""
    
    list_display = (
        'employee_name', 'tax_year', 'total_gross_pay', 'total_paye_tax',
        'status', 'generated_date'
    )
    
    list_filter = ('tax_year', 'status', 'generated_date')
    search_fields = ('employee_name', 'employee__user__email', 'employee_pin')
    readonly_fields = ('employee_name', 'generated_date', 'updated_date')
    
    fieldsets = (
        ('Employee Information', {
            'fields': (
                'employee', 'tax_year', 'employee_name', 'employee_pin'
            )
        }),
        ('Employer Information', {
            'fields': ('employer_name', 'employer_pin')
        }),
        ('Income Totals', {
            'fields': (
                'total_basic_salary', 'total_benefits_non_cash', 
                'total_value_of_quarters', 'total_gross_pay'
            )
        }),
        ('Deductions', {
            'fields': (
                'retirement_actual', 'total_ahl', 'total_shif', 
                'total_prmf', 'total_deductions'
            )
        }),
        ('Tax Calculations', {
            'fields': (
                'chargeable_pay', 'tax_charged', 'total_personal_relief', 
                'total_insurance_relief', 'total_paye_tax'
            )
        }),
        ('Status', {
            'fields': ('status', 'notes', 'generated_by', 'generated_date')
        })
    )
    
    inlines = [P9MonthlyBreakdownInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # New P9 report
            obj.generated_by = request.user
        obj.calculate_totals()
        super().save_model(request, obj, form, change)


@admin.register(P9MonthlyBreakdown)
class P9MonthlyBreakdownAdmin(admin.ModelAdmin):
    list_display = (
        'p9_report', 'get_month_name', 'basic_salary', 'gross_pay', 
        'ahl', 'shif', 'paye_tax'
    )
    
    list_filter = ('p9_report__tax_year', 'month')
    search_fields = ('p9_report__employee_name',)
    
    def get_month_name(self, obj):
        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return month_names[obj.month]
    get_month_name.short_description = "Month"
    get_month_name.admin_order_field = 'month'
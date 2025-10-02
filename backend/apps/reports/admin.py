from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import ReportGenerationLog, P9Report, P9MonthlyBreakdown
from .bulk_p9_generator import BulkP9Generator
from .p9_pdf_generator import P9PDFGenerator
import json
from decimal import Decimal


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
    """Django Admin interface for P9 Tax Reports with auto-population and bulk generation"""
    
    list_display = (
        'employee_name', 'tax_year', 'total_gross_pay_display', 'total_paye_tax_display',
        'status', 'generated_date', 'download_pdf_link'
    )
    
    list_filter = ('tax_year', 'status', 'generated_date')
    search_fields = ('employee_name', 'employee__user__email', 'employee_pin')
    readonly_fields = ('employee_name', 'generated_date', 'updated_date', 'payroll_data_summary')
    actions = ['generate_bulk_p9', 'download_bulk_pdf']
    
    # Add custom URLs for AJAX endpoints
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate-from-payroll/', self.admin_site.admin_view(self.populate_from_payroll_ajax), 
                 name='reports_p9report_populate_payroll'),
            path('bulk-generate/', self.admin_site.admin_view(self.bulk_generate_view), 
                 name='reports_p9report_bulk_generate'),
            path('<int:object_id>/download-pdf/', self.admin_site.admin_view(self.download_pdf_view),
                 name='reports_p9report_download_pdf'),
        ]
        return custom_urls + urls
    
    def download_pdf_view(self, request, object_id):
        """Download individual P9 PDF"""
        try:
            from django.shortcuts import get_object_or_404
            p9_report = get_object_or_404(P9Report, id=object_id)
            pdf_generator = P9PDFGenerator()
            return pdf_generator.create_http_response(p9_report)
        except Exception as e:
            messages.error(request, f'PDF generation failed: {str(e)}')
            return redirect('admin:reports_p9report_changelist')
    
    fieldsets = (
        ('Employee Information', {
            'fields': (
                'employee', 'tax_year', 'employee_name', 'employee_pin', 'payroll_data_summary'
            ),
            'description': 'Select employee and tax year, then data will auto-populate from payroll records.'
        }),
        ('Auto-Population Controls', {
            'fields': (),
            'description': mark_safe(
                '<div id="auto-populate-controls">'
                '<button type="button" id="populate-btn" class="btn btn-primary">🔄 Auto-Populate from Payroll Data</button>'
                '<div id="populate-status" style="margin-top: 10px;"></div>'
                '</div>'
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

    class Media:
        js = ('admin/js/p9_auto_populate.js',)
        css = {
            'all': ('admin/css/p9_admin.css',)
        }
    
    def total_gross_pay_display(self, obj):
        return f"KES {obj.total_gross_pay:,.2f}"
    total_gross_pay_display.short_description = "Gross Pay"
    
    def total_paye_tax_display(self, obj):
        return f"KES {obj.total_paye_tax:,.2f}"
    total_paye_tax_display.short_description = "PAYE Tax"
    
    def download_pdf_link(self, obj):
        if obj.pk:
            url = reverse('admin:reports_p9report_download_pdf', args=[obj.pk])
            return format_html('<a href="{}" target="_blank" class="button">📄 Download PDF</a>', url)
        return "Save first"
    download_pdf_link.short_description = "PDF"
    
    def payroll_data_summary(self, obj):
        """Display summary of available payroll data"""
        if not obj.employee or not obj.tax_year:
            return "Select employee and tax year first"
            
        try:
            from apps.payroll.models import Payslip
            payslips = Payslip.objects.filter(
                employee=obj.employee,
                payroll_run__period_start_date__year=obj.tax_year
            )
            
            if not payslips.exists():
                return format_html(
                    '<span style="color: red;">⚠️ No payroll data found for {} in {}</span>',
                    obj.employee.full_name(), obj.tax_year
                )
            
            total_payslips = payslips.count()
            total_gross = sum(Decimal(str(p.total_gross_income or 0)) for p in payslips)
            total_paye = sum(Decimal(str(p.paye_tax or 0)) for p in payslips)
            
            return format_html(
                '<div style="background: #e8f5e8; padding: 10px; border-radius: 4px;">'
                '<strong>✅ Payroll Data Available:</strong><br/>'
                '• {} payslips found<br/>'
                '• Total Gross Pay: KES {:,.2f}<br/>'
                '• Total PAYE Tax: KES {:,.2f}<br/>'
                '<em>Click "Auto-Populate" to fill P9 fields</em>'
                '</div>',
                total_payslips, float(total_gross), float(total_paye)
            )
        except Exception as e:
            return format_html('<span style="color: red;">Error checking payroll data: {}</span>', str(e))
    
    payroll_data_summary.short_description = "Payroll Data Status"
    
    def populate_from_payroll_ajax(self, request):
        """AJAX endpoint to populate P9 fields from payroll data"""
        if request.method != 'POST':
            return JsonResponse({'error': 'POST method required'})
        
        try:
            employee_id = request.POST.get('employee_id')
            tax_year = int(request.POST.get('tax_year'))
            
            if not employee_id or not tax_year:
                return JsonResponse({'error': 'Employee and tax year required'})
            
            from apps.employees.models import Employee
            from apps.payroll.models import Payslip
            
            employee = Employee.objects.get(id=employee_id)
            payslips = Payslip.objects.filter(
                employee=employee,
                payroll_run__period_start_date__year=tax_year
            ).order_by('payroll_run__run_date')
            
            if not payslips.exists():
                return JsonResponse({'error': f'No payroll data found for {employee.full_name()} in {tax_year}'})
            
            # Calculate totals from payroll data
            # Map model fields to their actual names
            total_basic = sum(Decimal(str(p.gross_salary or 0)) for p in payslips)  # Use gross_salary as basic
            total_gross = sum(Decimal(str(p.total_gross_income or 0)) for p in payslips)
            total_paye = sum(Decimal(str(p.paye_tax or 0)) for p in payslips)
            total_nssf = sum(Decimal(str(p.nssf_deduction or 0)) for p in payslips)
            total_ahl = sum(Decimal(str(p.ahl_deduction or 0)) for p in payslips)
            total_shif = sum(Decimal(str(p.shif_deduction or 0)) for p in payslips)
            
            # Calculate monthly data for breakdown
            monthly_data = []
            for payslip in payslips:
                month = payslip.payroll_run.period_start_date.month
                monthly_data.append({
                    'month': month,
                    'basic_salary': float(payslip.gross_salary or 0),
                    'gross_pay': float(payslip.total_gross_income or 0),
                    'ahl': float(payslip.ahl_deduction or 0),
                    'shif': float(payslip.shif_deduction or 0),
                    'paye_tax': float(payslip.paye_tax or 0),
                    'total_deductions': float((payslip.nssf_deduction or 0) + (payslip.ahl_deduction or 0) + (payslip.shif_deduction or 0)),
                    'chargeable_pay': float((payslip.total_gross_income or 0) - ((payslip.nssf_deduction or 0) + (payslip.ahl_deduction or 0) + (payslip.shif_deduction or 0)))
                })
            
            # Personal relief calculation (KES 28,800 per year)
            personal_relief = Decimal('28800.00')
            insurance_relief = Decimal('0.00')  # Calculate based on actual data if available
            
            response_data = {
                'success': True,
                'data': {
                    'employee_name': employee.full_name(),
                    'employee_pin': '',  # Add if available in employee model
                    'total_basic_salary': float(total_basic),
                    'total_gross_pay': float(total_gross),
                    'total_ahl': float(total_ahl),
                    'total_shif': float(total_shif),
                    'retirement_actual': float(total_nssf),
                    'total_deductions': float(total_ahl + total_shif + total_nssf),
                    'chargeable_pay': float(total_gross - (total_ahl + total_shif + total_nssf)),
                    'total_personal_relief': float(personal_relief),
                    'total_insurance_relief': float(insurance_relief),
                    'total_paye_tax': float(total_paye),
                    'monthly_data': monthly_data,
                    'payslips_count': payslips.count()
                }
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to populate data: {str(e)}'})
    
    def bulk_generate_view(self, request):
        """View for bulk P9 generation"""
        if request.method == 'POST':
            tax_year = int(request.POST.get('tax_year'))
            employee_ids = request.POST.getlist('employees')
            
            try:
                bulk_generator = BulkP9Generator(tax_year=tax_year)
                
                if employee_ids:
                    # Generate for selected employees
                    results = bulk_generator.generate_bulk_p9(employee_ids=employee_ids)
                else:
                    # Generate for all employees with payroll data
                    results = bulk_generator.generate_bulk_p9()
                
                successful = results.get('successful_p9s', 0)
                failed = results.get('failed_p9s', 0)
                
                if successful > 0:
                    messages.success(
                        request, 
                        f'Bulk P9 generation completed! ✅ {successful} successful, ❌ {failed} failed'
                    )
                else:
                    messages.warning(request, f'No P9 reports generated. {failed} failed attempts.')
                
                # Show any specific errors
                for error in results.get('errors', []):
                    messages.error(request, f'Error: {error}')
                
                return redirect('admin:reports_p9report_changelist')
                
            except Exception as e:
                messages.error(request, f'Bulk generation failed: {str(e)}')
                return redirect('admin:reports_p9report_changelist')
        
        # GET request - show bulk generation form
        context = {
            'title': 'Bulk P9 Generation',
            'has_permission': True,
            'available_years': range(2020, 2026),
        }
        
        # Get employees with payroll data
        try:
            from apps.employees.models import Employee
            from apps.payroll.models import Payslip
            
            current_year = timezone.now().year
            # Fix the relationship - use 'payslips' (plural) as defined in the model
            employees_with_payroll = Employee.objects.filter(
                payslips__payroll_run__period_start_date__year__in=[current_year - 1, current_year]
            ).distinct().order_by('user__first_name')
            
            # If no employees found, try getting all employees
            if not employees_with_payroll.exists():
                employees_with_payroll = Employee.objects.all().order_by('user__first_name')
                messages.info(request, 'Showing all employees. Payroll data will be checked during generation.')
            
            context['employees'] = employees_with_payroll
            context['current_year'] = current_year  # Use actual current year
            context['default_tax_year'] = current_year  # Add default tax year for template
            
        except Exception as e:
            messages.error(request, f'Error loading employees: {str(e)}')
            context['employees'] = Employee.objects.all().order_by('user__first_name')
            context['current_year'] = timezone.now().year
            context['default_tax_year'] = timezone.now().year
        
        return render(request, 'admin/reports/p9report/bulk_generate.html', context)
    
    def generate_bulk_p9(self, request, queryset):
        """Admin action to generate P9 reports for selected employees"""
        tax_year = timezone.now().year  # Use current year as default
        
        try:
            # Get employee IDs from the selected P9 reports
            employee_ids = [p9.employee.id for p9 in queryset if p9.employee]
            
            if not employee_ids:
                self.message_user(request, 'No valid employees found in selection', messages.ERROR)
                return
            
            bulk_generator = BulkP9Generator(tax_year=tax_year)
            results = bulk_generator.generate_bulk_p9(employee_ids=employee_ids)
            
            successful = results.get('successful_p9s', 0)
            failed = results.get('failed_p9s', 0)
            
            if successful > 0:
                self.message_user(
                    request,
                    f'Bulk P9 generation: ✅ {successful} successful, ❌ {failed} failed',
                    messages.SUCCESS
                )
            else:
                self.message_user(request, f'No P9 reports generated. {failed} failed attempts.', messages.WARNING)
                
        except Exception as e:
            self.message_user(request, f'Bulk generation failed: {str(e)}', messages.ERROR)
    
    generate_bulk_p9.short_description = "🔄 Generate P9 from payroll data"
    
    def download_bulk_pdf(self, request, queryset):
        """Admin action to download PDFs for selected P9 reports"""
        if queryset.count() == 1:
            # Single PDF download
            p9_report = queryset.first()
            try:
                pdf_generator = P9PDFGenerator()
                response = pdf_generator.create_http_response(p9_report)
                return response
            except Exception as e:
                self.message_user(request, f'PDF generation failed: {str(e)}', messages.ERROR)
        else:
            # Multiple PDFs - redirect to bulk PDF download
            ids = ','.join(str(p.id) for p in queryset)
            return redirect(f'/admin/reports/p9report/bulk-pdf-download/?ids={ids}')
    
    download_bulk_pdf.short_description = "📄 Download PDF(s)"
    
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
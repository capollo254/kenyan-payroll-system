# apps/reports/admin.py

from django.contrib import admin
from .models import ReportGenerationLog

@admin.register(ReportGenerationLog)
class ReportGenerationLogAdmin(admin.ModelAdmin):
    list_display = (
        'report_type', 
        'generated_at', 
        'generated_by', 
        'status', 
        'file_path'
    )
    list_filter = ('report_type', 'status', 'generated_at')
    search_fields = (
        'report_type', 
        'generated_by__first_name', 
        'generated_by__last_name', 
        'generated_by__email'
    )
    readonly_fields = (
        'report_type', 
        'generated_at', 
        'generated_by', 
        'file_path', 
        'status'
    )
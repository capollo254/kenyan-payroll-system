# apps/leaves/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import LeaveType, LeaveBalance, LeaveRequest

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'annual_allocation', 'requires_approval', 'is_paid', 'is_active']
    list_filter = ['requires_approval', 'is_paid', 'is_active', 'carry_forward']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'allocated_days', 'used_days', 'pending_days', 'available_days']
    list_filter = ['leave_type', 'year']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'leave_type__name']
    ordering = ['-year', 'employee__user__last_name']
    readonly_fields = ['available_days']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 
        'status_badge', 'applied_date', 'approved_by'
    ]
    list_filter = ['status', 'leave_type', 'applied_date', 'start_date']
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name', 
        'leave_type__name', 'reason'
    ]
    ordering = ['-applied_date']
    readonly_fields = ['applied_date', 'created_at', 'updated_at', 'duration_in_days']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'reason')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by', 'approved_date', 'rejection_reason')
        }),
        ('Additional Information', {
            'fields': ('emergency_contact', 'handover_notes'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('applied_date', 'created_at', 'updated_at', 'duration_in_days'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745', 
            'rejected': '#dc3545',
            'cancelled': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        # Set approved_by and approved_date when status changes to approved
        if obj.status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
            obj.approved_date = timezone.now()
        super().save_model(request, obj, form, change)
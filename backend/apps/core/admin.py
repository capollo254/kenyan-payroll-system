from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .forms import UserChangeForm, UserCreationForm
from .models import User, CompanySettings, ContactInquiry


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    
    # Redefine the fieldsets to exclude the 'username' field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2'),
        }),
    )

    list_display = ['email', 'is_staff', 'is_superuser']
    ordering = ('email',)
    search_fields = ('email',)


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    """Admin interface for Company Settings"""
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'kra_pin', 'logo')
        }),
        ('Contact Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'postal_code', 'country', 'phone', 'email', 'website')
        }),
    )
    
    list_display = ('company_name', 'kra_pin', 'logo_preview', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    def logo_preview(self, obj):
        """Display a small preview of the logo"""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.logo.url
            )
        return "No logo uploaded"
    logo_preview.short_description = "Logo Preview"
    
    def has_add_permission(self, request):
        """Only allow one company settings instance"""
        return not CompanySettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deletion of company settings"""
        return False


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    """Admin interface for Contact Form Inquiries - Lead Management"""
    
    list_display = (
        'company_name', 'contact_name', 'email', 'phone', 'employee_count',
        'primary_interest', 'status', 'hot_lead_indicator', 'submission_date',
        'days_since_inquiry'
    )
    
    list_filter = (
        'status', 'primary_interest', 'employee_count', 'timeline', 
        'budget_range', 'industry', 'submission_date'
    )
    
    search_fields = (
        'company_name', 'contact_name', 'email', 'phone', 'industry'
    )
    
    readonly_fields = ('submission_date', 'days_since_inquiry', 'is_hot_lead')
    
    fieldsets = (
        ('Lead Status', {
            'fields': ('status', 'follow_up_date', 'notes'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('company_name', 'contact_name', 'job_title', 'email', 'phone')
        }),
        ('Company Details', {
            'fields': ('employee_count', 'industry', 'current_method')
        }),
        ('Interest & Requirements', {
            'fields': ('primary_interest', 'timeline', 'budget_range', 'specific_needs', 'newsletter')
        }),
        ('System Information', {
            'fields': ('submission_date', 'days_since_inquiry', 'is_hot_lead'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-submission_date',)
    date_hierarchy = 'submission_date'
    
    actions = ['mark_as_contacted', 'mark_as_demo_scheduled', 'mark_as_proposal_sent']
    
    def hot_lead_indicator(self, obj):
        """Visual indicator for hot leads"""
        if obj.is_hot_lead:
            return format_html(
                '<span style="color: red; font-weight: bold;">🔥 HOT</span>'
            )
        return format_html('<span style="color: gray;">-</span>')
    hot_lead_indicator.short_description = "Lead Priority"
    hot_lead_indicator.admin_order_field = 'submission_date'
    
    def days_since_inquiry(self, obj):
        """Show days since inquiry with color coding"""
        days = obj.days_since_inquiry
        if days <= 1:
            color = 'green'
        elif days <= 7:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} days</span>',
            color, days
        )
    days_since_inquiry.short_description = "Days Since Inquiry"
    
    # Custom actions
    def mark_as_contacted(self, request, queryset):
        """Mark selected inquiries as contacted"""
        queryset.update(status='contacted')
        self.message_user(request, f"{queryset.count()} inquiries marked as contacted.")
    mark_as_contacted.short_description = "Mark as Contacted"
    
    def mark_as_demo_scheduled(self, request, queryset):
        """Mark selected inquiries as demo scheduled"""
        queryset.update(status='demo-scheduled')
        self.message_user(request, f"{queryset.count()} inquiries marked as demo scheduled.")
    mark_as_demo_scheduled.short_description = "Mark as Demo Scheduled"
    
    def mark_as_proposal_sent(self, request, queryset):
        """Mark selected inquiries as proposal sent"""
        queryset.update(status='proposal-sent')
        self.message_user(request, f"{queryset.count()} inquiries marked as proposal sent.")
    mark_as_proposal_sent.short_description = "Mark as Proposal Sent"
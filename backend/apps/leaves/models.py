# apps/leaves/models.py

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta

class LeaveType(models.Model):
    """
    Defines different types of leave available in the organization
    """
    name = models.CharField(max_length=50, unique=True, help_text="Name of the leave type")
    code = models.CharField(max_length=10, unique=True, help_text="Short code for leave type")
    annual_allocation = models.PositiveIntegerField(
        default=21, 
        help_text="Number of days allocated per year for this leave type"
    )
    carry_forward = models.BooleanField(
        default=False, 
        help_text="Whether unused days can be carried forward to next year"
    )
    max_carry_forward = models.PositiveIntegerField(
        default=0, 
        help_text="Maximum days that can be carried forward"
    )
    requires_approval = models.BooleanField(
        default=True, 
        help_text="Whether this leave type requires manager approval"
    )
    is_paid = models.BooleanField(default=True, help_text="Whether this leave type is paid")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.code})"

class LeaveBalance(models.Model):
    """
    Tracks leave balance for each employee for each leave type
    """
    employee = models.ForeignKey(
        'employees.Employee', 
        on_delete=models.CASCADE, 
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(help_text="Year for which this balance applies")
    allocated_days = models.DecimalField(
        max_digits=5, 
        decimal_places=1, 
        default=Decimal('0.0'),
        help_text="Total days allocated for this year"
    )
    used_days = models.DecimalField(
        max_digits=5, 
        decimal_places=1, 
        default=Decimal('0.0'),
        help_text="Days already used"
    )
    pending_days = models.DecimalField(
        max_digits=5, 
        decimal_places=1, 
        default=Decimal('0.0'),
        help_text="Days in pending requests"
    )
    carried_forward = models.DecimalField(
        max_digits=5, 
        decimal_places=1, 
        default=Decimal('0.0'),
        help_text="Days carried forward from previous year"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['-year', 'leave_type__name']
    
    @property
    def available_days(self):
        """Calculate remaining available days"""
        return self.allocated_days + self.carried_forward - self.used_days - self.pending_days
    
    def __str__(self):
        return f"{self.employee.full_name()} - {self.leave_type.name} ({self.year})"

class LeaveRequest(models.Model):
    """
    Leave request submitted by employees
    """
    STATUS_CHOICES = (
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    )
    
    employee = models.ForeignKey(
        'employees.Employee', 
        on_delete=models.CASCADE, 
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField(help_text="First day of leave")
    end_date = models.DateField(help_text="Last day of leave")
    days_requested = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.5'))],
        help_text="Number of days requested"
    )
    reason = models.TextField(help_text="Reason for leave request")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Request tracking
    applied_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        'core.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_leaves'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Additional fields
    emergency_contact = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Emergency contact number during leave"
    )
    handover_notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Work handover instructions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_date']
        
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate date range
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date cannot be after end date")
            
            # Don't allow past dates for new requests
            if self.start_date < timezone.now().date() and not self.pk:
                raise ValidationError("Cannot apply for leave in the past")
    
    def calculate_working_days(self):
        """Calculate working days between start and end date (excluding weekends)"""
        if not self.start_date or not self.end_date:
            return 0
            
        current_date = self.start_date
        working_days = 0
        
        while current_date <= self.end_date:
            # Count Monday to Friday as working days (0-4 are Mon-Fri)
            if current_date.weekday() < 5:
                working_days += 1
            current_date += timedelta(days=1)
            
        return working_days
    
    def save(self, *args, **kwargs):
        # Auto-calculate days if not set
        if not self.days_requested:
            self.days_requested = self.calculate_working_days()
        
        super().save(*args, **kwargs)
        
        # Update leave balance when status changes
        if self.pk:  # Only for existing requests
            self.update_leave_balance()
    
    def update_leave_balance(self):
        """Update employee's leave balance based on request status"""
        try:
            balance, created = LeaveBalance.objects.get_or_create(
                employee=self.employee,
                leave_type=self.leave_type,
                year=self.start_date.year,
                defaults={
                    'allocated_days': self.leave_type.annual_allocation,
                    'used_days': Decimal('0.0'),
                    'pending_days': Decimal('0.0'),
                    'carried_forward': Decimal('0.0')
                }
            )
            
            # Recalculate pending and used days for this leave type and year
            pending_requests = LeaveRequest.objects.filter(
                employee=self.employee,
                leave_type=self.leave_type,
                start_date__year=self.start_date.year,
                status='pending'
            )
            
            approved_requests = LeaveRequest.objects.filter(
                employee=self.employee,
                leave_type=self.leave_type,
                start_date__year=self.start_date.year,
                status='approved'
            )
            
            balance.pending_days = sum(req.days_requested for req in pending_requests)
            balance.used_days = sum(req.days_requested for req in approved_requests)
            balance.save()
            
        except Exception as e:
            # Log error but don't break the save operation
            print(f"Error updating leave balance: {e}")
    
    @property
    def duration_in_days(self):
        """Get duration in human readable format"""
        if self.days_requested == 1:
            return "1 day"
        return f"{self.days_requested} days"
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        return self.status == 'rejected'
    
    def __str__(self):
        return f"{self.employee.full_name()} - {self.leave_type.name} ({self.start_date} to {self.end_date})"
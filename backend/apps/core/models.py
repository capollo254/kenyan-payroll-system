from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .company_models import CompanySettings


class TokenActivity(models.Model):
    """
    Track token activity for automatic logout after inactivity.
    """
    token = models.OneToOneField(
        Token,
        on_delete=models.CASCADE,
        related_name='activity'
    )
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Token Activity"
        verbose_name_plural = "Token Activities"
    
    def __str__(self):
        return f"Activity for {self.token.user.email}"
    
    @property
    def is_expired(self):
        """Check if token is expired based on inactivity (3 minutes)."""
        from django.conf import settings
        from datetime import timedelta
        
        timeout = getattr(settings, 'TOKEN_INACTIVITY_TIMEOUT', 180)
        expiration_time = self.last_activity + timedelta(seconds=timeout)
        return timezone.now() > expiration_time


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True) # <-- Added this field
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True) # <-- Added this field
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name


class ContactInquiry(models.Model):
    """Model to store contact form inquiries for lead management"""
    
    # Contact Information
    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Company Details
    employee_count = models.CharField(max_length=20, choices=[
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    ])
    industry = models.CharField(max_length=100, blank=True)
    current_method = models.CharField(max_length=20, choices=[
        ('manual', 'Manual/Excel'),
        ('basic-software', 'Basic Software'),
        ('payroll-service', 'Payroll Service'),
        ('other', 'Other'),
    ], blank=True)
    
    # Interest Details
    primary_interest = models.CharField(max_length=20, choices=[
        ('demo', 'Request Demo'),
        ('pricing', 'Get Pricing'),
        ('features', 'Learn Features'),
        ('implementation', 'Implementation Support'),
    ])
    timeline = models.CharField(max_length=20, choices=[
        ('immediately', 'Immediately'),
        ('1-3-months', '1-3 months'),
        ('3-6-months', '3-6 months'),
        ('6-12-months', '6-12 months'),
        ('planning-stage', 'Just planning'),
    ], blank=True)
    budget_range = models.CharField(max_length=20, choices=[
        ('under-10k', 'Under KES 10,000'),
        ('10k-50k', 'KES 10,000 - 50,000'),
        ('50k-100k', 'KES 50,000 - 100,000'),
        ('100k+', 'Over KES 100,000'),
    ], blank=True)
    
    # Additional Information
    specific_needs = models.TextField(blank=True, help_text="Specific requirements or challenges")
    newsletter = models.BooleanField(default=False)
    
    # System Fields
    submission_date = models.DateTimeField(auto_now_add=True)
    follow_up_date = models.DateTimeField(null=True, blank=True, help_text="When to follow up")
    status = models.CharField(max_length=20, choices=[
        ('new', 'New Lead'),
        ('contacted', 'Contacted'),
        ('demo-scheduled', 'Demo Scheduled'),
        ('proposal-sent', 'Proposal Sent'),
        ('negotiating', 'Negotiating'),
        ('closed-won', 'Closed - Won'),
        ('closed-lost', 'Closed - Lost'),
    ], default='new')
    notes = models.TextField(blank=True, help_text="Internal notes for follow-up")
    
    class Meta:
        ordering = ['-submission_date']
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
    
    def __str__(self):
        return f"{self.company_name} - {self.contact_name} ({self.submission_date.strftime('%Y-%m-%d')})"
    
    @property
    def is_hot_lead(self):
        """Determine if this is a hot lead based on criteria"""
        hot_criteria = [
            self.timeline in ['immediately', '1-3-months'],
            self.employee_count in ['51-200', '201-500', '500+'],
            self.budget_range in ['50k-100k', '100k+'],
            self.primary_interest in ['demo', 'implementation']
        ]
        return sum(hot_criteria) >= 2
    
    @property
    def days_since_inquiry(self):
        """Calculate days since inquiry was submitted"""
        return (timezone.now() - self.submission_date).days


# ===================================================================
# MULTI-TENANT MODELS - SaaS Setup
# ===================================================================

class Tenant(models.Model):
    """
    Multi-tenant model for SaaS setup
    Each tenant represents a company/organization using the system
    """
    # Basic Information
    company_name = models.CharField(max_length=200, help_text="Company/Organization name")
    subdomain = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="Unique subdomain for this tenant (e.g., 'acme' for acme.yourapp.com)"
    )
    domain = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        help_text="Custom domain (optional)"
    )
    
    # Subscription Information
    subscription_plan = models.CharField(
        max_length=50,
        choices=[
            ('trial', 'Trial (30 days)'),
            ('basic', 'Basic Plan'),
            ('professional', 'Professional Plan'),
            ('enterprise', 'Enterprise Plan'),
        ],
        default='trial'
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('trial', 'Trial'),
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
        ],
        default='trial'
    )
    
    # Limits and Features
    max_employees = models.IntegerField(default=10, help_text="Maximum number of employees allowed")
    features_enabled = models.JSONField(
        default=dict,
        help_text="JSON object with enabled features"
    )
    
    # Billing Information
    billing_email = models.EmailField(help_text="Email for billing communications")
    billing_cycle = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
        ],
        default='monthly'
    )
    next_billing_date = models.DateTimeField(null=True, blank=True)
    
    # System Fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    # Contact Information
    admin_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='administered_tenants',
        help_text="Primary admin user for this tenant"
    )
    
    class Meta:
        ordering = ['company_name']
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
    
    def __str__(self):
        return f"{self.company_name} ({self.subdomain})"
    
    @property
    def is_trial(self):
        """Check if tenant is in trial period"""
        return self.subscription_status == 'trial'
    
    @property
    def is_trial_expired(self):
        """Check if trial period has expired"""
        if not self.trial_end_date:
            return False
        return timezone.now() > self.trial_end_date
    
    @property
    def days_remaining_in_trial(self):
        """Get days remaining in trial"""
        if not self.trial_end_date or not self.is_trial:
            return 0
        remaining = (self.trial_end_date - timezone.now()).days
        return max(0, remaining)
    
    @property
    def full_domain(self):
        """Get the full domain for this tenant"""
        if self.domain:
            return self.domain
        return f"{self.subdomain}.yourdomain.com"  # Replace with your actual domain
    
    def get_feature(self, feature_name, default=False):
        """Check if a specific feature is enabled for this tenant"""
        return self.features_enabled.get(feature_name, default)
    
    def enable_feature(self, feature_name):
        """Enable a feature for this tenant"""
        self.features_enabled[feature_name] = True
        self.save()
    
    def disable_feature(self, feature_name):
        """Disable a feature for this tenant"""
        self.features_enabled[feature_name] = False
        self.save()


class TenantUser(models.Model):
    """
    Link users to tenants for multi-tenant access control
    A user can belong to multiple tenants with different roles
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_memberships')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='user_memberships')
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Administrator'),
            ('hr_manager', 'HR Manager'),
            ('payroll_manager', 'Payroll Manager'),
            ('employee', 'Employee'),
            ('readonly', 'Read Only'),
        ],
        default='employee'
    )
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'tenant']
        ordering = ['tenant__company_name', 'user__email']
        verbose_name = "Tenant User"
        verbose_name_plural = "Tenant Users"
    
    def __str__(self):
        return f"{self.user.email} - {self.tenant.company_name} ({self.role})"
    
    @property
    def is_admin(self):
        """Check if user has admin privileges for this tenant"""
        return self.role in ['owner', 'admin']
    
    @property
    def can_manage_payroll(self):
        """Check if user can manage payroll for this tenant"""
        return self.role in ['owner', 'admin', 'payroll_manager']
    
    @property
    def can_manage_employees(self):
        """Check if user can manage employees for this tenant"""
        return self.role in ['owner', 'admin', 'hr_manager']
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
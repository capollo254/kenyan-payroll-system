# apps/core/company_models.py

from django.db import models
from django.conf import settings
import os

def company_logo_upload_path(instance, filename):
    """Generate upload path for company logo"""
    ext = filename.split('.')[-1]
    filename = f'company_logo.{ext}'
    return os.path.join('company', filename)

class CompanySettings(models.Model):
    """Model to store company-wide settings including logo"""
    company_name = models.CharField(max_length=200, default='Kenyan Payroll System')
    kra_pin = models.CharField(
        max_length=20, 
        blank=True, 
        help_text='Company/Employer KRA PIN for tax purposes'
    )
    logo = models.ImageField(
        upload_to=company_logo_upload_path,
        null=True,
        blank=True,
        help_text='Upload company logo for payslips and documents'
    )
    address_line_1 = models.CharField(max_length=200, blank=True)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
    
    def __str__(self):
        return f"Company Settings - {self.company_name}"
    
    @classmethod
    def get_settings(cls):
        """Get or create company settings instance"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion of company settings
        pass
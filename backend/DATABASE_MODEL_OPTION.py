# Optional: Database Model for Contact Inquiries
# Add this to backend/apps/core/models.py if you want to store in database

from django.db import models
from django.utils import timezone

class ContactInquiry(models.Model):
    # Company Information
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Company Details
    employee_count = models.CharField(max_length=50)
    industry = models.CharField(max_length=255, blank=True)
    current_method = models.CharField(max_length=50, blank=True)
    
    # Requirements
    primary_interest = models.CharField(max_length=100)
    timeline = models.CharField(max_length=50, blank=True)
    budget_range = models.CharField(max_length=50, blank=True)
    specific_needs = models.TextField(blank=True)
    
    # Additional Info
    newsletter = models.BooleanField(default=False)
    submission_date = models.DateTimeField(default=timezone.now)
    
    # Status tracking
    status = models.CharField(max_length=50, default='new', choices=[
        ('new', 'New Inquiry'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified Lead'),
        ('demo_scheduled', 'Demo Scheduled'),
        ('proposal_sent', 'Proposal Sent'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ])
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submission_date']
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
    
    def __str__(self):
        return f"{self.company_name} - {self.contact_name} ({self.submission_date.strftime('%Y-%m-%d')})"

# If you add this model:
# 1. Run: python manage.py makemigrations
# 2. Run: python manage.py migrate
# 3. Update contact_views.py to save to database instead of just log file
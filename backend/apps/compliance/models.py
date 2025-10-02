# apps/compliance/models.py

from django.db import models
from decimal import Decimal

class StatutoryRate(models.Model):
    """
    Model to store configurable statutory deduction rates
    """
    RATE_TYPES = (
        ('nssf', 'NSSF Rate'),
        ('shif', 'SHIF Rate'), 
        ('ahl', 'AHL Rate'),
        ('paye_relief', 'PAYE Personal Relief'),
    )
    
    rate_type = models.CharField(max_length=20, choices=RATE_TYPES, unique=True)
    rate_value = models.DecimalField(max_digits=8, decimal_places=4, help_text="Rate as decimal (e.g., 0.06 for 6%)")
    description = models.TextField(blank=True, null=True)
    effective_date = models.DateField(help_text="Date when this rate becomes effective")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date']
        
    def __str__(self):
        return f"{self.get_rate_type_display()}: {self.rate_value}"
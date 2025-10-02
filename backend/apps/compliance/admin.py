# apps/compliance/admin.py

from django.contrib import admin
from .models import StatutoryRate

@admin.register(StatutoryRate)
class StatutoryRateAdmin(admin.ModelAdmin):
    list_display = ('rate_type', 'rate_value', 'rate_percentage_display', 'effective_date', 'is_active')
    list_filter = ('rate_type', 'is_active', 'effective_date')
    search_fields = ('rate_type', 'description')
    ordering = ['-effective_date', 'rate_type']
    
    @admin.display(description='Rate (%)')
    def rate_percentage_display(self, obj):
        return f"{obj.rate_value * 100:.2f}%"
# apps/compliance/serializers.py

from rest_framework import serializers
from .models import StatutoryRate

class StatutoryRateSerializer(serializers.ModelSerializer):
    rate_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = StatutoryRate
        fields = ['id', 'rate_type', 'rate_value', 'rate_percentage', 'description', 
                 'effective_date', 'is_active']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_rate_percentage(self, obj):
        """Convert decimal rate to percentage for display"""
        return float(obj.rate_value * 100)
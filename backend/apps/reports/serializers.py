# apps/reports/serializers.py

from rest_framework import serializers
from .models import ReportGenerationLog, P9Report, P9MonthlyBreakdown

class ReportGenerationLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the ReportGenerationLog model.
    """
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)

    class Meta:
        model = ReportGenerationLog
        fields = [
            'id', 'report_type', 'report_type_display', 'generated_by',
            'generated_by_name', 'generation_date', 'start_date', 'end_date', 'file_path'
        ]
        read_only_fields = ['generated_by', 'generation_date']


class P9MonthlyBreakdownSerializer(serializers.ModelSerializer):
    """Serializer for P9 Monthly Breakdown"""
    month_name = serializers.SerializerMethodField()
    
    class Meta:
        model = P9MonthlyBreakdown
        fields = [
            'id', 'month', 'month_name', 'basic_salary', 'benefits_non_cash',
            'value_of_quarters', 'gross_pay', 'retirement_contribution', 'ahl',
            'shif', 'prmf', 'total_deductions', 'chargeable_pay', 'tax_charged',
            'personal_relief', 'insurance_relief', 'paye_tax'
        ]
    
    def get_month_name(self, obj):
        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return month_names[obj.month] if 1 <= obj.month <= 12 else ''


class P9ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for P9 Tax Report
    """
    employee_name = serializers.CharField(read_only=True)
    monthly_breakdown = P9MonthlyBreakdownSerializer(many=True, read_only=True)
    effective_retirement_deduction = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    is_complete = serializers.BooleanField(read_only=True)
    
    # Employee details for display
    employee_email = serializers.EmailField(source='employee.user.email', read_only=True)
    employee_first_name = serializers.CharField(source='employee.user.first_name', read_only=True)
    employee_last_name = serializers.CharField(source='employee.user.last_name', read_only=True)
    
    class Meta:
        model = P9Report
        fields = [
            # Basic info
            'id', 'employee', 'employee_name', 'employee_email', 
            'employee_first_name', 'employee_last_name', 'tax_year',
            
            # Company info
            'employer_name', 'employer_pin', 'employee_pin',
            
            # Income totals
            'total_basic_salary', 'total_benefits_non_cash', 'total_value_of_quarters',
            'total_gross_pay',
            
            # Deductions
            'retirement_30_percent', 'retirement_actual', 'retirement_fixed_cap',
            'effective_retirement_deduction', 'total_ahl', 'total_shif', 'total_prmf',
            'total_owner_occupied_interest', 'total_deductions',
            
            # Tax calculations
            'chargeable_pay', 'tax_charged', 'total_personal_relief',
            'total_insurance_relief', 'total_paye_tax',
            
            # System fields
            'generated_date', 'updated_date', 'generated_by', 'status', 'notes',
            'is_complete',
            
            # Related data
            'monthly_breakdown'
        ]
        read_only_fields = [
            'employee_name', 'generated_date', 'updated_date', 'is_complete',
            'effective_retirement_deduction'
        ]

    def update(self, instance, validated_data):
        """Override update to recalculate totals when saved"""
        instance = super().update(instance, validated_data)
        instance.calculate_totals()
        instance.save()
        return instance

    def create(self, validated_data):
        """Override create to recalculate totals when created"""
        instance = super().create(validated_data)
        instance.calculate_totals()
        instance.save()
        return instance
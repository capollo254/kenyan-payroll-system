# apps/payroll/serializers.py

from rest_framework import serializers
from .models import PayrollRun, Payslip, PayslipDeduction
from apps.employees.serializers import EmployeeSerializer
from apps.core.company_models import CompanySettings

class PayrollRunSerializer(serializers.ModelSerializer):
    # Fix: Use DateField since run_date is a DateField in the model
    run_date = serializers.DateField(read_only=True)

    class Meta:
        model = PayrollRun
        fields = ['id', 'run_date', 'run_by', 'period_start_date', 'period_end_date']
        read_only_fields = ['run_by']


class PayslipDeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayslipDeduction
        fields = ['id', 'deduction_type', 'amount', 'is_statutory']


class CompanySettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanySettings
        fields = [
            'company_name', 'logo_url', 'address_line_1', 'address_line_2',
            'city', 'postal_code', 'country', 'phone', 'email', 'website'
        ]
    
    def get_logo_url(self, obj):
        """Return the logo URL if it exists"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class PayslipDetailedSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    payroll_run = PayrollRunSerializer(read_only=True)
    deductions = PayslipDeductionSerializer(many=True, read_only=True, source='deduction_items')
    company_settings = serializers.SerializerMethodField()
    
    # Breakdown of statutory deductions
    statutory_deductions = serializers.SerializerMethodField()
    voluntary_deductions = serializers.SerializerMethodField()
    
    class Meta:
        model = Payslip
        fields = [
            'id', 'payroll_run', 'employee', 'company_settings',
            'gross_salary', 'overtime_pay', 'total_gross_income',
            'paye_tax', 'nssf_deduction', 'shif_deduction',
            'ahl_deduction', 'helb_deduction', 'total_deductions', 'net_pay',
            'deductions', 'statutory_deductions', 'voluntary_deductions'
        ]
        read_only_fields = [
            'payroll_run', 'employee', 'gross_salary', 'overtime_pay',
            'total_gross_income', 'paye_tax', 'nssf_deduction', 'shif_deduction',
            'ahl_deduction', 'helb_deduction', 'total_deductions', 'net_pay',
            'deductions'
        ]
    
    def get_company_settings(self, obj):
        """Get company settings for the payslip"""
        company_settings = CompanySettings.get_settings()
        serializer = CompanySettingsSerializer(company_settings, context=self.context)
        return serializer.data
    
    def get_statutory_deductions(self, obj):
        """Get all statutory deductions"""
        return obj.deduction_items.filter(is_statutory=True).values('deduction_type', 'amount')
    
    def get_voluntary_deductions(self, obj):
        """Get all voluntary deductions"""
        return obj.deduction_items.filter(is_statutory=False).values('deduction_type', 'amount')


class PayslipSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    payroll_run = PayrollRunSerializer(read_only=True)
    deductions = PayslipDeductionSerializer(many=True, read_only=True, source='deduction_items')

    class Meta:
        model = Payslip
        fields = [
            'id', 'payroll_run', 'employee', 'gross_salary', 'overtime_pay',
            'total_gross_income', 'paye_tax', 'nssf_deduction', 'shif_deduction',
            'ahl_deduction', 'helb_deduction', 'total_deductions', 'net_pay',
            'deductions'
        ]
        read_only_fields = [
            'payroll_run', 'employee', 'gross_salary', 'overtime_pay',
            'total_gross_income', 'paye_tax', 'nssf_deduction', 'shif_deduction',
            'ahl_deduction', 'helb_deduction', 'total_deductions', 'net_pay',
            'deductions'
        ]
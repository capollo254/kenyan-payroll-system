# apps/employees/serializers.py

from rest_framework import serializers
from .models import Employee, VoluntaryDeduction, JobInformation, EmployeeBenefit


class BankingInformationSerializer(serializers.ModelSerializer):
    """Serializer specifically for banking information"""
    full_name = serializers.SerializerMethodField()
    account_type_display = serializers.SerializerMethodField()
    mobile_money_provider_display = serializers.SerializerMethodField()
    banking_info_formatted = serializers.SerializerMethodField()
    has_complete_banking_info = serializers.SerializerMethodField()
    
    def get_full_name(self, obj):
        return obj.full_name()
    
    def get_account_type_display(self, obj):
        return obj.get_account_type_display() if obj.account_type else None
    
    def get_mobile_money_provider_display(self, obj):
        return obj.get_mobile_money_provider_display() if obj.mobile_money_provider else None
    
    def get_banking_info_formatted(self, obj):
        return obj.get_banking_info()
    
    def get_has_complete_banking_info(self, obj):
        return obj.has_complete_banking_info()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'full_name',
            # Banking Information
            'bank_name', 'bank_code', 'bank_branch', 'bank_branch_code',
            'bank_account_number', 'account_type', 'account_holder_name',
            'account_type_display', 'banking_info_formatted', 'has_complete_banking_info',
            # Mobile Money Information  
            'mobile_money_provider', 'mobile_money_number', 'mobile_money_provider_display',
        ]


class JobInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInformation
        fields = ['company_employee_id', 'kra_pin', 'nssf_number', 'nhif_number', 
                 'department', 'position', 'date_of_joining', 'is_active']


class VoluntaryDeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoluntaryDeduction
        fields = ['id', 'name', 'deduction_type', 'calculation_type', 'amount', 
                 'description', 'start_date', 'end_date', 'is_active', 'employee']
        read_only_fields = ['created_at', 'updated_at']


class EmployeeBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBenefit
        fields = ['id', 'name', 'benefit_type', 'calculation_type', 'amount', 
                 'description', 'is_taxable', 'is_active', 'employee']
        read_only_fields = ['created_at', 'updated_at']


class EmployeeSerializer(serializers.ModelSerializer):
    job_information = JobInformationSerializer(source='job_info', read_only=True)
    voluntary_deductions = VoluntaryDeductionSerializer(many=True, read_only=True)
    benefits = EmployeeBenefitSerializer(many=True, read_only=True)
    
    # Use SerializerMethodField to get the full name from the method
    full_name = serializers.SerializerMethodField()
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    # Banking information methods
    banking_info = serializers.SerializerMethodField()
    has_complete_banking = serializers.SerializerMethodField()
    account_type_display = serializers.SerializerMethodField()
    mobile_money_provider_display = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.full_name()
    
    def get_banking_info(self, obj):
        return obj.get_banking_info()
    
    def get_has_complete_banking(self, obj):
        return obj.has_complete_banking_info()
    
    def get_account_type_display(self, obj):
        return obj.get_account_type_display() if obj.account_type else None
    
    def get_mobile_money_provider_display(self, obj):
        return obj.get_mobile_money_provider_display() if obj.mobile_money_provider else None

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'full_name', 'email', 'first_name', 'last_name',
            'gross_salary', 'helb_monthly_deduction', 'is_active',
            # Banking Information
            'bank_name', 'bank_code', 'bank_branch', 'bank_branch_code',
            'bank_account_number', 'account_type', 'account_holder_name',
            'account_type_display', 'banking_info', 'has_complete_banking',
            # Mobile Money Information  
            'mobile_money_provider', 'mobile_money_number', 'mobile_money_provider_display',
            # KRA Tax Relief Fields
            'monthly_insurance_premiums', 'monthly_medical_fund_contribution', 'monthly_mortgage_interest',
            # Related Information
            'job_information', 'voluntary_deductions', 'benefits'
        ]
        read_only_fields = ['user', 'is_active']
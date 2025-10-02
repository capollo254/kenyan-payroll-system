# apps/payroll/serializers.py

from rest_framework import serializers
from .models import PayrollRun, Payslip, PayslipDeduction
from apps.employees.serializers import EmployeeSerializer

class PayslipDeductionSerializer(serializers.ModelSerializer):
    """
    Serializer for the PayslipDeduction model.
    This is used to list individual deductions on a payslip.
    """
    deduction_type_display = serializers.CharField(source='get_deduction_type_display', read_only=True)

    class Meta:
        model = PayslipDeduction
        fields = ('id', 'deduction_type', 'deduction_type_display', 'amount', 'is_statutory')
        read_only_fields = ('id',)

class PayslipSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payslip model.
    Includes nested serializers for employee details and individual deductions.
    """
    # Use the EmployeeSerializer to embed employee details
    employee = EmployeeSerializer(read_only=True)
    
    # A nested serializer to show the individual deduction items
    deduction_items = PayslipDeductionSerializer(many=True, read_only=True)

    class Meta:
        model = Payslip
        fields = (
            'id', 
            'payroll_run',
            'employee',
            'gross_salary', 
            'overtime_pay', 
            'total_gross_income',
            'paye_tax', 
            'nssf_deduction', 
            'shif_deduction', 
            'ahl_deduction',
            'helb_deduction',
            'total_deductions', 
            'net_pay',
            'deduction_items', # Include the nested deductions
        )
        read_only_fields = ('id',)


class PayrollRunSerializer(serializers.ModelSerializer):
    """
    Serializer for the PayrollRun model.
    Includes nested payslips to represent the entire run in one API call.
    """
    payslips = PayslipSerializer(many=True, read_only=True)
    
    class Meta:
        model = PayrollRun
        fields = (
            'id',
            'run_date',
            'period_start_date',
            'period_end_date',
            'total_net_pay',
            'total_deductions',
            'payslips',
        )
        read_only_fields = ('id',)
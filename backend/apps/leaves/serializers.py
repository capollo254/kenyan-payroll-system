# apps/leaves/serializers.py

from rest_framework import serializers
from django.utils import timezone
from .models import LeaveType, LeaveBalance, LeaveRequest
from apps.employees.serializers import EmployeeSerializer

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'code', 'annual_allocation', 'carry_forward', 
                 'max_carry_forward', 'requires_approval', 'is_paid', 'is_active']

class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    available_days = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaveBalance
        fields = ['id', 'employee', 'employee_name', 'leave_type', 'year', 
                 'allocated_days', 'used_days', 'pending_days', 'carried_forward', 
                 'available_days']

class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.user.username', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    duration_in_days = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'leave_type', 
            'leave_type_name', 'start_date', 'end_date', 'days_requested', 
            'reason', 'status', 'status_display', 'applied_date', 'approved_by', 
            'approved_by_name', 'approved_date', 'rejection_reason', 
            'emergency_contact', 'handover_notes', 'duration_in_days'
        ]
        read_only_fields = ['applied_date', 'approved_date', 'duration_in_days']
    
    def validate(self, data):
        # Validate date range
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date cannot be after end date")
        
        # Validate leave balance (only for new requests)
        if not self.instance:  # New request
            employee = data['employee']
            leave_type = data['leave_type']
            year = data['start_date'].year
            days_requested = data.get('days_requested', 0)
            
            try:
                balance = LeaveBalance.objects.get(
                    employee=employee,
                    leave_type=leave_type,
                    year=year
                )
                if balance.available_days < days_requested:
                    raise serializers.ValidationError(
                        f"Insufficient leave balance. Available: {balance.available_days} days, "
                        f"Requested: {days_requested} days"
                    )
            except LeaveBalance.DoesNotExist:
                # Create balance if it doesn't exist
                LeaveBalance.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    allocated_days=leave_type.annual_allocation
                )
        
        return data

class LeaveRequestCreateSerializer(LeaveRequestSerializer):
    """Serializer for creating leave requests (employee view)"""
    class Meta(LeaveRequestSerializer.Meta):
        fields = [
            'leave_type', 'start_date', 'end_date', 'days_requested', 
            'reason', 'emergency_contact', 'handover_notes'
        ]
    
    def validate(self, data):
        # Validate date range
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date cannot be after end date")
        
        # Get employee from request context
        try:
            employee = self.context['request'].user.employee_profile
        except AttributeError:
            raise serializers.ValidationError("User does not have an employee profile")
        
        # Validate leave balance (only for new requests)
        if not self.instance:  # New request
            leave_type = data['leave_type']
            year = data['start_date'].year
            days_requested = data.get('days_requested', 0)
            
            try:
                balance = LeaveBalance.objects.get(
                    employee=employee,
                    leave_type=leave_type,
                    year=year
                )
                if balance.available_days < days_requested:
                    raise serializers.ValidationError(
                        f"Insufficient leave balance. Available: {balance.available_days} days, "
                        f"Requested: {days_requested} days"
                    )
            except LeaveBalance.DoesNotExist:
                # Create balance if it doesn't exist
                LeaveBalance.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    allocated_days=leave_type.annual_allocation
                )
        
        return data
    
    def create(self, validated_data):
        # Set the employee from the request user
        try:
            validated_data['employee'] = self.context['request'].user.employee_profile
        except AttributeError:
            raise serializers.ValidationError("User does not have an employee profile")
        return super().create(validated_data)

class LeaveRequestApprovalSerializer(serializers.ModelSerializer):
    """Serializer for approving/rejecting leave requests (admin view)"""
    class Meta:
        model = LeaveRequest
        fields = ['status', 'rejection_reason']
    
    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status must be either 'approved' or 'rejected'")
        return value
    
    def update(self, instance, validated_data):
        # Set approval info
        if validated_data.get('status') == 'approved':
            instance.approved_by = self.context['request'].user
            instance.approved_date = serializers.DateTimeField().to_representation(
                serializers.DateTimeField().to_internal_value(
                    timezone.now().isoformat()
                )
            )
        
        return super().update(instance, validated_data)
# apps/employees/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Employee, JobInformation, VoluntaryDeduction, EmployeeBenefit
from .serializers import EmployeeSerializer, JobInformationSerializer, VoluntaryDeductionSerializer, EmployeeBenefitSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return employees based on user permissions
        """
        user = self.request.user
        
        # If user is superuser, they can see all employees
        if user.is_superuser:
            return Employee.objects.all().order_by('user__last_name')
        
        # Regular employees can only see their own profile
        try:
            employee = user.employee_profile
            return Employee.objects.filter(id=employee.id)
        except Exception:
            # If user has no employee profile, return empty queryset
            return Employee.objects.none()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Returns the current user's employee profile.
        """
        try:
            employee = Employee.objects.get(user=request.user)
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found for current user'}, status=404)

    @action(detail=True, methods=['get'])
    def gross_salary(self, request, pk=None):
        employee = self.get_object()
        return Response({'gross_salary': employee.gross_salary})
    
    @action(detail=False, methods=['get'])
    def banking_details(self, request):
        """
        Returns banking details for the current user's employee profile.
        """
        try:
            employee = Employee.objects.get(user=request.user)
            banking_info = {
                'id': employee.id,
                'full_name': employee.full_name(),
                'bank_name': employee.bank_name,
                'bank_code': employee.bank_code,
                'bank_branch': employee.bank_branch,
                'bank_branch_code': employee.bank_branch_code,
                'bank_account_number': employee.bank_account_number,
                'account_type': employee.account_type,
                'account_type_display': employee.get_account_type_display() if employee.account_type else None,
                'account_holder_name': employee.account_holder_name,
                'mobile_money_provider': employee.mobile_money_provider,
                'mobile_money_provider_display': employee.get_mobile_money_provider_display() if employee.mobile_money_provider else None,
                'mobile_money_number': employee.mobile_money_number,
                'banking_info_formatted': employee.get_banking_info(),
                'has_complete_banking_info': employee.has_complete_banking_info(),
            }
            return Response(banking_info)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found for current user'}, status=404)
    
    @action(detail=True, methods=['get'])
    def banking_details_by_id(self, request, pk=None):
        """
        Returns banking details for a specific employee (admin only).
        """
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
        
        employee = self.get_object()
        banking_info = {
            'id': employee.id,
            'full_name': employee.full_name(),
            'bank_name': employee.bank_name,
            'bank_code': employee.bank_code,
            'bank_branch': employee.bank_branch,
            'bank_branch_code': employee.bank_branch_code,
            'bank_account_number': employee.bank_account_number,
            'account_type': employee.account_type,
            'account_type_display': employee.get_account_type_display() if employee.account_type else None,
            'account_holder_name': employee.account_holder_name,
            'mobile_money_provider': employee.mobile_money_provider,
            'mobile_money_provider_display': employee.get_mobile_money_provider_display() if employee.mobile_money_provider else None,
            'mobile_money_number': employee.mobile_money_number,
            'banking_info_formatted': employee.get_banking_info(),
            'has_complete_banking_info': employee.has_complete_banking_info(),
        }
        return Response(banking_info)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_banking_details(self, request):
        """
        Updates banking details for the current user's employee profile.
        """
        try:
            employee = Employee.objects.get(user=request.user)
            
            # Update banking fields if provided
            banking_fields = [
                'bank_name', 'bank_code', 'bank_branch', 'bank_branch_code',
                'bank_account_number', 'account_type', 'account_holder_name',
                'mobile_money_provider', 'mobile_money_number'
            ]
            
            updated_fields = []
            for field in banking_fields:
                if field in request.data:
                    setattr(employee, field, request.data[field])
                    updated_fields.append(field)
            
            if updated_fields:
                employee.save(update_fields=updated_fields)
                
                # Return updated banking info
                banking_info = {
                    'id': employee.id,
                    'full_name': employee.full_name(),
                    'bank_name': employee.bank_name,
                    'bank_code': employee.bank_code,
                    'bank_branch': employee.bank_branch,
                    'bank_branch_code': employee.bank_branch_code,
                    'bank_account_number': employee.bank_account_number,
                    'account_type': employee.account_type,
                    'account_type_display': employee.get_account_type_display() if employee.account_type else None,
                    'account_holder_name': employee.account_holder_name,
                    'mobile_money_provider': employee.mobile_money_provider,
                    'mobile_money_provider_display': employee.get_mobile_money_provider_display() if employee.mobile_money_provider else None,
                    'mobile_money_number': employee.mobile_money_number,
                    'banking_info_formatted': employee.get_banking_info(),
                    'has_complete_banking_info': employee.has_complete_banking_info(),
                    'updated_fields': updated_fields
                }
                return Response(banking_info)
            else:
                return Response({'message': 'No banking fields provided for update'}, status=400)
                
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found for current user'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def employees_with_incomplete_banking(self, request):
        """
        Returns employees with incomplete banking information (admin only).
        """
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
        
        # Find employees with incomplete banking info
        incomplete_banking_employees = []
        employees = Employee.objects.all()
        
        for employee in employees:
            if not employee.has_complete_banking_info():
                incomplete_banking_employees.append({
                    'id': employee.id,
                    'full_name': employee.full_name(),
                    'email': employee.user.email,
                    'missing_fields': self._get_missing_banking_fields(employee),
                    'banking_completion_percentage': self._get_banking_completion_percentage(employee)
                })
        
        return Response({
            'count': len(incomplete_banking_employees),
            'employees': incomplete_banking_employees
        })
    
    def _get_missing_banking_fields(self, employee):
        """Helper method to identify missing banking fields"""
        required_fields = {
            'bank_name': employee.bank_name,
            'bank_code': employee.bank_code,
            'bank_branch': employee.bank_branch,
            'bank_branch_code': employee.bank_branch_code,
            'bank_account_number': employee.bank_account_number,
            'account_type': employee.account_type,
        }
        
        missing_fields = []
        for field_name, field_value in required_fields.items():
            if not field_value:
                missing_fields.append(field_name)
        
        return missing_fields
    
    def _get_banking_completion_percentage(self, employee):
        """Helper method to calculate banking info completion percentage"""
        required_fields = [
            employee.bank_name,
            employee.bank_code,
            employee.bank_branch,
            employee.bank_branch_code,
            employee.bank_account_number,
            employee.account_type,
        ]
        
        completed_fields = sum(1 for field in required_fields if field)
        total_fields = len(required_fields)
        
        return round((completed_fields / total_fields) * 100, 1) if total_fields > 0 else 0
    
class JobInformationViewSet(viewsets.ModelViewSet):
    serializer_class = JobInformationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return job information based on user permissions
        """
        user = self.request.user
        
        # If user is superuser, they can see all job information
        if user.is_superuser:
            return JobInformation.objects.all().order_by('employee__user__last_name')
        
        # Regular employees can only see their own job information
        try:
            employee = user.employee_profile
            return JobInformation.objects.filter(employee=employee)
        except Exception:
            return JobInformation.objects.none()

class VoluntaryDeductionViewSet(viewsets.ModelViewSet):
    serializer_class = VoluntaryDeductionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return voluntary deductions based on user permissions
        """
        user = self.request.user
        
        # If user is superuser, they can see all deductions
        if user.is_superuser:
            return VoluntaryDeduction.objects.all()
        
        # Regular employees can only see their own deductions
        try:
            employee = user.employee_profile
            return VoluntaryDeduction.objects.filter(employee=employee)
        except Exception:
            return VoluntaryDeduction.objects.none()

class EmployeeBenefitViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeBenefitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return employee benefits based on user permissions
        """
        user = self.request.user
        
        # If user is superuser, they can see all benefits
        if user.is_superuser:
            return EmployeeBenefit.objects.all()
        
        # Regular employees can only see their own benefits
        try:
            employee = user.employee_profile
            return EmployeeBenefit.objects.filter(employee=employee)
        except Exception:
            return EmployeeBenefit.objects.none()
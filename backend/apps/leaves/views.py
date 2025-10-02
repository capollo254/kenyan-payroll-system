# apps/leaves/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from .models import LeaveType, LeaveBalance, LeaveRequest
from .serializers import (
    LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer,
    LeaveRequestCreateSerializer, LeaveRequestApprovalSerializer
)

class LeaveTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing leave types
    """
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]
    queryset = LeaveType.objects.filter(is_active=True)

class LeaveBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing leave balances
    """
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['leave_type', 'year']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    
    def get_queryset(self):
        user = self.request.user
        
        # Superusers can see all balances
        if user.is_superuser:
            return LeaveBalance.objects.all().order_by('-year', 'employee__user__last_name')
        
        # Regular employees can only see their own balances
        try:
            employee = user.employee_profile
            return LeaveBalance.objects.filter(employee=employee).order_by('-year')
        except:
            return LeaveBalance.objects.none()

class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave requests
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'leave_type', 'employee']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reason']
    ordering_fields = ['applied_date', 'start_date', 'end_date']
    ordering = ['-applied_date']
    
    def get_queryset(self):
        user = self.request.user
        
        # Superusers can see all leave requests
        if user.is_superuser:
            return LeaveRequest.objects.all()
        
        # Regular employees can only see their own requests
        try:
            employee = user.employee_profile
            return LeaveRequest.objects.filter(employee=employee)
        except:
            return LeaveRequest.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveRequestCreateSerializer
        elif self.action in ['approve', 'reject']:
            return LeaveRequestApprovalSerializer
        return LeaveRequestSerializer
    
    def perform_create(self, serializer):
        # Ensure the employee is set to the current user's profile
        employee = self.request.user.employee_profile
        serializer.save(employee=employee)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """
        Approve a leave request (superuser only)
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can approve leave requests'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        leave_request = self.get_object()
        
        if leave_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check leave balance
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            )
            if balance.available_days < leave_request.days_requested:
                return Response(
                    {
                        'error': f'Insufficient leave balance. Available: {balance.available_days} days, '
                                f'Requested: {leave_request.days_requested} days'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except LeaveBalance.DoesNotExist:
            return Response(
                {'error': 'Leave balance not found for this employee and leave type'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Approve the request
        leave_request.status = 'approved'
        leave_request.approved_by = request.user
        leave_request.approved_date = timezone.now()
        leave_request.save()
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response({
            'message': 'Leave request approved successfully',
            'leave_request': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """
        Reject a leave request (superuser only)
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can reject leave requests'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        leave_request = self.get_object()
        
        if leave_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be rejected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get rejection reason from request data
        rejection_reason = request.data.get('rejection_reason', '')
        
        if not rejection_reason:
            return Response(
                {'error': 'Rejection reason is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reject the request
        leave_request.status = 'rejected'
        leave_request.approved_by = request.user
        leave_request.approved_date = timezone.now()
        leave_request.rejection_reason = rejection_reason
        leave_request.save()
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response({
            'message': 'Leave request rejected successfully',
            'leave_request': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending_requests(self, request):
        """
        Get all pending leave requests (superuser only)
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can view all pending requests'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_requests = LeaveRequest.objects.filter(status='pending').order_by('applied_date')
        serializer = LeaveRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_balance(self, request):
        """
        Get current user's leave balances for current year
        """
        try:
            employee = request.user.employee_profile
            current_year = timezone.now().year
            balances = LeaveBalance.objects.filter(
                employee=employee, 
                year=current_year
            )
            serializer = LeaveBalanceSerializer(balances, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {'error': 'Employee profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def dashboard_stats(self, request):
        """
        Get leave statistics for dashboard (superuser only)
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only administrators can view dashboard statistics'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'pending_requests': LeaveRequest.objects.filter(status='pending').count(),
            'approved_today': LeaveRequest.objects.filter(
                status='approved', 
                approved_date__date=timezone.now().date()
            ).count(),
            'employees_on_leave_today': LeaveRequest.objects.filter(
                status='approved',
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date()
            ).count(),
            'upcoming_leaves': LeaveRequest.objects.filter(
                status='approved',
                start_date__gt=timezone.now().date(),
                start_date__lte=timezone.now().date() + timezone.timedelta(days=7)
            ).count()
        }
        
        return Response(stats)
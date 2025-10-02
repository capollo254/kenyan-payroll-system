# apps/employees/views.py
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import Employee, JobInformation, VoluntaryDeduction
from .serializers import EmployeeSerializer, JobInformationSerializer, VoluntaryDeductionSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows employees to be viewed or edited.
    """
    queryset = Employee.objects.select_related('user', 'job_info').prefetch_related('voluntary_deductions').all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

class JobInformationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows job information to be viewed or edited.
    """
    queryset = JobInformation.objects.select_related('employee__user').all()
    serializer_class = JobInformationSerializer
    permission_classes = [IsAuthenticated]

class VoluntaryDeductionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows voluntary deductions to be viewed or edited.
    """
    queryset = VoluntaryDeduction.objects.select_related('employee__user').all()
    serializer_class = VoluntaryDeductionSerializer
    permission_classes = [IsAuthenticated]
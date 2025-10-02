# apps/employees/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import EmployeeViewSet, JobInformationViewSet, VoluntaryDeductionViewSet

router = DefaultRouter()

router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'job-information', JobInformationViewSet, basename='job-information')
router.register(r'voluntary-deductions', VoluntaryDeductionViewSet, basename='voluntary-deduction')

urlpatterns = [
    path('', include(router.urls)),
]
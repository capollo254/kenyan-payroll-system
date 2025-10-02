# apps/payroll/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PayrollRunViewSet, PayslipViewSet

# Create a router instance
router = DefaultRouter()

# Register the viewsets with the router
# The first argument is the URL prefix for this viewset
# The second argument is the ViewSet class itself
router.register(r'payroll-runs', PayrollRunViewSet, basename='payroll-run')
router.register(r'payslips', PayslipViewSet, basename='payslip')

urlpatterns = [
    # The router automatically generates a full set of RESTful URLs for each viewset
    path('', include(router.urls)),
]
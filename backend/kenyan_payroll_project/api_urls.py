# kenyan_payroll_project/api_urls.py

from django.urls import path, include

urlpatterns = [
    # Auth endpoints
    path('auth/', include('apps.core.urls')),
    
    # App-specific endpoints
    path('employees/', include('apps.employees.urls')),
    path('payroll/', include('apps.payroll.urls')),
    path('reports/', include('apps.reports.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('compliance/', include('apps.compliance.urls')),
    path('leaves/', include('apps.leaves.urls')),
]
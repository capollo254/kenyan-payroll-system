# kenyan_payroll_project/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from apps.core.views import welcome, calculator_page, api_root, user_logout_view, user_login_view, my_payslips_view, test_simple_view, payslips_view_fixed, api_docs_view_fixed, calculator_view_fixed, debug_user_check_secure, create_admin_disabled, react_frontend_fixed
from apps.core.contact_views import contact_form_view, contact_form_submit
from apps.payroll.calculator_views import public_payroll_calculator
import os

# Customize Django Admin Interface
admin.site.site_header = "Kenya Payroll System Administration"
admin.site.site_title = "Kenya Payroll System Admin"
admin.site.index_title = "Welcome to Kenya Payroll System Administration"

urlpatterns = [
    path('', welcome, name='home'),  # Root URL
    path('admin/', admin.site.urls),
    path('welcome/', welcome, name='welcome'),
    
    # Authentication
    path('logout/', user_logout_view, name='logout'),
    path('login/', user_login_view, name='login'),
    
    # Payslips - Using fixed version
    path('my-payslips/', payslips_view_fixed, name='my_payslips'),
    
    # Calculator page - Full calculator interface  
    path('calculator/', calculator_page, name='calculator_page'),
    
    # Contact form for businesses interested in full system
    path('contact/', contact_form_view, name='contact_form'),
    path('contact/submit/', contact_form_submit, name='contact_submit'),
    
    # Debug calculator
    path('debug-calculator/', lambda request: HttpResponse(open(os.path.join(settings.BASE_DIR.parent, 'debug_calculator.html'), 'r').read(), content_type='text/html'), name='debug_calculator'),
    path('admin-trigger/', lambda request: HttpResponse(open(os.path.join(settings.BASE_DIR.parent, 'create_admin_trigger.html'), 'r').read(), content_type='text/html'), name='admin_trigger'),
    
    # API Root documentation - Using fixed version
    path('api/', api_docs_view_fixed, name='api_root'),
    
    # Debug endpoint for checking users
    path('debug/users/', debug_user_check_secure, name='debug_users_secure'),
    path('debug/create-admin/', create_admin_disabled, name='create_admin_disabled'),
    path('debug/create-admin-no-csrf/', create_admin_disabled, name='create_admin_disabled_no_csrf'),
    path('admin-trigger/', create_admin_disabled, name='admin_trigger_disabled'),
    
    # React Frontend
    path('frontend/', react_frontend_fixed, name='react_frontend_fixed'),
    path('employee-portal/', react_frontend_fixed, name='employee_portal'),
    
    # Public Calculator API (no authentication required)
    path('api/public/calculator/', public_payroll_calculator, name='public_calculator'),
    
    # Authenticated API endpoints
    path('api/v1/auth/', include('apps.core.urls')),
    path('api/v1/employees/', include('apps.employees.urls')),
    path('api/v1/payroll/', include('apps.payroll.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/leaves/', include('apps.leaves.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Add at the end of urls.py before the media files section

# Serve React static files
if settings.DEBUG or True:  # Allow in production for React frontend
    from django.views.static import serve
    import re
    
    urlpatterns += [
        re_path(r'^frontend-static/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR.parent, 'frontend_build', 'static'),
        }),
    ]

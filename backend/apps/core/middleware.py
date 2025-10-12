# apps/core/middleware.py

from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import Tenant, TenantUser


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to detect and set the current tenant based on subdomain or path
    This enables multi-tenant functionality for the SaaS application
    """
    
    def process_request(self, request):
        """
        Process the incoming request to determine the tenant
        """
        # Skip tenant detection for admin, API, and static routes
        if self.should_skip_tenant_detection(request):
            return None
        
        # Determine tenant from subdomain or path
        tenant = self.get_tenant_from_request(request)
        
        if tenant:
            # Set tenant in request
            request.tenant = tenant
            request.tenant_obj = tenant  # Store the actual model instance
            
            # Check if tenant is active and subscription is valid
            if not self.is_tenant_accessible(tenant):
                return self.handle_inactive_tenant(request, tenant)
        else:
            # No tenant found - handle default case
            request.tenant = None
            request.tenant_obj = None
        
        return None
    
    def should_skip_tenant_detection(self, request):
        """
        Check if tenant detection should be skipped for this request
        """
        skip_paths = [
            '/admin/',
            '/api/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
        ]
        
        path = request.path_info
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def get_tenant_from_request(self, request):
        """
        Extract tenant information from the request
        Priority: Path parameter > Custom domain > Subdomain > Default
        """
        tenant = None
        
        # Method 1: Check for tenant in path (/tenant/subdomain/)
        path_parts = request.path_info.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'tenant':
            subdomain = path_parts[1]
            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                return tenant
            except Tenant.DoesNotExist:
                pass
        
        # Method 2: Check for specific frontend paths that should use default tenant
        if request.path_info.startswith('/employee-portal') or request.path_info.startswith('/app'):
            try:
                tenant = Tenant.objects.get(subdomain='default', is_active=True)
                return tenant
            except Tenant.DoesNotExist:
                pass
        
        # Method 3: Check for custom domain
        host = request.get_host().split(':')[0]  # Remove port if present
        try:
            tenant = Tenant.objects.get(domain=host, is_active=True)
            return tenant
        except Tenant.DoesNotExist:
            pass
        
        # Method 4: Check for subdomain
        if '.' in host and not self.is_local_development(host):
            subdomain = host.split('.')[0]
            if subdomain and subdomain != 'www':
                try:
                    tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                    return tenant
                except Tenant.DoesNotExist:
                    pass
        
        # Method 5: Default tenant for local development
        if self.is_local_development(host):
            try:
                tenant = Tenant.objects.filter(
                    subdomain='default', 
                    is_active=True
                ).first()
                return tenant
            except:
                pass
        
        return None
    
    def is_local_development(self, host):
        """
        Check if we're in local development environment
        """
        local_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
        return any(local_host in host for local_host in local_hosts)
    
    def is_tenant_accessible(self, tenant):
        """
        Check if the tenant is accessible (active subscription, not expired, etc.)
        """
        if not tenant.is_active:
            return False
        
        # Check if trial has expired
        if tenant.is_trial and tenant.is_trial_expired:
            return False
        
        # Check subscription status
        if tenant.subscription_status in ['suspended', 'cancelled', 'expired']:
            return False
        
        return True
    
    def handle_inactive_tenant(self, request, tenant):
        """
        Handle cases where tenant exists but is not accessible
        """
        from django.http import HttpResponse
        
        if tenant.is_trial_expired:
            return HttpResponse(
                "<h1>Trial Expired</h1>"
                "<p>Your trial period has expired. Please upgrade to continue using the service.</p>",
                status=402  # Payment Required
            )
        
        if tenant.subscription_status == 'suspended':
            return HttpResponse(
                "<h1>Account Suspended</h1>"
                "<p>This account has been suspended. Please contact support.</p>",
                status=403  # Forbidden
            )
        
        return HttpResponse(
            "<h1>Service Unavailable</h1>"
            "<p>This service is temporarily unavailable.</p>",
            status=503  # Service Unavailable
        )


class TenantUserMiddleware(MiddlewareMixin):
    """
    Middleware to check user permissions within a tenant context
    """
    
    def process_request(self, request):
        """
        Check if the authenticated user has access to the current tenant
        """
        # Skip if no tenant or user is not authenticated
        if not hasattr(request, 'tenant_obj') or not request.tenant_obj:
            return None
        
        if not request.user.is_authenticated:
            return None
        
        # Skip for superusers
        if request.user.is_superuser:
            return None
        
        # Check if user has access to this tenant
        try:
            tenant_user = TenantUser.objects.get(
                user=request.user,
                tenant=request.tenant_obj,
                is_active=True
            )
            request.tenant_user = tenant_user
            request.tenant_role = tenant_user.role
        except TenantUser.DoesNotExist:
            # User doesn't have access to this tenant
            request.tenant_user = None
            request.tenant_role = None
        
        return None


class TenantDatabaseMiddleware(MiddlewareMixin):
    """
    Middleware to filter database queries by tenant
    This can be extended to implement database-per-tenant or schema-per-tenant
    """
    
    def process_request(self, request):
        """
        Set up tenant context for database queries
        """
        if hasattr(request, 'tenant_obj') and request.tenant_obj:
            # Store tenant ID in thread-local storage or request
            # This can be used by model managers to filter queries
            request.tenant_id = request.tenant_obj.id
        else:
            request.tenant_id = None
        
        return None
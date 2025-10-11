# apps/core/management/commands/setup_tenants.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Tenant, TenantUser

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up default tenants for multi-tenant SaaS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing tenants (delete all)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write("🗑️  Removing existing tenants...")
            Tenant.objects.all().delete()
            TenantUser.objects.all().delete()

        self.stdout.write("🏢 Setting up default tenants...")

        # Create default tenant for development
        default_tenant, created = Tenant.objects.get_or_create(
            subdomain='default',
            defaults={
                'company_name': 'Default Company',
                'subscription_plan': 'trial',
                'subscription_status': 'trial',
                'max_employees': 50,
                'billing_email': 'admin@default.com',
                'trial_end_date': timezone.now() + timedelta(days=30),
                'features_enabled': {
                    'payroll': True,
                    'reports': True,
                    'leave_management': True,
                    'multi_currency': False,
                    'advanced_reports': False,
                }
            }
        )
        
        if created:
            self.stdout.write(f"✅ Created default tenant: {default_tenant}")
        else:
            self.stdout.write(f"ℹ️  Default tenant already exists: {default_tenant}")

        # Create demo tenant
        demo_tenant, created = Tenant.objects.get_or_create(
            subdomain='demo',
            defaults={
                'company_name': 'Demo Corporation',
                'subscription_plan': 'professional',
                'subscription_status': 'active',
                'max_employees': 100,
                'billing_email': 'billing@demo.com',
                'features_enabled': {
                    'payroll': True,
                    'reports': True,
                    'leave_management': True,
                    'multi_currency': True,
                    'advanced_reports': True,
                }
            }
        )
        
        if created:
            self.stdout.write(f"✅ Created demo tenant: {demo_tenant}")
        else:
            self.stdout.write(f"ℹ️  Demo tenant already exists: {demo_tenant}")

        # Create test company tenant
        test_tenant, created = Tenant.objects.get_or_create(
            subdomain='acme',
            defaults={
                'company_name': 'ACME Corporation',
                'subscription_plan': 'basic',
                'subscription_status': 'trial',
                'max_employees': 25,
                'billing_email': 'hr@acme.com',
                'trial_end_date': timezone.now() + timedelta(days=15),
                'features_enabled': {
                    'payroll': True,
                    'reports': True,
                    'leave_management': False,
                    'multi_currency': False,
                    'advanced_reports': False,
                }
            }
        )
        
        if created:
            self.stdout.write(f"✅ Created test tenant: {test_tenant}")
        else:
            self.stdout.write(f"ℹ️  Test tenant already exists: {test_tenant}")

        # Create admin users for tenants if they don't exist
        self.create_tenant_users()

        self.stdout.write("\n🎯 Tenant setup complete!")
        self.stdout.write("\n📝 Available tenants:")
        for tenant in Tenant.objects.all():
            self.stdout.write(f"   • {tenant.company_name} ({tenant.subdomain})")
            self.stdout.write(f"     Status: {tenant.subscription_status}")
            self.stdout.write(f"     Plan: {tenant.subscription_plan}")
            if tenant.trial_end_date:
                days_remaining = (tenant.trial_end_date - timezone.now()).days
                self.stdout.write(f"     Trial: {days_remaining} days remaining")
            self.stdout.write("")

        self.stdout.write("🌐 Access URLs:")
        self.stdout.write("   • Default: http://localhost:8000/employee-portal/")
        self.stdout.write("   • Demo: http://localhost:8000/tenant/demo/")
        self.stdout.write("   • ACME: http://localhost:8000/tenant/acme/")

    def create_tenant_users(self):
        """Create admin users for each tenant"""
        self.stdout.write("👥 Setting up tenant users...")
        
        # Get or create a system admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@system.com',
            defaults={
                'first_name': 'System',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f"✅ Created system admin: {admin_user.email}")

        # Add admin user to all tenants
        for tenant in Tenant.objects.all():
            tenant_user, created = TenantUser.objects.get_or_create(
                user=admin_user,
                tenant=tenant,
                defaults={'role': 'owner'}
            )
            
            if created:
                self.stdout.write(f"✅ Added {admin_user.email} as owner of {tenant.company_name}")
            
            # Set admin_user for tenant if not set
            if not tenant.admin_user:
                tenant.admin_user = admin_user
                tenant.save()
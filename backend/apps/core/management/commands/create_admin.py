from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import os
import sys

class Command(BaseCommand):
    help = "Create a superuser for the admin panel"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🚀 Starting superuser creation process...")
        )
        
        try:
            User = get_user_model()
            self.stdout.write(f"✅ User model loaded: {User.__name__}")
            
            # Get credentials from environment or use defaults
            email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "constantive@gmail.com")
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "September@2025.com")
            first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
            last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME", "User")
            
            self.stdout.write(f"📧 Email from env: {email}")
            self.stdout.write(f"🔒 Password length: {len(password)} chars")
            self.stdout.write(f"👤 Name: {first_name} {last_name}")
            
            # Debug: Check current users
            current_count = User.objects.count()
            self.stdout.write(f"📊 Current users in database: {current_count}")

            # Check if user with this email already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f"🔄 User with email {email} already exists! Updating...")
                )
                user = User.objects.get(email=email)
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ User with email {email} updated successfully!")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"🆕 Creating new superuser with email: {email}")
                )
                # Create new superuser - NOTE: No username field in this User model
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Superuser created successfully!")
                )
                
            # Verify creation
            final_count = User.objects.count()
            superuser_count = User.objects.filter(is_superuser=True).count()
            self.stdout.write(f"📊 Final user count: {final_count}")
            self.stdout.write(f"👑 Superuser count: {superuser_count}")
                
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Database integrity error: {e}")
            )
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Unexpected error: {e}")
            )
            sys.exit(1)

        self.stdout.write(
            self.style.SUCCESS("=" * 50)
        )
        self.stdout.write(
            self.style.SUCCESS("ADMIN LOGIN CREDENTIALS:")
        )
        self.stdout.write(
            self.style.SUCCESS(f"🔑 LOGIN EMAIL: {email}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"🔑 PASSWORD: {password}")
        )
        self.stdout.write(
            self.style.WARNING("📧 NOTE: Login using EMAIL address!")
        )
        self.stdout.write(
            self.style.WARNING("📧 This User model does NOT have username field!"))
        self.stdout.write(
            self.style.SUCCESS("🌐 Admin URL: /admin/")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 50)
        )
        
        # Also create the system admin user for tenants
        self.create_system_admin()
    
    def create_system_admin(self):
        """Create the system admin user for tenant management"""
        try:
            User = get_user_model()
            system_email = "admin@system.com"
            system_password = "admin123"
            
            if User.objects.filter(email=system_email).exists():
                self.stdout.write(
                    self.style.WARNING(f"🔄 System admin {system_email} already exists!")
                )
                user = User.objects.get(email=system_email)
                user.set_password(system_password)
                user.save()
            else:
                User.objects.create_user(
                    email=system_email,
                    password=system_password,
                    first_name="System",
                    last_name="Admin",
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f"✅ System admin created: {system_email}")
                )
                
            self.stdout.write(
                self.style.SUCCESS("🔑 ADDITIONAL LOGIN:")
            )
            self.stdout.write(
                self.style.SUCCESS(f"📧 EMAIL: {system_email}")
            )
            self.stdout.write(
                self.style.SUCCESS(f"🔒 PASSWORD: {system_password}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error creating system admin: {e}")
            )

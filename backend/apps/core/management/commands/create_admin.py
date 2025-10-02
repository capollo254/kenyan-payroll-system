from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create a superuser for the admin panel'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get credentials from environment or use defaults
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@company.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123456')

        # Check if user with this email already exists (since we authenticate by email)
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email "{email}" already exists! Updating...')
            )
            user = User.objects.get(email=email)
            user.set_password(password)
            user.username = username  # Update username too
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'User with email "{email}" updated successfully!')
            )
        else:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser created successfully!')
            )

        self.stdout.write(
            self.style.SUCCESS('=' * 50)
        )
        self.stdout.write(
            self.style.SUCCESS('ADMIN LOGIN CREDENTIALS:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'🔑 LOGIN EMAIL: {email}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'🔑 PASSWORD: {password}')
        )
        self.stdout.write(
            self.style.WARNING('📧 NOTE: Login using EMAIL address, not username!')
        )
        self.stdout.write(
            self.style.SUCCESS('🌐 Admin URL: /admin/')
        )
        self.stdout.write(
            self.style.SUCCESS('=' * 50)
        )
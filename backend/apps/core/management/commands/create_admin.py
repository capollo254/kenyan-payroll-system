from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Create a superuser for the admin panel'

    def handle(self, *args, **options):
        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Superuser already exists!')
            )
            return

        # Get credentials from environment or use defaults
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@lekohr.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123!')

        # Create superuser
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(f'Superuser "{username}" created successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Email: {email}')
        )
        self.stdout.write(
            self.style.WARNING('Password: [Check environment variable or use default]')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now login to /admin/ with these credentials.')
        )
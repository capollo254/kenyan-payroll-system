from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo users for testing'
    
    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Reset existing users')
    
    def handle(self, *args, **options):
        demo_users = [
            {
                'email': 'admin@demo.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'password': 'admin123',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'email': 'employee@demo.com', 
                'first_name': 'Employee',
                'last_name': 'User',
                'password': 'employee123',
                'is_staff': False,
                'is_superuser': False
            }
        ]
        
        if options['reset']:
            User.objects.filter(email__endswith='@demo.com').delete()
            self.stdout.write('Deleted existing demo users')
        
        for user_data in demo_users:
            email = user_data['email']
            password = user_data.pop('password')
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data
            )
            
            if created or options['reset']:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{"Created" if created else "Updated"} user: {email} (password: {password})'
                    )
                )
            else:
                self.stdout.write(f'User {email} already exists')
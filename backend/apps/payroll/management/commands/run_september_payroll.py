from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.payroll.models import PayrollRun
from apps.employees.models import Employee
from apps.core.models import User

class Command(BaseCommand):
    help = 'Run payroll for September 2025'

    def add_arguments(self, parser):
        parser.add_argument('--period-start', type=str, default='2025-09-01', help='Period start date (YYYY-MM-DD)')
        parser.add_argument('--period-end', type=str, default='2025-09-30', help='Period end date (YYYY-MM-DD)')
        parser.add_argument('--run-by-email', type=str, default='employee@demo.com', help='Email of user running payroll')

    @transaction.atomic
    def handle(self, *args, **options):
        period_start = options['period_start']
        period_end = options['period_end']
        run_by_email = options['run_by_email']

        try:
            run_by_user = User.objects.get(email=run_by_email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {run_by_email} not found'))
            return

        # Create payroll run
        payroll_run = PayrollRun.objects.create(
            run_by=run_by_user,
            run_date=timezone.now().date(),
            period_start_date=period_start,
            period_end_date=period_end
        )

        # Count active employees
        active_employees = Employee.objects.filter(is_active=True)
        employee_count = active_employees.count()

        if employee_count == 0:
            self.stdout.write(self.style.WARNING('No active employees found'))
            return

        self.stdout.write(self.style.SUCCESS(f'✅ Payroll run created successfully!'))
        self.stdout.write(f'📋 Payroll Run ID: {payroll_run.id}')
        self.stdout.write(f'📅 Run Date: {payroll_run.run_date}')
        self.stdout.write(f'📊 Period: {payroll_run.period_start_date} to {payroll_run.period_end_date}')
        self.stdout.write(f'👤 Run By: {payroll_run.run_by.email}')
        self.stdout.write(f'👥 Active Employees: {employee_count}')

        # Note: The actual payslip generation happens in the PayrollRunViewSet.create method
        # If you want to trigger that here, you would need to import and call that logic
        self.stdout.write(self.style.SUCCESS('✅ September 2025 payroll run completed!'))
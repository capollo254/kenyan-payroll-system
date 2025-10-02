# apps/leaves/management/commands/allocate_leaves.py

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.employees.models import Employee
from apps.leaves.models import LeaveType, LeaveBalance
from decimal import Decimal

class Command(BaseCommand):
    help = 'Allocate leave days to employees for a specific year'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=2025,
            help='Year for leave allocation (default: 2025)'
        )
        parser.add_argument(
            '--employee-id',
            type=int,
            help='Allocate to specific employee ID only'
        )
        parser.add_argument(
            '--leave-type',
            type=str,
            help='Allocate specific leave type code only (e.g., AL, SL)'
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Custom number of days to allocate (overrides default)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update existing allocations'
        )

    def handle(self, *args, **options):
        year = options['year']
        employee_id = options.get('employee_id')
        leave_type_code = options.get('leave_type')
        custom_days = options.get('days')
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting leave allocation for year {year}')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  DRY RUN MODE - No changes will be made')
            )

        try:
            with transaction.atomic():
                # Get employees to process
                if employee_id:
                    employees = Employee.objects.filter(id=employee_id)
                    if not employees.exists():
                        raise CommandError(f'Employee with ID {employee_id} not found')
                else:
                    employees = Employee.objects.all()

                # Get leave types to process
                if leave_type_code:
                    leave_types = LeaveType.objects.filter(code=leave_type_code, is_active=True)
                    if not leave_types.exists():
                        raise CommandError(f'Leave type with code {leave_type_code} not found')
                else:
                    leave_types = LeaveType.objects.filter(is_active=True)

                created_count = 0
                updated_count = 0
                skipped_count = 0

                for employee in employees:
                    self.stdout.write(f'\n👤 Processing: {employee.full_name()}')

                    for leave_type in leave_types:
                        # Determine allocation amount
                        allocation_days = custom_days if custom_days else leave_type.annual_allocation

                        try:
                            balance, created = LeaveBalance.objects.get_or_create(
                                employee=employee,
                                leave_type=leave_type,
                                year=year,
                                defaults={
                                    'allocated_days': Decimal(str(allocation_days)),
                                    'used_days': Decimal('0.0'),
                                    'pending_days': Decimal('0.0'),
                                    'carried_forward': Decimal('0.0')
                                }
                            )

                            if created:
                                if not dry_run:
                                    created_count += 1
                                self.stdout.write(
                                    f'  ✅ {"Would create" if dry_run else "Created"}: '
                                    f'{leave_type.name} - {allocation_days} days'
                                )
                            elif force:
                                if not dry_run:
                                    balance.allocated_days = Decimal(str(allocation_days))
                                    balance.save()
                                    updated_count += 1
                                self.stdout.write(
                                    f'  🔄 {"Would update" if dry_run else "Updated"}: '
                                    f'{leave_type.name} - {allocation_days} days '
                                    f'(was {balance.allocated_days})'
                                )
                            else:
                                skipped_count += 1
                                self.stdout.write(
                                    f'  ⏭️  Skipped: {leave_type.name} - '
                                    f'{balance.allocated_days} days (already exists)'
                                )

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'  ❌ Error processing {leave_type.name}: {e}')
                            )

                # Summary
                self.stdout.write(f'\n🎉 Allocation {"Preview" if dry_run else "Complete"}!')
                self.stdout.write(f'📊 {"Would create" if dry_run else "Created"}: {created_count} new allocations')
                self.stdout.write(f'📊 {"Would update" if dry_run else "Updated"}: {updated_count} allocations')
                self.stdout.write(f'📊 Skipped: {skipped_count} existing allocations')

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING('⚠️  Run without --dry-run to make actual changes')
                    )
                    # Rollback transaction in dry run mode
                    transaction.set_rollback(True)

        except Exception as e:
            raise CommandError(f'Error during allocation: {e}')
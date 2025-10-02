#!/usr/bin/env python
# Quick script to check leave types in the database

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.leaves.models import LeaveType

print("Checking Leave Types in Database:")
print("-" * 40)

leave_types = LeaveType.objects.all()
print(f"Total Leave Types: {leave_types.count()}")

for lt in leave_types:
    print(f"- {lt.name} ({lt.code}) - {lt.annual_allocation} days - Active: {lt.is_active}")

if leave_types.count() == 0:
    print("\nNo leave types found! Creating default leave types...")
    
    # Create default leave types
    default_types = [
        {
            'name': 'Annual Leave',
            'code': 'AL',
            'annual_allocation': 21,
            'carry_forward': True,
            'max_carry_forward': 5,
            'requires_approval': True,
            'is_paid': True
        },
        {
            'name': 'Sick Leave',
            'code': 'SL',
            'annual_allocation': 14,
            'carry_forward': False,
            'requires_approval': False,
            'is_paid': True
        },
        {
            'name': 'Maternity Leave',
            'code': 'ML',
            'annual_allocation': 90,
            'carry_forward': False,
            'requires_approval': True,
            'is_paid': True
        },
        {
            'name': 'Paternity Leave',
            'code': 'PL',
            'annual_allocation': 14,
            'carry_forward': False,
            'requires_approval': True,
            'is_paid': True
        },
        {
            'name': 'Emergency Leave',
            'code': 'EL',
            'annual_allocation': 3,
            'carry_forward': False,
            'requires_approval': True,
            'is_paid': True
        }
    ]
    
    for leave_type_data in default_types:
        leave_type, created = LeaveType.objects.get_or_create(
            code=leave_type_data['code'],
            defaults=leave_type_data
        )
        if created:
            print(f"✓ Created: {leave_type.name}")
        else:
            print(f"- Already exists: {leave_type.name}")
    
    print(f"\nFinal count: {LeaveType.objects.count()} leave types")
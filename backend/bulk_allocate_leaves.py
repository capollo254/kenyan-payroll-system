# Bulk Leave Allocation Script
# Run this in Django shell: python manage.py shell < bulk_allocate_leaves.py

from apps.employees.models import Employee
from apps.leaves.models import LeaveType, LeaveBalance
from decimal import Decimal
from datetime import datetime

def allocate_leaves_for_year(year=2025):
    """
    Allocate leave days to all employees for a specific year
    """
    print(f"🚀 Starting leave allocation for year {year}...")
    
    employees = Employee.objects.all()
    leave_types = LeaveType.objects.filter(is_active=True)
    
    created_count = 0
    updated_count = 0
    
    for employee in employees:
        print(f"\n👤 Processing: {employee.full_name()}")
        
        for leave_type in leave_types:
            balance, created = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                year=year,
                defaults={
                    'allocated_days': Decimal(str(leave_type.annual_allocation)),
                    'used_days': Decimal('0.0'),
                    'pending_days': Decimal('0.0'),
                    'carried_forward': Decimal('0.0')
                }
            )
            
            if created:
                created_count += 1
                print(f"  ✅ Created: {leave_type.name} - {leave_type.annual_allocation} days")
            else:
                updated_count += 1
                print(f"  ℹ️  Exists: {leave_type.name} - {balance.allocated_days} days")
    
    print(f"\n🎉 Allocation Complete!")
    print(f"📊 Created: {created_count} new allocations")
    print(f"📊 Existing: {updated_count} allocations")

def allocate_custom_leaves(employee_id, leave_type_code, days, year=2025):
    """
    Allocate custom leave days to a specific employee
    """
    try:
        employee = Employee.objects.get(id=employee_id)
        leave_type = LeaveType.objects.get(code=leave_type_code)
        
        balance, created = LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            year=year,
            defaults={'allocated_days': Decimal(str(days))}
        )
        
        if not created:
            balance.allocated_days = Decimal(str(days))
            balance.save()
        
        print(f"✅ Allocated {days} {leave_type.name} days to {employee.full_name()}")
        return balance
        
    except Employee.DoesNotExist:
        print(f"❌ Employee with ID {employee_id} not found")
    except LeaveType.DoesNotExist:
        print(f"❌ Leave type with code {leave_type_code} not found")

# Example usage:
if __name__ == "__main__":
    # Allocate standard leaves to all employees
    allocate_leaves_for_year(2025)
    
    # Example: Give extra days to specific employee
    # allocate_custom_leaves(employee_id=1, leave_type_code='AL', days=25, year=2025)
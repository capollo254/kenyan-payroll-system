#!/usr/bin/env python
import os
import django
from datetime import datetime, date
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee, JobInformation, VoluntaryDeduction
from apps.payroll.models import PayrollRun, Payslip

User = get_user_model()

def create_demo_employee_data():
    print("=== Creating Demo Employee Data ===")
    
    # Demo employee data
    demo_employee_data = [
        {
            'email': 'admin@demo.com',
            'employee_data': {
                'gross_salary': Decimal('120000.00'),  # KES 120,000
                'bank_account_number': '1234567890',
                'helb_monthly_deduction': Decimal('5000.00')
            },
            'job_data': {
                'company_employee_id': 'EMP001',
                'kra_pin': 'A012345678B',
                'nssf_number': 'NSSF001',
                'nhif_number': 'NHIF001',
                'department': 'Administration',
                'position': 'System Administrator',
                'date_of_joining': date(2023, 1, 15)
            }
        },
        {
            'email': 'employee@demo.com',
            'employee_data': {
                'gross_salary': Decimal('80000.00'),  # KES 80,000
                'bank_account_number': '9876543210',
                'helb_monthly_deduction': Decimal('3000.00')
            },
            'job_data': {
                'company_employee_id': 'EMP002',
                'kra_pin': 'A012345679C',
                'nssf_number': 'NSSF002',
                'nhif_number': 'NHIF002',
                'department': 'Finance',
                'position': 'Accountant',
                'date_of_joining': date(2023, 3, 1)
            }
        },
        {
            'email': 'demo@admin.com',
            'employee_data': {
                'gross_salary': Decimal('100000.00'),  # KES 100,000
                'bank_account_number': '5555666677',
                'helb_monthly_deduction': Decimal('4000.00')
            },
            'job_data': {
                'company_employee_id': 'EMP003',
                'kra_pin': 'A012345680D',
                'nssf_number': 'NSSF003',
                'nhif_number': 'NHIF003',
                'department': 'Human Resources',
                'position': 'HR Manager',
                'date_of_joining': date(2022, 11, 10)
            }
        }
    ]
    
    for user_data in demo_employee_data:
        email = user_data['email']
        user = User.objects.filter(email=email).first()
        
        if user:
            print(f"\n🔄 Processing {email}...")
            
            # Create or update employee profile
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults=user_data['employee_data']
            )
            
            if created:
                print(f"   ✅ Created Employee profile")
            else:
                print(f"   ℹ️  Employee profile already exists")
                # Update existing employee with new data
                for key, value in user_data['employee_data'].items():
                    setattr(employee, key, value)
                employee.save()
                print(f"   🔄 Updated employee data")
            
            # Create or update job information
            job_info, created = JobInformation.objects.get_or_create(
                employee=employee,
                defaults=user_data['job_data']
            )
            
            if created:
                print(f"   ✅ Created Job Information")
            else:
                print(f"   ℹ️  Job Information already exists")
                # Update existing job info
                for key, value in user_data['job_data'].items():
                    setattr(job_info, key, value)
                job_info.save()
                print(f"   🔄 Updated job information")
            
            print(f"   💰 Gross salary: KES {employee.gross_salary:,}")
            print(f"   🏢 Position: {job_info.position}")
            print(f"   🏦 Bank account: {employee.bank_account_number}")
        else:
            print(f"❌ User {email} not found")

if __name__ == '__main__':
    create_demo_employee_data()
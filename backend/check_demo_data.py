#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from apps.payroll.models import Payslip

User = get_user_model()

def check_demo_user_data():
    print("=== Checking Demo User Data ===")
    
    demo_users = ['admin@demo.com', 'employee@demo.com', 'demo@admin.com']
    
    for email in demo_users:
        user = User.objects.filter(email=email).first()
        if user:
            print(f"\n👤 User: {email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            
            # Check employee profile
            emp = Employee.objects.filter(user=user).first()
            if emp:
                print(f"   ✅ Employee profile exists")
                print(f"   💰 Gross salary: KES {emp.gross_salary}")
                print(f"   🏦 Bank account: {emp.bank_account_number or 'Not set'}")
                
                # Check payslips
                payslips = Payslip.objects.filter(employee=emp)
                print(f"   📄 Payslips: {payslips.count()}")
                
                if payslips.exists():
                    latest = payslips.first()
                    print(f"   💵 Latest net pay: KES {latest.net_pay}")
                
            else:
                print("   ❌ No employee profile found")
        else:
            print(f"\n❌ User {email} not found")

if __name__ == '__main__':
    check_demo_user_data()
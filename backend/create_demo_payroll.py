#!/usr/bin/env python
import os
import django
from datetime import datetime, date
from decimal import Decimal
from dateutil.relativedelta import relativedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from apps.payroll.models import PayrollRun, Payslip
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl

User = get_user_model()

def create_demo_payroll_data():
    print("=== Creating Demo Payroll Data ===")
    
    # Get demo employees
    demo_emails = ['admin@demo.com', 'employee@demo.com', 'demo@admin.com']
    demo_employees = []
    
    for email in demo_emails:
        user = User.objects.filter(email=email).first()
        if user and hasattr(user, 'employee_profile'):
            demo_employees.append(user.employee_profile)
    
    if not demo_employees:
        print("❌ No demo employees found. Run create_demo_employees.py first.")
        return
    
    # Create payroll runs for the last 3 months
    today = date.today()
    admin_user = User.objects.filter(is_staff=True).first()
    
    for i in range(3):  # Last 3 months
        month_date = today - relativedelta(months=i)
        period_start = month_date.replace(day=1)
        period_end = (period_start + relativedelta(months=1)) - relativedelta(days=1)
        
        print(f"\n📅 Creating payroll for {period_start.strftime('%B %Y')}")
        
        # Create payroll run
        payroll_run = PayrollRun.objects.filter(
            period_start_date=period_start,
            period_end_date=period_end
        ).first()
        
        if not payroll_run:
            payroll_run = PayrollRun.objects.create(
                period_start_date=period_start,
                period_end_date=period_end,
                run_date=period_end,
                run_by=admin_user,
                total_net_pay=Decimal('0.00'),
                total_deductions=Decimal('0.00')
            )
            print(f"   ✅ Created PayrollRun")
        else:
            print(f"   ℹ️  PayrollRun already exists")
        
        total_net_pay = Decimal('0.00')
        total_deductions = Decimal('0.00')
        
        # Create payslips for each demo employee
        for employee in demo_employees:
            print(f"   👤 Processing {employee.user.email}")
            
            # Check if payslip already exists
            existing_payslip = Payslip.objects.filter(
                payroll_run=payroll_run,
                employee=employee
            ).first()
            
            if existing_payslip:
                print(f"      ℹ️  Payslip already exists")
                total_net_pay += existing_payslip.net_pay
                total_deductions += existing_payslip.total_deductions
                continue
            
            gross_salary = employee.gross_salary
            overtime_pay = Decimal('5000.00') if i == 0 else Decimal('0.00')  # Current month has overtime
            total_gross = gross_salary + overtime_pay
            
            # Calculate statutory deductions using compliance functions
            try:
                # Import the calculation functions
                paye = calculate_paye(total_gross, employee.helb_monthly_deduction or Decimal('0.00'))
                nssf = calculate_nssf(gross_salary)
                shif = calculate_shif(gross_salary)
                ahl = calculate_ahl(gross_salary)
                helb = employee.helb_monthly_deduction or Decimal('0.00')
                
                total_deductions_emp = paye + nssf + shif + ahl + helb
                net_pay = total_gross - total_deductions_emp
                
            except Exception as e:
                print(f"      ⚠️  Error calculating deductions: {e}")
                # Fallback calculations
                paye = total_gross * Decimal('0.15')  # 15% PAYE estimate
                nssf = min(gross_salary * Decimal('0.06'), Decimal('2160.00'))  # 6% capped at 2160
                shif = gross_salary * Decimal('0.025')  # 2.5% SHIF
                ahl = gross_salary * Decimal('0.015')  # 1.5% AHL
                helb = employee.helb_monthly_deduction or Decimal('0.00')
                
                total_deductions_emp = paye + nssf + shif + ahl + helb
                net_pay = total_gross - total_deductions_emp
            
            # Create payslip
            payslip = Payslip.objects.create(
                payroll_run=payroll_run,
                employee=employee,
                gross_salary=gross_salary,
                overtime_pay=overtime_pay,
                total_gross_income=total_gross,
                paye_tax=paye,
                nssf_deduction=nssf,
                shif_deduction=shif,
                ahl_deduction=ahl,
                helb_deduction=helb,
                total_deductions=total_deductions_emp,
                net_pay=net_pay
            )
            
            total_net_pay += net_pay
            total_deductions += total_deductions_emp
            
            print(f"      💰 Gross: KES {total_gross:,.2f}")
            print(f"      🏦 Net Pay: KES {net_pay:,.2f}")
            print(f"      📊 Deductions: KES {total_deductions_emp:,.2f}")
        
        # Update payroll run totals
        payroll_run.total_net_pay = total_net_pay
        payroll_run.total_deductions = total_deductions
        payroll_run.save()
        
        print(f"   📈 Total Net Pay: KES {total_net_pay:,.2f}")

if __name__ == '__main__':
    create_demo_payroll_data()
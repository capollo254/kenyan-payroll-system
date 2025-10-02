# apps/payroll/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.employees.models import Employee, VoluntaryDeduction
from apps.payroll.models import PayrollRun, Payslip, PayslipDeduction
from apps.payroll.serializers import PayrollRunSerializer, PayslipSerializer, PayslipDetailedSerializer

# Import the calculation functions
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl
from apps.compliance.calc_overtime import calculate_overtime_pay
from apps.compliance.calc_reliefs import (
    calculate_insurance_relief,
    calculate_post_retirement_medical_deduction,
    calculate_mortgage_interest_relief
)

class PayrollRunViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollRunSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return payroll runs based on user permissions
        """
        user = self.request.user
        
        # Only superusers can see and create payroll runs
        if user.is_superuser:
            return PayrollRun.objects.all().order_by('-run_date')
        
        # Regular employees cannot see payroll runs
        return PayrollRun.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Only superusers can create payroll runs
        """
        if not request.user.is_superuser:
            return Response({"error": "Only administrators can create payroll runs."}, status=status.HTTP_403_FORBIDDEN)
        
        period_start = request.data.get('period_start_date')
        period_end = request.data.get('period_end_date')

        if not all([period_start, period_end]):
            return Response({"error": "period_start_date and period_end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        payroll_run = PayrollRun.objects.create(
            run_by=request.user,
            run_date=timezone.now().date(),
            period_start_date=period_start,
            period_end_date=period_end
        )

        employees = Employee.objects.filter(is_active=True)
        if not employees.exists():
            return Response({"error": "No active employees found to run payroll."}, status=status.HTTP_404_NOT_FOUND)

        for employee in employees:
            gross_salary = employee.gross_salary
            
            weekday_ot = Decimal(request.data.get(f'overtime_weekday_{employee.id}', '0.00'))
            weekend_ot = Decimal(request.data.get(f'overtime_weekend_{employee.id}', '0.00'))
            
            overtime_pay = calculate_overtime_pay(gross_salary, weekday_ot, weekend_ot)
            total_gross_income = gross_salary + overtime_pay
            
            # --- BEGIN PAYROLL CALCULATION LOGIC ---
            nssf_deduction = calculate_nssf(total_gross_income)
            shif_deduction = calculate_shif(total_gross_income)
            ahl_employee_deduction, ahl_employer_contribution = calculate_ahl(total_gross_income)
            helb_deduction = employee.helb_monthly_deduction if employee.helb_monthly_deduction else Decimal('0.00')

            # Assuming 'VoluntaryDeduction' for pension has a deduction_type of 'Pension'
            # and only one such deduction exists per employee.
            pension_contributions = VoluntaryDeduction.objects.filter(
                employee=employee,
                deduction_type__icontains='pension',
                is_active=True
            ).first()

            pension_deduction = Decimal('0.00')
            if pension_contributions:
                # Apply the tax-deductible cap of KES 30,000 per month
                PENSION_MAX_RELIEF = Decimal('30000.00')
                pension_deduction = min(pension_contributions.amount, PENSION_MAX_RELIEF)

            # Calculate additional reliefs as per KRA PAYE document
            medical_fund_deduction = calculate_post_retirement_medical_deduction(
                employee.monthly_medical_fund_contribution
            )
            mortgage_interest_relief = calculate_mortgage_interest_relief(
                employee.monthly_mortgage_interest
            )

            # CORRECTED: Subtract all mandatory and allowable voluntary deductions from gross income
            taxable_income = total_gross_income - (
                nssf_deduction + 
                shif_deduction + 
                ahl_employee_deduction + 
                pension_deduction +
                medical_fund_deduction +
                mortgage_interest_relief
            )

            # Ensure taxable income is not negative
            taxable_income = max(taxable_income, Decimal('0.00'))

            paye_tax = calculate_paye(taxable_income)
            
            # Calculate insurance relief (reduces PAYE tax)
            insurance_relief = calculate_insurance_relief(employee.monthly_insurance_premiums)
            paye_tax_after_relief = max(paye_tax - insurance_relief, Decimal('0.00'))
            
            # Calculate voluntary deductions (excluding pension as it's already accounted for in taxable income)
            voluntary_deductions_total = Decimal('0.00')
            voluntary_deductions = employee.voluntary_deductions.filter(is_active=True).exclude(deduction_type__icontains='pension')
            for deduction in voluntary_deductions:
                voluntary_deductions_total += deduction.amount

            # Total statutory deductions (using PAYE after insurance relief)
            total_statutory_deductions = paye_tax_after_relief + nssf_deduction + shif_deduction + ahl_employee_deduction + helb_deduction
            
            # Total deductions = statutory + voluntary (pension is already reflected in lower PAYE due to reduced taxable income)
            total_deductions = total_statutory_deductions + voluntary_deductions_total
            
            # Add pension deduction amount to total deductions for display purposes
            if pension_contributions and pension_contributions.amount > 0:
                total_deductions += pension_contributions.amount
            
            # Calculate net pay
            net_pay = total_gross_income - total_deductions
            
            # Ensure net pay is not negative
            net_pay = max(net_pay, Decimal('0.00'))
            # --- END PAYROLL CALCULATION LOGIC ---

            # --- Create Payslip Record ---
            payslip = Payslip.objects.create(
                payroll_run=payroll_run,
                employee=employee,
                gross_salary=gross_salary,
                overtime_pay=overtime_pay,
                total_gross_income=total_gross_income,
                paye_tax=paye_tax,
                nssf_deduction=nssf_deduction,
                shif_deduction=shif_deduction,
                ahl_deduction=ahl_employee_deduction,
                helb_deduction=helb_deduction,
                total_deductions=total_deductions,
                net_pay=net_pay
            )

            # Create individual deduction records for the payslip
            if paye_tax > 0:
                PayslipDeduction.objects.create(payslip=payslip, deduction_type='PAYE Tax', amount=paye_tax, is_statutory=True)
            if nssf_deduction > 0:
                PayslipDeduction.objects.create(payslip=payslip, deduction_type='NSSF', amount=nssf_deduction, is_statutory=True)
            if shif_deduction > 0:
                PayslipDeduction.objects.create(payslip=payslip, deduction_type='SHIF', amount=shif_deduction, is_statutory=True)
            if ahl_employee_deduction > 0:
                PayslipDeduction.objects.create(payslip=payslip, deduction_type='Affordable Housing Levy (AHL)', amount=ahl_employee_deduction, is_statutory=True)
            if helb_deduction > 0:
                PayslipDeduction.objects.create(payslip=payslip, deduction_type='HELB', amount=helb_deduction, is_statutory=True)

            # Create deduction record for pension contributions
            if pension_contributions and pension_contributions.amount > 0:
                PayslipDeduction.objects.create(
                    payslip=payslip,
                    deduction_type=pension_contributions.deduction_type,
                    amount=pension_contributions.amount,
                    is_statutory=False
                )
            
            # Create records for all other voluntary deductions (excluding pension)
            other_voluntary_deductions = employee.voluntary_deductions.filter(is_active=True).exclude(deduction_type__icontains='pension')
            for deduction in other_voluntary_deductions:
                PayslipDeduction.objects.create(
                    payslip=payslip,
                    deduction_type=deduction.deduction_type,
                    amount=deduction.amount,
                    is_statutory=False
                )

        # Update PayrollRun totals
        payroll_run.total_net_pay = sum(payslip.net_pay for payslip in payroll_run.payslips.all())
        payroll_run.total_deductions = sum(payslip.total_deductions for payslip in payroll_run.payslips.all())
        payroll_run.save()

        serializer = PayrollRunSerializer(payroll_run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# apps/payroll/views.py

... # (All other code remains the same) ...

class PayslipViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return payslips for the current user only
        """
        user = self.request.user
        
        # All authenticated users (including superusers) can only see their own payslips
        # Check if user has an employee profile
        if not hasattr(user, 'employee_profile'):
            return Payslip.objects.none()
        
        try:
            employee = user.employee_profile
            return Payslip.objects.filter(employee=employee).order_by('-payroll_run__run_date')
        except Exception:
            # If user has no employee profile, return empty queryset
            return Payslip.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to use detailed serializer
        """
        instance = self.get_object()
        serializer = PayslipDetailedSerializer(instance, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """
        Download payslip as PDF
        """
        try:
            payslip = self.get_object()
            
            # Import here to avoid circular imports
            from .pdf_generator import PayslipPDFGenerator
            
            # Generate and return PDF
            pdf_generator = PayslipPDFGenerator(payslip)
            return pdf_generator.generate_pdf()
            
        except Exception as e:
            return Response(
                {"error": f"Failed to generate PDF: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
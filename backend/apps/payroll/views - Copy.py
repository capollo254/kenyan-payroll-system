# apps/payroll/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.employees.models import Employee, VoluntaryDeduction
from apps.payroll.models import PayrollRun, Payslip, PayslipDeduction
from apps.payroll.serializers import PayrollRunSerializer, PayslipSerializer

# Import the calculation functions
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl
from apps.compliance.calc_overtime import calculate_overtime_pay

class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all().order_by('-run_date')
    serializer_class = PayrollRunSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        period_start = request.data.get('period_start_date')
        period_end = request.data.get('period_end_date')

        if not all([period_start, period_end]):
            return Response({"error": "period_start_date and period_end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        payroll_run = PayrollRun.objects.create(
            run_by=request.user,
            run_date=timezone.now(),
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
                pension_deduction = min(pension_contributions.monthly_amount, Decimal('30000.00'))

            # CORRECTED: Subtract all mandatory and allowable voluntary deductions from gross income
            taxable_income = total_gross_income - (
                nssf_deduction + 
                shif_deduction + 
                ahl_employee_deduction + 
                pension_deduction
            )

            # Ensure taxable income is not negative
            taxable_income = max(taxable_income, Decimal('0.00'))

            paye_tax = calculate_paye(taxable_income)
            
            voluntary_deductions_total = Decimal('0.00')
            voluntary_deductions = employee.voluntary_deductions.filter(is_active=True)
            for deduction in voluntary_deductions:
                voluntary_deductions_total += deduction.monthly_amount

            # Note: total_statutory_deductions and total_deductions now include the correct amounts
            total_statutory_deductions = paye_tax + nssf_deduction + shif_deduction + ahl_employee_deduction + helb_deduction
            total_deductions = total_statutory_deductions + voluntary_deductions_total
            net_pay = total_gross_income - total_deductions
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

            # Create deduction record for pension if it's considered here
            if pension_contributions and pension_contributions.monthly_amount > 0:
                PayslipDeduction.objects.create(
                    payslip=payslip,
                    deduction_type=pension_contributions.deduction_type,
                    amount=pension_contributions.monthly_amount,
                    is_statutory=False
                )
            
            # Create records for all other voluntary deductions
            other_voluntary_deductions = employee.voluntary_deductions.filter(is_active=True).exclude(deduction_type__icontains='pension')
            for deduction in other_voluntary_deductions:
                PayslipDeduction.objects.create(
                    payslip=payslip,
                    deduction_type=deduction.deduction_type,
                    amount=deduction.monthly_amount,
                    is_statutory=False
                )

        serializer = PayrollRunSerializer(payroll_run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PayslipViewSet(viewsets.ReadOnlyModelViewSet):
    # This class remains unchanged
    queryset = Payslip.objects.all().order_by('-payroll_run__run_date', 'employee__full_name')
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
            
        try:
            employee = Employee.objects.get(user=self.request.user)
            return queryset.filter(employee=employee)
        except Employee.DoesNotExist:
            return Payslip.objects.none()
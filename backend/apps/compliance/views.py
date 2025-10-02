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

# UNCOMMENT THE FOLLOWING IMPORTS
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
            
            # --- BEGIN PAYROLL CALCULATION LOGIC ---
            weekday_ot = Decimal(request.data.get(f'overtime_weekday_{employee.id}', '0.00'))
            weekend_ot = Decimal(request.data.get(f'overtime_weekend_{employee.id}', '0.00'))
            
            overtime_pay = calculate_overtime_pay(gross_salary, weekday_ot, weekend_ot)
            total_gross_income = gross_salary + overtime_pay
            
            # Calculate Statutory Deductions
            nssf_deduction = calculate_nssf(total_gross_income)
            shif_deduction = calculate_shif(total_gross_income)
            # UNPACK THE AHL CONTRIBUTION TUPLE
            ahl_employee_deduction, ahl_employer_contribution = calculate_ahl(total_gross_income)
            helb_deduction = employee.helb_monthly_deduction if employee.helb_monthly_deduction else Decimal('0.00')

            # Calculate Taxable Income and PAYE
            taxable_income = total_gross_income - nssf_deduction
            paye_tax = calculate_paye(taxable_income)
            
            # Calculate Voluntary Deductions
            voluntary_deductions_total = Decimal('0.00')
            for deduction in employee.voluntary_deductions.filter(is_active=True):
                voluntary_deductions_total += deduction.monthly_amount

            # Calculate Net Pay
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
                # ENSURE WE ONLY SAVE THE EMPLOYEE'S PORTION
                ahl_deduction=ahl_employee_deduction, 
                helb_deduction=helb_deduction,
                total_deductions=total_deductions,
                net_pay=net_pay
            )

            # Create individual deduction records for the payslip
            # ADD AHL AS A STATUTORY DEDUCTION RECORD
            PayslipDeduction.objects.create(
                payslip=payslip,
                deduction_type='Affordable Housing Levy (AHL)',
                amount=ahl_employee_deduction,
                is_statutory=True
            )
            
            # NSSF, SHIF, PAYE and HELB will be added as statutory deductions later...
            
            for deduction in employee.voluntary_deductions.filter(is_active=True):
                PayslipDeduction.objects.create(
                    payslip=payslip,
                    deduction_type=deduction.deduction_type,
                    amount=deduction.monthly_amount,
                    is_statutory=False
                )

        serializer = PayrollRunSerializer(payroll_run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PayslipViewSet(viewsets.ReadOnlyModelViewSet):
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
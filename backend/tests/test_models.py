# backend/tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

# Import all models from your apps
from apps.employees.models import Employee, JobInformation, VoluntaryDeduction
from apps.payroll.models import PayrollRun, Payslip, PayslipDeduction
from apps.notifications.models import Notification

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        """
        Create a base set of model instances for all tests.
        """
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        self.employee = Employee.objects.create(
            user=self.user,
            gross_salary=Decimal('50000.00')
        )
        self.job_info = JobInformation.objects.create(
            employee=self.employee,
            employee_id='EMP001',
            department='HR',
            position='Manager'
        )
        self.voluntary_deduction = VoluntaryDeduction.objects.create(
            employee=self.employee,
            deduction_type='sacco',
            monthly_amount=Decimal('5000.00')
        )
        self.payroll_run = PayrollRun.objects.create(
            run_by=self.user,
            period_start_date=timezone.now().date(),
            period_end_date=timezone.now().date()
        )
        self.payslip = Payslip.objects.create(
            payroll_run=self.payroll_run,
            employee=self.employee,
            gross_salary=Decimal('50000.00'),
            net_pay=Decimal('40000.00')
        )
        self.payslip_deduction = PayslipDeduction.objects.create(
            payslip=self.payslip,
            deduction_type='PAYE',
            amount=Decimal('5000.00'),
            is_statutory=True
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='This is a test notification.'
        )

    # ------------------ Employee App Tests ------------------

    def test_employee_creation(self):
        self.assertEqual(self.employee.user, self.user)
        self.assertEqual(self.employee.gross_salary, Decimal('50000.00'))

    def test_job_information_creation(self):
        self.assertEqual(self.job_info.employee, self.employee)
        self.assertEqual(self.job_info.department, 'HR')

    def test_voluntary_deduction_creation(self):
        self.assertEqual(self.voluntary_deduction.employee, self.employee)
        self.assertEqual(self.voluntary_deduction.monthly_amount, Decimal('5000.00'))

    def test_employee_str_method(self):
        self.assertEqual(str(self.employee), f"Employee for {self.user.email}")

    def test_employee_full_name_method(self):
        self.assertEqual(self.employee.full_name(), f"{self.user.first_name} {self.user.last_name}")

    # ------------------ Payroll App Tests ------------------

    def test_payroll_run_creation(self):
        self.assertEqual(self.payroll_run.run_by, self.user)
        self.assertEqual(self.payroll_run.total_net_pay, Decimal('0.00'))

    def test_payslip_creation(self):
        self.assertEqual(self.payslip.employee, self.employee)
        self.assertEqual(self.payslip.payroll_run, self.payroll_run)
        self.assertEqual(self.payslip.net_pay, Decimal('40000.00'))

    def test_payslip_deduction_creation(self):
        self.assertEqual(self.payslip_deduction.payslip, self.payslip)
        self.assertEqual(self.payslip_deduction.deduction_type, 'PAYE')
        self.assertTrue(self.payslip_deduction.is_statutory)

    def test_payroll_run_str_method(self):
        expected_str = f"Payroll Run for {self.payroll_run.period_start_date} to {self.payroll_run.period_end_date}"
        self.assertEqual(str(self.payroll_run), expected_str)

    def test_payslip_str_method(self):
        expected_str = f"Payslip for {self.employee.full_name()} ({self.payroll_run.run_date})"
        self.assertEqual(str(self.payslip), expected_str)

    # ------------------ Notification App Tests ------------------

    def test_notification_creation(self):
        self.assertEqual(self.notification.recipient, self.user)
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertFalse(self.notification.is_read)

    def test_notification_str_method(self):
        expected_str = f"[New Notification] for {self.user.email} at {self.notification.created_at.date()}"
        self.assertEqual(str(self.notification), expected_str)

    def test_on_delete_behavior(self):
        """
        Ensure that deleting a User does not cascade and delete their Employee profile.
        Also, ensure deleting a PayrollRun cascades to its Payslips.
        """
        # Test PROTECT behavior for Employee
        user_to_delete = User.objects.create_user(email='delete@test.com', password='pass')
        protected_employee = Employee.objects.create(user=user_to_delete, gross_salary=Decimal('1000'))
        
        with self.assertRaises(models.deletion.ProtectedError):
            user_to_delete.delete()
            
        # Test CASCADE behavior for PayrollRun
        payslip_id = self.payslip.id
        self.payroll_run.delete()
        
        with self.assertRaises(Payslip.DoesNotExist):
            Payslip.objects.get(id=payslip_id)
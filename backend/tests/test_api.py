# backend/tests/test_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.employees.models import Employee
from apps.payroll.models import PayrollRun, Payslip
from apps.notifications.models import Notification

User = get_user_model()

class APITests(APITestCase):
    def setUp(self):
        """
        Set up a superuser, a regular user, and an employee profile for testing.
        """
        # Create a superuser for testing admin-level access
        self.superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword'
        )
        # Create a regular user
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpassword'
        )
        # Create a second regular user for cross-user permission tests
        self.another_user = User.objects.create_user(
            email='another@example.com',
            password='anotherpassword'
        )

        # Create Employee profiles linked to the users
        self.employee = Employee.objects.create(
            user=self.regular_user,
            first_name='John',
            last_name='Doe',
            email='user@example.com',
            kra_pin='A123456789Z',
            nssf_number='NSSF98765',
            shif_number='SHIF98765'
        )
        self.another_employee = Employee.objects.create(
            user=self.another_user,
            first_name='Jane',
            last_name='Smith',
            email='another@example.com',
            kra_pin='B987654321A',
            nssf_number='NSSF12345',
            shif_number='SHIF12345'
        )

        # Create a payroll run and payslips for testing
        self.payroll_run = PayrollRun.objects.create(
            period_start_date='2025-01-01',
            period_end_date='2025-01-31',
            total_net_pay=Decimal('0.00'),
            total_deductions=Decimal('0.00')
        )
        self.payslip = Payslip.objects.create(
            payroll_run=self.payroll_run,
            employee=self.employee,
            gross_salary=Decimal('50000.00'),
            net_pay=Decimal('45000.00')
        )
        self.another_payslip = Payslip.objects.create(
            payroll_run=self.payroll_run,
            employee=self.another_employee,
            gross_salary=Decimal('60000.00'),
            net_pay=Decimal('55000.00')
        )

        # Create notifications for testing
        Notification.objects.create(
            recipient=self.regular_user,
            notification_type='payslip_published',
            title='Your January Payslip is Ready',
            message='Your latest payslip has been published.'
        )

        # Get API URLs
        self.employees_url = reverse('employee-list')
        self.payslips_url = reverse('payslip-list')
        self.payroll_runs_url = reverse('payroll-run-list')
        self.my_payslips_url = reverse('payslip-list')
        self.notifications_url = reverse('notification-list')

    def test_unauthenticated_access_is_forbidden(self):
        """
        Ensure unauthenticated requests are denied access to protected endpoints.
        """
        response = self.client.get(self.employees_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # ------------------ Employee API Tests ------------------

    def test_admin_can_list_all_employees(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.employees_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_regular_user_cannot_list_all_employees(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.employees_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_retrieve_own_employee_profile(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('employee-detail', args=[self.employee.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.regular_user.email)

    def test_regular_user_cannot_retrieve_another_employee_profile(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('employee-detail', args=[self.another_employee.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------ Payroll API Tests ------------------

    def test_admin_can_list_all_payslips(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.payslips_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_regular_user_can_list_own_payslips(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.my_payslips_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['employee']['email'], self.regular_user.email)

    def test_regular_user_cannot_retrieve_another_users_payslip(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('payslip-detail', args=[self.another_payslip.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------ Notifications API Tests ------------------

    def test_user_can_retrieve_their_notifications(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['is_read'], False)

    def test_user_can_mark_all_notifications_as_read(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('notification-mark-all-read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the notification is now marked as read
        notification = Notification.objects.get(recipient=self.regular_user)
        self.assertTrue(notification.is_read)

    def test_user_can_get_unread_notification_count(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('notification-unread-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

        # Mark as read and check again
        self.client.post(reverse('notification-mark-all-read'))
        response = self.client.get(url)
        self.assertEqual(response.data['unread_count'], 0)
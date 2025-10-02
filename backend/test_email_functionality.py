#!/usr/bin/env python
"""
Test script to check if email functionality is working
"""
import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.core.mail import send_mail

def test_email_sending():
    """Test if email sending functionality works"""
    
    print("Testing email functionality...")
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    
    # Test data (similar to your form submission)
    test_data = {
        'company_name': 'Apollo Car Imports Limited',
        'contact_name': 'FirstName LastName',
        'job_title': 'HR Manager',
        'email': 'apollocarimports@gmail.com',
        'phone': '+254711836874',
        'employee_count': '1-10',
        'industry': 'Automotive',
        'primary_interest': 'pricing'
    }
    
    # Test admin email
    print("\n--- Testing Admin Email ---")
    admin_subject = f"New Payroll System Inquiry from {test_data['company_name']}"
    admin_body = f"""
New inquiry received from Kenya Payroll System contact form:

COMPANY INFORMATION:
- Company: {test_data['company_name']}
- Contact Person: {test_data['contact_name']}
- Job Title: {test_data['job_title']}
- Email: {test_data['email']}
- Phone: {test_data['phone']}

REQUIREMENTS:
- Number of Employees: {test_data['employee_count']}
- Industry: {test_data['industry']}
- Primary Interest: {test_data['primary_interest']}

Please follow up with this potential client.
"""
    
    try:
        send_mail(
            admin_subject,
            admin_body,
            'noreply@localhost',
            ['constantive@gmail.com'],
            fail_silently=False,
        )
        print("✅ Admin email sent successfully!")
    except Exception as e:
        print(f"❌ Admin email failed: {e}")
    
    # Test confirmation email
    print("\n--- Testing Confirmation Email ---")
    confirmation_subject = "Thank you for your interest in Kenya Payroll System"
    confirmation_body = f"""
Dear {test_data['contact_name']},

Thank you for your interest in our Kenya Payroll System!

We have received your inquiry and will contact you within 24 hours.

Best regards,
Kenya Payroll System Team
"""
    
    try:
        send_mail(
            confirmation_subject,
            confirmation_body,
            'noreply@localhost',
            [test_data['email']],
            fail_silently=False,
        )
        print("✅ Confirmation email sent successfully!")
    except Exception as e:
        print(f"❌ Confirmation email failed: {e}")

    # Print Django email settings for debugging
    print("\n--- Django Email Settings ---")
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    
if __name__ == "__main__":
    test_email_sending()
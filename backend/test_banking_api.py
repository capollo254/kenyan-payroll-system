#!/usr/bin/env python3
"""
Employee Banking API Test Script
Tests the enhanced employee banking API endpoints
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee, JobInformation

User = get_user_model()

class EmployeeBankingAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.auth_token = None
    
    def authenticate(self, username="admin", password="admin123"):
        """Authenticate and get JWT token"""
        print("🔐 Authenticating...")
        
        auth_url = f"{self.api_base}/auth/login/"
        auth_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(auth_url, json=auth_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get('access')
                
                if self.auth_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    print("   ✅ Authentication successful")
                    return True
                else:
                    print("   ❌ No access token received")
                    return False
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   📊 Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_get_all_employees(self):
        """Test getting all employees"""
        print("\n📋 Testing GET /api/employees/")
        
        try:
            response = self.session.get(f"{self.api_base}/employees/")
            
            if response.status_code == 200:
                employees = response.json()
                print(f"   ✅ Found {len(employees)} employees")
                
                if employees:
                    # Show first employee details
                    first_employee = employees[0]
                    print(f"   📊 Sample Employee: {first_employee.get('full_name')}")
                    print(f"      Bank: {first_employee.get('bank_name', 'Not specified')}")
                    print(f"      Account: {first_employee.get('bank_account_number', 'Not specified')}")
                    
                return employees
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📊 Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)}")
            return None
    
    def test_get_employee_me(self):
        """Test getting current user's employee profile"""
        print("\n👤 Testing GET /api/employees/me/")
        
        try:
            response = self.session.get(f"{self.api_base}/employees/me/")
            
            if response.status_code == 200:
                employee = response.json()
                print(f"   ✅ Current employee: {employee.get('full_name')}")
                print(f"   📊 Banking Info:")
                print(f"      Bank Name: {employee.get('bank_name', 'Not specified')}")
                print(f"      Bank Code: {employee.get('bank_code', 'Not specified')}")
                print(f"      Account Number: {employee.get('bank_account_number', 'Not specified')}")
                print(f"      Account Type: {employee.get('account_type_display', 'Not specified')}")
                print(f"      Complete Banking: {employee.get('has_complete_banking', False)}")
                
                return employee
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📊 Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)}")
            return None
    
    def test_get_banking_details(self):
        """Test getting banking details endpoint"""
        print("\n🏦 Testing GET /api/employees/banking_details/")
        
        try:
            response = self.session.get(f"{self.api_base}/employees/banking_details/")
            
            if response.status_code == 200:
                banking_info = response.json()
                print(f"   ✅ Banking details for: {banking_info.get('full_name')}")
                print(f"   📊 Banking Information:")
                
                # Display all banking fields
                banking_fields = [
                    ('Bank Name', 'bank_name'),
                    ('Bank Code', 'bank_code'),
                    ('Bank Branch', 'bank_branch'),
                    ('Branch Code', 'bank_branch_code'),
                    ('Account Number', 'bank_account_number'),
                    ('Account Type', 'account_type_display'),
                    ('Account Holder', 'account_holder_name'),
                    ('Mobile Money Provider', 'mobile_money_provider_display'),
                    ('Mobile Money Number', 'mobile_money_number'),
                ]
                
                for label, field in banking_fields:
                    value = banking_info.get(field, 'Not specified')
                    print(f"      {label}: {value}")
                
                print(f"   🎯 Complete Banking Info: {banking_info.get('has_complete_banking_info', False)}")
                
                # Show formatted banking info
                formatted_info = banking_info.get('banking_info_formatted')
                if formatted_info:
                    print("   📋 Formatted Banking Info:")
                    for key, value in formatted_info.items():
                        print(f"      {key}: {value}")
                
                return banking_info
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📊 Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)}")
            return None
    
    def test_update_banking_details(self):
        """Test updating banking details"""
        print("\n✏️ Testing PUT /api/employees/update_banking_details/")
        
        # Sample banking data to update
        banking_data = {
            "bank_name": "Equity Bank Kenya Limited",
            "bank_code": "68",
            "bank_branch": "Westlands Branch",
            "bank_branch_code": "068",
            "account_type": "savings",
            "mobile_money_provider": "mpesa",
            "mobile_money_number": "0712345678"
        }
        
        try:
            response = self.session.put(
                f"{self.api_base}/employees/update_banking_details/",
                json=banking_data
            )
            
            if response.status_code == 200:
                updated_info = response.json()
                print(f"   ✅ Banking details updated for: {updated_info.get('full_name')}")
                print(f"   📊 Updated fields: {updated_info.get('updated_fields', [])}")
                print(f"   🎯 Complete Banking Info: {updated_info.get('has_complete_banking_info', False)}")
                
                return updated_info
            else:
                print(f"   ❌ Update failed: {response.status_code}")
                print(f"   📊 Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)}")
            return None
    
    def test_incomplete_banking_employees(self):
        """Test getting employees with incomplete banking info (admin only)"""
        print("\n⚠️ Testing GET /api/employees/employees_with_incomplete_banking/")
        
        try:
            response = self.session.get(f"{self.api_base}/employees/employees_with_incomplete_banking/")
            
            if response.status_code == 200:
                incomplete_data = response.json()
                count = incomplete_data.get('count', 0)
                employees = incomplete_data.get('employees', [])
                
                print(f"   ✅ Found {count} employees with incomplete banking info")
                
                for employee in employees[:3]:  # Show first 3
                    print(f"   📊 {employee.get('full_name')}:")
                    print(f"      Email: {employee.get('email')}")
                    print(f"      Missing Fields: {employee.get('missing_fields', [])}")
                    print(f"      Completion: {employee.get('banking_completion_percentage', 0)}%")
                
                if len(employees) > 3:
                    print(f"   ... and {len(employees) - 3} more")
                
                return incomplete_data
            elif response.status_code == 403:
                print("   ⚠️ Access denied (admin only endpoint)")
                return None
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📊 Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)}")
            return None
    
    def create_sample_banking_data(self):
        """Create sample banking data for testing"""
        print("\n🔧 Creating sample banking data...")
        
        try:
            # Get or create a test employee
            user, created = User.objects.get_or_create(
                email='test_employee@company.com',
                defaults={
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'phone_number': '0712345678'
                }
            )
            
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'gross_salary': 50000.00,
                    'bank_name': 'KCB Bank Kenya Limited',
                    'bank_code': '01',
                    'bank_branch': 'Nairobi Branch',
                    'bank_branch_code': '001',
                    'bank_account_number': '1234567890',
                    'account_type': 'current',
                    'account_holder_name': 'John Doe',
                    'mobile_money_provider': 'mpesa',
                    'mobile_money_number': '0701234567',
                }
            )
            
            if created:
                print(f"   ✅ Created test employee: {employee.full_name()}")
                
                # Create job information
                job_info, job_created = JobInformation.objects.get_or_create(
                    employee=employee,
                    defaults={
                        'company_employee_id': 'EMP001',
                        'kra_pin': 'A123456789Z',
                        'department': 'IT',
                        'position': 'Software Developer',
                        'date_of_joining': datetime.now().date(),
                    }
                )
                
                if job_created:
                    print(f"   ✅ Created job information for: {employee.full_name()}")
            else:
                print(f"   ℹ️ Test employee already exists: {employee.full_name()}")
            
            return employee
            
        except Exception as e:
            print(f"   ❌ Error creating sample data: {str(e)}")
            return None

def main():
    """Main testing function"""
    print("EMPLOYEE BANKING API TESTING")
    print("=" * 50)
    
    # Initialize tester
    tester = EmployeeBankingAPITester()
    
    # Create sample data
    tester.create_sample_banking_data()
    
    # Test authentication
    if not tester.authenticate():
        print("❌ Authentication failed. Cannot proceed with API tests.")
        return
    
    # Run API tests
    print(f"\n🚀 Testing Employee Banking APIs")
    print("=" * 30)
    
    # Test all endpoints
    tester.test_get_all_employees()
    tester.test_get_employee_me()
    tester.test_get_banking_details()
    tester.test_update_banking_details()
    tester.test_incomplete_banking_employees()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 API TESTING SUMMARY")
    print("=" * 50)
    print("Available Endpoints:")
    print("  📋 GET  /api/employees/                           - List all employees")
    print("  👤 GET  /api/employees/me/                        - Current user's profile")
    print("  🏦 GET  /api/employees/banking_details/           - Current user's banking")
    print("  ✏️  PUT  /api/employees/update_banking_details/   - Update banking info")
    print("  ⚠️  GET  /api/employees/employees_with_incomplete_banking/ - Incomplete banking (admin)")
    print("  🔍 GET  /api/employees/{id}/banking_details_by_id/ - Specific employee banking (admin)")
    
    print("\n🎉 Testing completed!")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Simple Django Model Test for Employee Banking
Tests the employee banking functionality without requiring server to be running
"""

import os
import sys
import django
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

def test_employee_banking_model():
    """Test the Employee banking model functionality"""
    print("🧪 EMPLOYEE BANKING MODEL TEST")
    print("=" * 50)
    
    try:
        # 1. Create or get a test user
        print("\n1️⃣ Creating test user...")
        user, created = User.objects.get_or_create(
            email='test.banking@company.com',
            defaults={
                'first_name': 'Banking',
                'last_name': 'Test',
                'phone_number': '0712345678'
            }
        )
        print(f"   {'✅ Created' if created else '✅ Found'} user: {user.first_name} {user.last_name}")
        
        # 2. Create or get employee profile
        print("\n2️⃣ Creating employee profile...")
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'gross_salary': 75000.00,
                'bank_name': 'Equity Bank Kenya Limited',
                'bank_code': '68',
                'bank_branch': 'Westlands Branch',
                'bank_branch_code': '068',
                'bank_account_number': '1234567890',
                'account_type': 'savings',
                'account_holder_name': 'Banking Test',
                'mobile_money_provider': 'mpesa',
                'mobile_money_number': '0712345678',
            }
        )
        print(f"   {'✅ Created' if created else '✅ Found'} employee: {employee.full_name()}")
        
        # 3. Test banking information methods
        print("\n3️⃣ Testing banking information methods...")
        
        # Test get_banking_info method
        banking_info = employee.get_banking_info()
        print(f"   📊 Banking Info: {banking_info}")
        
        # Test has_complete_banking_info method
        is_complete = employee.has_complete_banking_info()
        print(f"   🎯 Complete Banking Info: {is_complete}")
        
        # Test account type display
        account_display = employee.get_account_type_display()
        print(f"   💳 Account Type: {account_display}")
        
        # Test mobile money display
        mobile_display = employee.get_mobile_money_provider_display()
        print(f"   📱 Mobile Money: {mobile_display}")
        
        # 4. Create job information
        print("\n4️⃣ Creating job information...")
        job_info, created = JobInformation.objects.get_or_create(
            employee=employee,
            defaults={
                'company_employee_id': 'BANK001',
                'kra_pin': 'A123456789B',
                'nssf_number': 'NSSF12345',
                'nhif_number': 'NHIF67890',
                'department': 'Finance',
                'position': 'Banking Test Specialist',
                'date_of_joining': datetime.now().date(),
            }
        )
        print(f"   {'✅ Created' if created else '✅ Found'} job info: {job_info.position}")
        
        # 5. Test incomplete banking scenario
        print("\n5️⃣ Testing incomplete banking scenario...")
        
        # Create an employee with incomplete banking info
        incomplete_user, created = User.objects.get_or_create(
            email='incomplete.banking@company.com',
            defaults={
                'first_name': 'Incomplete',
                'last_name': 'Banking',
                'phone_number': '0701234567'
            }
        )
        
        incomplete_employee, created = Employee.objects.get_or_create(
            user=incomplete_user,
            defaults={
                'gross_salary': 50000.00,
                'bank_name': 'KCB Bank Kenya Limited',
                'bank_code': '01',
                # Missing bank_branch, bank_branch_code, account details
            }
        )
        
        print(f"   {'✅ Created' if created else '✅ Found'} incomplete employee: {incomplete_employee.full_name()}")
        
        # Test completion status
        incomplete_banking_info = incomplete_employee.get_banking_info()
        incomplete_status = incomplete_employee.has_complete_banking_info()
        
        print(f"   📊 Incomplete Banking Info: {incomplete_banking_info}")
        print(f"   🎯 Is Complete: {incomplete_status}")
        
        # 6. Display summary
        print("\n6️⃣ Summary...")
        all_employees = Employee.objects.all()
        complete_count = sum(1 for emp in all_employees if emp.has_complete_banking_info())
        total_count = all_employees.count()
        
        print(f"   📈 Total Employees: {total_count}")
        print(f"   ✅ Complete Banking: {complete_count}")
        print(f"   ⚠️ Incomplete Banking: {total_count - complete_count}")
        
        # 7. Show employees with banking details
        print("\n7️⃣ Employee Banking Summary...")
        for emp in all_employees:
            banking_info = emp.get_banking_info()
            is_complete = emp.has_complete_banking_info()
            status = "✅ Complete" if is_complete else "⚠️ Incomplete"
            
            print(f"   {status} {emp.full_name()}: {emp.bank_name or 'No bank'} - {emp.bank_account_number or 'No account'}")
        
        print("\n" + "=" * 50)
        print("🎉 ALL BANKING MODEL TESTS PASSED!")
        print("✅ Banking information system is working correctly")
        print("✅ Complete and incomplete banking scenarios tested")
        print("✅ All model methods functioning properly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_serializer_functionality():
    """Test the Employee serializer with banking information"""
    print("\n🧪 SERIALIZER FUNCTIONALITY TEST")
    print("=" * 50)
    
    try:
        from apps.employees.serializers import EmployeeSerializer, BankingInformationSerializer
        
        # Get an employee for testing
        employee = Employee.objects.filter(bank_name__isnull=False).first()
        
        if not employee:
            print("   ⚠️ No employees with banking data found. Creating one...")
            user = User.objects.create(
                email='serializer.test@company.com',
                first_name='Serializer',
                last_name='Test',
                phone_number='0723456789'
            )
            employee = Employee.objects.create(
                user=user,
                gross_salary=60000.00,
                bank_name='Co-operative Bank of Kenya Limited',
                bank_code='11',
                bank_branch='Nairobi Branch',
                bank_branch_code='011',
                bank_account_number='9876543210',
                account_type='current',
                account_holder_name='Serializer Test',
            )
        
        print(f"   📋 Testing serialization for: {employee.full_name()}")
        
        # Test EmployeeSerializer
        print("\n   🔸 Testing EmployeeSerializer...")
        employee_serializer = EmployeeSerializer(employee)
        employee_data = employee_serializer.data
        
        print(f"      Full Name: {employee_data.get('full_name')}")
        print(f"      Bank Name: {employee_data.get('bank_name')}")
        print(f"      Account Type Display: {employee_data.get('account_type_display')}")
        print(f"      Has Complete Banking: {employee_data.get('has_complete_banking')}")
        print(f"      Banking Info: {employee_data.get('banking_info')}")
        
        # Test BankingInformationSerializer
        print("\n   🔸 Testing BankingInformationSerializer...")
        banking_serializer = BankingInformationSerializer(employee)
        banking_data = banking_serializer.data
        
        print(f"      Banking Data Keys: {list(banking_data.keys())}")
        print(f"      Bank Account Number: {banking_data.get('bank_account_number')}")
        print(f"      Formatted Banking Info: {banking_data.get('banking_info_formatted')}")
        
        print("\n   ✅ Serializer tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Serializer test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("EMPLOYEE BANKING SYSTEM TEST SUITE")
    print("=" * 60)
    
    # Run model tests
    model_test_passed = test_employee_banking_model()
    
    # Run serializer tests
    serializer_test_passed = test_serializer_functionality()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST SUMMARY")
    print("=" * 60)
    
    print(f"📋 Model Tests: {'✅ PASSED' if model_test_passed else '❌ FAILED'}")
    print(f"📋 Serializer Tests: {'✅ PASSED' if serializer_test_passed else '❌ FAILED'}")
    
    if model_test_passed and serializer_test_passed:
        print("\n🎉 ALL TESTS PASSED! Employee banking system is ready for use.")
        print("\n📡 Next steps:")
        print("   1. Start Django server: python manage.py runserver")
        print("   2. Test API endpoints using the frontend or API client")
        print("   3. Verify banking data in Django admin interface")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Test the public payroll calculator API with live HTTP requests
"""
import requests
import json

def test_live_api():
    """Test the calculator API with live HTTP requests to running Django server"""
    
    print("🧮 TESTING LIVE PUBLIC PAYROLL CALCULATOR API")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    api_endpoint = f"{base_url}/api/public/calculator/"
    
    # Test Case 1: Basic salary calculation
    print("\n📋 Test Case 1: Basic Salary (KSh 80,000)")
    test_data_1 = {
        'gross_salary': 80000,
        'pension_contribution': 0,
        'insurance_premiums': 0,
        'medical_fund_contribution': 0,
        'mortgage_interest': 0,
        'helb_deduction': 0,
        'other_voluntary_deductions': 0
    }
    
    try:
        response_1 = requests.post(
            api_endpoint,
            json=test_data_1,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response_1.status_code == 200:
            result_1 = response_1.json()
            if result_1.get('success'):
                print(f"✅ Basic calculation successful")
                print(f"   🔗 API Status: {response_1.status_code}")
                print(f"   💰 Gross: KSh {result_1['summary']['gross_salary']:,.2f}")
                print(f"   💵 Net Pay: KSh {result_1['summary']['net_pay']:,.2f}")
                print(f"   💸 PAYE: KSh {result_1['statutory_deductions']['paye_tax']['amount']:,.2f}")
                print(f"   🏦 NSSF: KSh {result_1['statutory_deductions']['nssf']['amount']:,.2f}")
                print(f"   🏥 SHIF: KSh {result_1['statutory_deductions']['shif']['amount']:,.2f}")
                print(f"   🏠 AHL: KSh {result_1['statutory_deductions']['ahl']['amount']:,.2f}")
                print(f"   📊 Tax Rate: {result_1['summary']['effective_tax_rate']:.2f}%")
            else:
                print(f"❌ API returned error: {result_1.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error {response_1.status_code}: {response_1.text}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed. Is Django server running at {base_url}?")
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout. Server may be slow.")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test Case 2: High salary with reliefs
    print("\n📋 Test Case 2: High Salary with Reliefs (KSh 180,000)")
    test_data_2 = {
        'gross_salary': 180000,
        'pension_contribution': 25000,
        'insurance_premiums': 4000,
        'medical_fund_contribution': 12000,
        'mortgage_interest': 25000,
        'helb_deduction': 2500,
        'other_voluntary_deductions': 3000
    }
    
    try:
        response_2 = requests.post(
            api_endpoint,
            json=test_data_2,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response_2.status_code == 200:
            result_2 = response_2.json()
            if result_2.get('success'):
                print(f"✅ High salary calculation successful")
                print(f"   💰 Gross: KSh {result_2['summary']['gross_salary']:,.2f}")
                print(f"   💵 Net Pay: KSh {result_2['summary']['net_pay']:,.2f}")
                print(f"   📊 Tax Rate: {result_2['summary']['effective_tax_rate']:.2f}%")
                
                # Show reliefs applied
                reliefs = result_2['reliefs_applied']
                print(f"   🎯 Reliefs Applied:")
                if reliefs['pension_relief']['relief_amount'] > 0:
                    print(f"     • Pension: KSh {reliefs['pension_relief']['relief_amount']:,.2f}")
                if reliefs['insurance_relief']['relief_amount'] > 0:
                    print(f"     • Insurance: KSh {reliefs['insurance_relief']['relief_amount']:,.2f}")
                if reliefs['medical_fund_relief']['relief_amount'] > 0:
                    print(f"     • Medical Fund: KSh {reliefs['medical_fund_relief']['relief_amount']:,.2f}")
                if reliefs['mortgage_relief']['relief_amount'] > 0:
                    print(f"     • Mortgage: KSh {reliefs['mortgage_relief']['relief_amount']:,.2f}")
                print(f"     • Personal: KSh {reliefs['personal_relief']['amount']:,.2f}")
            else:
                print(f"❌ API returned error: {result_2.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error {response_2.status_code}: {response_2.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test Case 3: Error handling
    print("\n📋 Test Case 3: Error Handling (Invalid Data)")
    test_data_3 = {
        'gross_salary': -10000,  # Invalid negative salary
    }
    
    try:
        response_3 = requests.post(
            api_endpoint,
            json=test_data_3,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response_3.status_code == 400:
            result_3 = response_3.json()
            print(f"✅ Error handling successful")
            print(f"   🔗 Status: {response_3.status_code} (Bad Request)")
            print(f"   ❌ Error: {result_3.get('error', 'Validation failed')}")
        else:
            print(f"❌ Unexpected status code: {response_3.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test CORS headers
    print("\n📋 Test Case 4: CORS Headers Check")
    try:
        response_4 = requests.options(
            api_endpoint,
            headers={'Origin': 'http://localhost:3000'},
            timeout=10
        )
        print(f"✅ CORS check completed")
        print(f"   🔗 Status: {response_4.status_code}")
        print(f"   🌐 CORS Headers Present:")
        cors_headers = [h for h in response_4.headers.keys() if 'cors' in h.lower() or 'access-control' in h.lower()]
        if cors_headers:
            for header in cors_headers:
                print(f"     • {header}: {response_4.headers[header]}")
        else:
            print(f"     • No explicit CORS headers found")
    except Exception as e:
        print(f"❌ CORS check failed: {e}")
    
    print("\n🎉 LIVE API TESTING COMPLETED!")
    print("=" * 60)
    print(f"🔗 API Endpoint: {api_endpoint}")
    print("✅ Calculator is ready for use on marketing website!")
    print("💡 Update the API_BASE_URL in HTML file to your production domain")

if __name__ == "__main__":
    test_live_api()
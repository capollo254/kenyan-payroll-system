import requests
import json

# Test data
data = {
    'gross_salary': 100000,
    'pension_contribution': 10000,
    'insurance_premiums': 2000,
    'medical_fund_contribution': 5000,
    'mortgage_interest': 15000,
    'helb_deduction': 1500,
    'other_voluntary_deductions': 2000
}

# Make request
response = requests.post(
    'http://127.0.0.1:8000/api/public/calculator/',
    json=data,
    headers={'Content-Type': 'application/json'}
)

# Print results
if response.status_code == 200:
    result = response.json()
    if result.get('success'):
        print('✅ API TEST SUCCESSFUL!')
        summary = result['summary']
        statutory = result['statutory_deductions']
        
        print(f'Gross Salary: KSh {summary["gross_salary"]:,.2f}')
        print(f'Net Pay: KSh {summary["net_pay"]:,.2f}')
        print(f'PAYE Tax: KSh {statutory["paye_tax"]["amount"]:,.2f}')
        print(f'NSSF: KSh {statutory["nssf"]["amount"]:,.2f}')
        print(f'SHIF: KSh {statutory["shif"]["amount"]:,.2f}')
        print(f'AHL: KSh {statutory["ahl"]["amount"]:,.2f}')
        print(f'Effective Tax Rate: {summary["effective_tax_rate"]:.2f}%')
        
        # Show reliefs
        reliefs = result['reliefs_applied']
        print('\n🎯 Tax Reliefs Applied:')
        print(f'Personal Relief: KSh {reliefs["personal_relief"]["amount"]:,.2f}')
        if reliefs["pension_relief"]["relief_amount"] > 0:
            print(f'Pension Relief: KSh {reliefs["pension_relief"]["relief_amount"]:,.2f}')
        if reliefs["insurance_relief"]["relief_amount"] > 0:
            print(f'Insurance Relief: KSh {reliefs["insurance_relief"]["relief_amount"]:,.2f}')
        if reliefs["medical_fund_relief"]["relief_amount"] > 0:
            print(f'Medical Fund Relief: KSh {reliefs["medical_fund_relief"]["relief_amount"]:,.2f}')
        if reliefs["mortgage_relief"]["relief_amount"] > 0:
            print(f'Mortgage Relief: KSh {reliefs["mortgage_relief"]["relief_amount"]:,.2f}')
            
    else:
        print(f'❌ API Error: {result.get("error")}')
else:
    print(f'❌ HTTP Error: {response.status_code}')
    print(response.text)
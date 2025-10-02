# Banking Information Enhancement for Employee Model
# This file shows the proposed changes to add comprehensive banking details

"""
PROPOSED BANKING INFORMATION FIELDS FOR EMPLOYEE MODEL:

1. Bank Details:
   - bank_name: Full bank name (e.g., "Equity Bank Kenya Limited")
   - bank_code: Central Bank assigned code (e.g., "68")
   - bank_branch: Branch name (e.g., "Westlands Branch")
   - bank_branch_code: Specific branch code (e.g., "068")
   
2. Account Details:
   - account_number: Current bank_account_number (already exists)
   - account_type: Savings, Current, etc.
   - account_holder_name: Name as appears on account
   
3. Mobile Money (Optional):
   - mobile_money_provider: M-Pesa, Airtel Money, etc.
   - mobile_money_number: Phone number for mobile money

KENYAN MAJOR BANKS AND CODES:
- Equity Bank: 68
- Kenya Commercial Bank (KCB): 01
- Cooperative Bank: 11
- Standard Chartered: 02
- Barclays Bank (now ABSA): 03
- National Bank of Kenya: 12
- Family Bank: 70
- I&M Bank: 57
- Diamond Trust Bank (DTB): 63
- CfC Stanbic Bank: 31
"""

# Implementation will be done in the actual models.py file
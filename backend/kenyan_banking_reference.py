# Kenyan Banking Reference Guide
# For use with the Enhanced Banking Information System

"""
MAJOR KENYAN BANKS AND THEIR CODES (Central Bank of Kenya Assigned)
==================================================================

TIER 1 BANKS (Large Commercial Banks):
- Equity Bank Kenya Limited: Code 68
- Kenya Commercial Bank (KCB): Code 01
- Cooperative Bank of Kenya: Code 11
- Standard Chartered Bank Kenya: Code 02
- ABSA Bank Kenya (formerly Barclays): Code 03

TIER 2 BANKS (Medium Commercial Banks):
- National Bank of Kenya: Code 12
- Family Bank Limited: Code 70
- I&M Bank Limited: Code 57
- Diamond Trust Bank Kenya: Code 63
- CfC Stanbic Bank: Code 31
- Commercial Bank of Africa: Code 67 (merged with NIC Bank)
- NIC Bank: Code 41 (merged with Commercial Bank of Africa)
- Prime Bank Limited: Code 10
- Guardian Bank Limited: Code 55
- Bank of Africa Kenya: Code 51

TIER 3 BANKS (Small Commercial Banks):
- African Banking Corporation: Code 35
- Bank of India: Code 53
- Bank of Baroda: Code 06
- Citibank N.A. Kenya: Code 16
- Consolidated Bank of Kenya: Code 23
- Development Bank of Kenya: Code 04
- Ecobank Kenya: Code 43
- First Community Bank: Code 74
- Gulf African Bank: Code 72
- Habib Bank AG Zurich: Code 21
- HFC Limited: Code 50
- Middle East Bank Kenya: Code 18
- Paramount Universal Bank: Code 44
- SBM Bank Kenya: Code 58
- Sidian Bank: Code 76
- UBA Kenya Bank: Code 76
- Victoria Commercial Bank: Code 54

ISLAMIC BANKS:
- Dubai Islamic Bank Kenya: Code 78
- First Community Bank (Islamic Banking): Code 74
- Gulf African Bank (Islamic Banking): Code 72

MICROFINANCE INSTITUTIONS (MFI):
- Kenya Women Microfinance Bank: Code 79
- Faulu Microfinance Bank: Code 81
- SMEP Microfinance Bank: Code 82
- Rafiki Microfinance Bank: Code 83

MOBILE MONEY PROVIDERS:
======================
- M-Pesa (Safaricom): Most widely used
- Airtel Money (Airtel Kenya): Second largest
- T-Kash (Telkom Kenya): Third option
- Equitel (Equity Bank): Bank-integrated mobile money

ACCOUNT TYPES:
=============
- Savings Account: Most common for salary payments
- Current Account: For business transactions and higher liquidity
- Fixed Deposit Account: For long-term savings (rare for salary)

IMPLEMENTATION NOTES:
====================
1. Bank codes are standardized by Central Bank of Kenya
2. Branch codes are bank-specific (each bank has its own system)
3. Account numbers vary by bank (some 10-15 digits)
4. SWIFT codes are different from local bank codes
5. Mobile money integration provides backup payment method

VALIDATION RECOMMENDATIONS:
===========================
1. Verify bank code against CBK official list
2. Validate account number length per bank requirements
3. Cross-check account holder name with employee records
4. Implement bank-specific validation rules where possible
5. Provide dropdown for common banks to avoid typos

PAYROLL INTEGRATION:
==================
1. Primary: Bank account for salary deposits
2. Backup: Mobile money for emergency payments
3. Verification: Account holder name matching
4. Compliance: CBK regulations for electronic transfers
"""

# This information can be used to create dropdown choices or validation rules
KENYAN_MAJOR_BANKS = [
    ('68', 'Equity Bank Kenya Limited'),
    ('01', 'Kenya Commercial Bank (KCB)'),
    ('11', 'Cooperative Bank of Kenya'),
    ('02', 'Standard Chartered Bank Kenya'),
    ('03', 'ABSA Bank Kenya'),
    ('12', 'National Bank of Kenya'),
    ('70', 'Family Bank Limited'),
    ('57', 'I&M Bank Limited'),
    ('63', 'Diamond Trust Bank Kenya'),
    ('31', 'CfC Stanbic Bank'),
    ('67', 'Commercial Bank of Africa'),
    ('41', 'NIC Bank'),
    ('10', 'Prime Bank Limited'),
    ('55', 'Guardian Bank Limited'),
    ('51', 'Bank of Africa Kenya'),
]

MOBILE_MONEY_PROVIDERS = [
    ('mpesa', 'M-Pesa (Safaricom)'),
    ('airtel', 'Airtel Money'),
    ('tkash', 'T-Kash (Telkom)'),
    ('equitel', 'Equitel'),
]

ACCOUNT_TYPES = [
    ('savings', 'Savings Account'),
    ('current', 'Current Account'),
    ('fixed', 'Fixed Deposit Account'),
]
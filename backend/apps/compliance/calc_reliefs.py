# compliance/calc_reliefs.py
from decimal import Decimal
from .rates import (
    INSURANCE_RELIEF_RATE, INSURANCE_RELIEF_MAX_MONTHLY,
    POST_RETIREMENT_MEDICAL_MAX, MORTGAGE_INTEREST_MAX
)

def calculate_insurance_relief(insurance_premiums_paid):
    """
    Calculates insurance relief at 15% of premiums paid up to KSh 5,000 monthly.
    
    Args:
        insurance_premiums_paid (Decimal): Monthly insurance premiums paid by employee.
        
    Returns:
        Decimal: The calculated insurance relief amount.
    """
    if insurance_premiums_paid <= Decimal('0'):
        return Decimal('0.00')
    
    # Calculate 15% of premiums paid
    relief_amount = insurance_premiums_paid * INSURANCE_RELIEF_RATE
    
    # Cap at maximum monthly relief
    return min(relief_amount, INSURANCE_RELIEF_MAX_MONTHLY)

def calculate_post_retirement_medical_deduction(medical_fund_contribution):
    """
    Calculates allowable post-retirement medical fund deduction up to KSh 15,000 monthly.
    
    Args:
        medical_fund_contribution (Decimal): Monthly contribution to post-retirement medical fund.
        
    Returns:
        Decimal: The allowable deduction amount.
    """
    if medical_fund_contribution <= Decimal('0'):
        return Decimal('0.00')
    
    # Cap at maximum monthly deduction
    return min(medical_fund_contribution, POST_RETIREMENT_MEDICAL_MAX)

def calculate_mortgage_interest_relief(mortgage_interest_paid):
    """
    Calculates allowable mortgage interest relief up to KSh 30,000 monthly.
    
    Args:
        mortgage_interest_paid (Decimal): Monthly mortgage interest paid by employee.
        
    Returns:
        Decimal: The allowable relief amount.
    """
    if mortgage_interest_paid <= Decimal('0'):
        return Decimal('0.00')
    
    # Cap at maximum monthly relief
    return min(mortgage_interest_paid, MORTGAGE_INTEREST_MAX)
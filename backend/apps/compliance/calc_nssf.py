# compliance/calc_nssf.py
from decimal import Decimal
from .rates import NSSF_RATE, NSSF_LOWER_EARNINGS_LIMIT, NSSF_UPPER_EARNINGS_LIMIT

def calculate_nssf(gross_salary):
    """
    Calculates NSSF contribution based on the new rates (Tier I and Tier II).
    
    Args:
        gross_salary (Decimal): The employee's gross income.
        
    Returns:
        Decimal: The calculated NSSF deduction.
    """
    nssf_deduction = Decimal('0.00')

    # Tier I contribution (up to the lower earnings limit)
    tier_i_income = min(gross_salary, NSSF_LOWER_EARNINGS_LIMIT)
    nssf_deduction += tier_i_income * NSSF_RATE
    
    # Tier II contribution (from lower to upper earnings limit)
    if gross_salary > NSSF_LOWER_EARNINGS_LIMIT:
        tier_ii_income = min(gross_salary - NSSF_LOWER_EARNINGS_LIMIT, NSSF_UPPER_EARNINGS_LIMIT - NSSF_LOWER_EARNINGS_LIMIT)
        nssf_deduction += tier_ii_income * NSSF_RATE
    
    return nssf_deduction
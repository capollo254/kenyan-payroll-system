# compliance/calc_paye.py
from decimal import Decimal
from .rates import PAYE_RATES, PAYE_PERSONAL_RELIEF

def calculate_paye(taxable_income):
    """
    Calculates PAYE based on the current Kenyan tax bands.
    
    Args:
        taxable_income (Decimal): The employee's income after all deductions.
        
    Returns:
        Decimal: The calculated PAYE tax.
    """
    paye = Decimal('0.00')
    remaining_income = taxable_income
    
    for band_limit, rate in PAYE_RATES:
        if remaining_income <= Decimal('0'):
            break
            
        # Handle the `inf` case for the highest tax band
        if band_limit == Decimal('inf'):
            taxable_in_band = remaining_income
        else:
            taxable_in_band = min(remaining_income, band_limit)
        
        paye += taxable_in_band * rate
        remaining_income -= taxable_in_band
        
    # Subtract personal relief from the total PAYE
    final_paye = paye - PAYE_PERSONAL_RELIEF
    
    # PAYE cannot be negative
    return max(final_paye, Decimal('0.00'))
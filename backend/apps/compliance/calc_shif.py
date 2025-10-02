# compliance/calc_shif.py
from decimal import Decimal
from .rates import SHIF_RATE, SHIF_MINIMUM_CONTRIBUTION

def calculate_shif(gross_salary):
    """
    Calculates the Social Health Insurance Fund (SHIF) contribution for a salaried employee.

    The calculation is based on the new legal framework where SHIF replaced NHIF.
    The contribution is 2.75% of the gross salary, with a minimum monthly contribution.

    Args:
        gross_salary (Decimal): The employee's gross monthly salary.

    Returns:
        Decimal: The final SHIF contribution amount to be deducted.
    """
    # Calculate the contribution based on the fixed rate
    shif_contribution = gross_salary * SHIF_RATE
    
    # Apply the minimum contribution rule. The employee pays the higher of the
    # calculated amount or the minimum.
    final_shif_contribution = max(shif_contribution, SHIF_MINIMUM_CONTRIBUTION)
    
    return final_shif_contribution
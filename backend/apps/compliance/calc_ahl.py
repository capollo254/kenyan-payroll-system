# compliance/calc_ahl.py
from decimal import Decimal
from .rates import AHL_RATE

def calculate_ahl(gross_salary):
    """
    Calculates the mandatory Affordable Housing Levy (AHL) for both the employee and employer.

    The calculation is based on the legal framework where the levy is 1.5% of the
    employee's gross monthly salary, with a matching contribution from the employer.

    Args:
        gross_salary (Decimal): The employee's total gross monthly salary.

    Returns:
        tuple: A tuple containing the employee's contribution and the employer's contribution.
    """
    # The contribution is a fixed percentage of the gross salary.
    contribution = gross_salary * AHL_RATE
    
    # Both employee and employer contribute the same amount.
    return (contribution, contribution)
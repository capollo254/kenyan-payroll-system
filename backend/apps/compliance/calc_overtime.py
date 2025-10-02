# compliance/calc_overtime.py
from decimal import Decimal
from .rates import (
    MONTHLY_WORKING_HOURS,
    OVERTIME_WEEKDAY_MULTIPLIER,
    OVERTIME_WEEKEND_MULTIPLIER
)

def calculate_overtime_pay(gross_salary, weekday_hours, weekend_hours):
    """
    Calculates total overtime pay based on hours worked on weekdays and weekends/holidays.

    Args:
        gross_salary (Decimal): The employee's gross monthly salary.
        weekday_hours (Decimal): The number of overtime hours worked on normal weekdays.
        weekend_hours (Decimal): The number of overtime hours worked on rest days or public holidays.

    Returns:
        Decimal: The total overtime pay for the period.
    """
    # If no overtime hours were worked, return 0.
    if weekday_hours <= 0 and weekend_hours <= 0:
        return Decimal('0.00')

    # Handle the edge case of a zero gross salary to prevent a ZeroDivisionError.
    if gross_salary <= 0:
        return Decimal('0.00')
    
    # Calculate the base hourly rate using the constant from rates.py.
    normal_hourly_rate = gross_salary / MONTHLY_WORKING_HOURS
    
    # Calculate pay for weekday overtime.
    weekday_ot_pay = weekday_hours * normal_hourly_rate * OVERTIME_WEEKDAY_MULTIPLIER
    
    # Calculate pay for weekend/holiday overtime.
    weekend_ot_pay = weekend_hours * normal_hourly_rate * OVERTIME_WEEKEND_MULTIPLIER
    
    # Return the sum of all overtime pay.
    return weekday_ot_pay + weekend_ot_pay
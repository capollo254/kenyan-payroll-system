# backend/tests/test_compliance.py

from django.test import TestCase
from decimal import Decimal

# Import the compliance functions you've created
from compliance.calc_paye import calculate_paye
from compliance.calc_nssf import calculate_nssf
from compliance.calc_shif import calculate_shif
from compliance.calc_ahl import calculate_ahl
from compliance.calc_overtime import calculate_overtime_pay

class ComplianceTests(TestCase):
    """
    A comprehensive test suite for all Kenyan statutory compliance calculations.
    
    Note: All calculations use Decimal for precision and are based on current
    Kenyan tax laws (Finance Act 2023/2024 and NSSF Act).
    """

    def test_calculate_paye(self):
        """
        Test the PAYE calculation with various taxable income levels.
        """
        # Test case 1: Income within the first tax bracket (0 - 24,000)
        # Tax rate: 10%
        income_1 = Decimal('20000.00')
        expected_paye_1 = income_1 * Decimal('0.10')
        self.assertEqual(calculate_paye(income_1), expected_paye_1)
        
        # Test case 2: Income spanning the first and second brackets (24,001 - 32,333)
        # Tax rates: 10% on first 24,000; 25% on remainder
        income_2 = Decimal('30000.00')
        paye_on_first_bracket = Decimal('24000.00') * Decimal('0.10')
        paye_on_second_bracket = (income_2 - Decimal('24000.00')) * Decimal('0.25')
        expected_paye_2 = paye_on_first_bracket + paye_on_second_bracket
        self.assertEqual(calculate_paye(income_2), expected_paye_2)
        
        # Test case 3: Income spanning all brackets
        # Tax rates: 10%, 25%, 30%, 32.5%
        income_3 = Decimal('65000.00')
        paye_on_first = Decimal('24000.00') * Decimal('0.10')
        paye_on_second = (Decimal('32333.00') - Decimal('24000.00')) * Decimal('0.25')
        paye_on_third = (Decimal('500000.00') - Decimal('32333.00')) * Decimal('0.30')
        paye_on_fourth = (income_3 - Decimal('500000.00')) * Decimal('0.325')
        expected_paye_3 = paye_on_first + paye_on_second + paye_on_third + paye_on_fourth
        self.assertEqual(calculate_paye(income_3), expected_paye_3)

        # Test case 4: Income above the top bracket ( > 800,000)
        # Tax rate: 35% on remainder
        income_4 = Decimal('850000.00')
        paye_on_first = Decimal('24000.00') * Decimal('0.10')
        paye_on_second = (Decimal('32333.00') - Decimal('24000.00')) * Decimal('0.25')
        paye_on_third = (Decimal('500000.00') - Decimal('32333.00')) * Decimal('0.30')
        paye_on_fourth = (Decimal('800000.00') - Decimal('500000.00')) * Decimal('0.325')
        paye_on_fifth = (income_4 - Decimal('800000.00')) * Decimal('0.35')
        expected_paye_4 = paye_on_first + paye_on_second + paye_on_third + paye_on_fourth + paye_on_fifth
        self.assertEqual(calculate_paye(income_4), expected_paye_4)

    def test_calculate_nssf(self):
        """
        Test the NSSF calculation based on the NSSF Act 2013, with two tiers.
        """
        # Tier I: Gross salary up to 7,000 KES (6% contribution)
        income_1 = Decimal('5000.00')
        expected_nssf_1 = income_1 * Decimal('0.06')
        self.assertEqual(calculate_nssf(income_1), expected_nssf_1)
        
        # Tier II: Gross salary above 7,000 KES, up to 36,000 KES (6% on a pensionable salary of 36,000)
        income_2 = Decimal('20000.00')
        expected_nssf_2 = Decimal('36000.00') * Decimal('0.06')
        self.assertEqual(calculate_nssf(income_2), expected_nssf_2)

        # Tier II: Gross salary above 36,000 KES
        income_3 = Decimal('50000.00')
        expected_nssf_3 = Decimal('36000.00') * Decimal('0.06')
        self.assertEqual(calculate_nssf(income_3), expected_nssf_3)

    def test_calculate_shif(self):
        """
        Test the SHIF calculation based on a fixed percentage of gross income.
        """
        # Test case 1: Gross income of 50,000 KES
        income_1 = Decimal('50000.00')
        expected_shif_1 = income_1 * Decimal('0.0275')
        self.assertEqual(calculate_shif(income_1), expected_shif_1)
        
        # Test case 2: Gross income of 15,000 KES
        income_2 = Decimal('15000.00')
        expected_shif_2 = income_2 * Decimal('0.0275')
        self.assertEqual(calculate_shif(income_2), expected_shif_2)

    def test_calculate_ahl(self):
        """
        Test the Affordable Housing Levy (AHL) calculation.
        """
        # Test case 1: Gross income of 50,000 KES
        income_1 = Decimal('50000.00')
        expected_ahl = income_1 * Decimal('0.015')
        self.assertEqual(calculate_ahl(income_1), (expected_ahl, expected_ahl))

        # Test case 2: Gross income of 150,000 KES
        income_2 = Decimal('150000.00')
        expected_ahl = income_2 * Decimal('0.015')
        self.assertEqual(calculate_ahl(income_2), (expected_ahl, expected_ahl))

    def test_calculate_overtime_pay(self):
        """
        Test the overtime pay calculation.
        Assumes a standard 160-hour work month.
        """
        gross_salary = Decimal('40000.00')
        standard_hours = Decimal('160.00')
        
        # Case 1: Weekday overtime (1.5x hourly rate)
        weekday_ot_hours = Decimal('10.00')
        expected_hourly_rate = gross_salary / standard_hours
        expected_overtime = expected_hourly_rate * weekday_ot_hours * Decimal('1.5')
        self.assertEqual(calculate_overtime_pay(gross_salary, weekday_ot_hours, Decimal('0.00')), expected_overtime)
        
        # Case 2: Weekend overtime (2.0x hourly rate)
        weekend_ot_hours = Decimal('5.00')
        expected_overtime = expected_hourly_rate * weekend_ot_hours * Decimal('2.0')
        self.assertEqual(calculate_overtime_pay(gross_salary, Decimal('0.00'), weekend_ot_hours), expected_overtime)

        # Case 3: Both weekday and weekend overtime
        total_weekday_ot = Decimal('10.00')
        total_weekend_ot = Decimal('5.00')
        
        expected_weekday_pay = expected_hourly_rate * total_weekday_ot * Decimal('1.5')
        expected_weekend_pay = expected_hourly_rate * total_weekend_ot * Decimal('2.0')
        expected_total = expected_weekday_pay + expected_weekend_pay
        self.assertEqual(calculate_overtime_pay(gross_salary, total_weekday_ot, total_weekend_ot), expected_total)
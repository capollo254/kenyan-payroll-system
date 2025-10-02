# apps/payroll/calculator_views.py
"""
Public Payroll Calculator API
No authentication required - for marketing website integration
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal, InvalidOperation
import json

# Import our calculation functions
from apps.compliance.calc_paye import calculate_paye
from apps.compliance.calc_nssf import calculate_nssf
from apps.compliance.calc_shif import calculate_shif
from apps.compliance.calc_ahl import calculate_ahl
from apps.compliance.calc_reliefs import (
    calculate_insurance_relief,
    calculate_post_retirement_medical_deduction,
    calculate_mortgage_interest_relief
)

@csrf_exempt  # CSRF exemption needed for public calculator - safe because no sensitive data is modified
@api_view(['POST', 'GET'])
@authentication_classes([])  # No authentication required
@permission_classes([AllowAny])  # No authentication required
def public_payroll_calculator(request):
    """
    Public payroll calculator endpoint for marketing website.
    
    SECURITY NOTE: CSRF exemption is safe here because:
    1. This endpoint only performs calculations and returns data
    2. No user data is stored or modified
    3. No sensitive operations are performed
    4. Designed for public use by both authenticated and anonymous users
    
    Accepts salary and optional relief inputs, returns complete payroll breakdown.
    No authentication required - designed for public use.
    """
    
    if request.method == 'GET':
        # Return calculator information and input format
        return Response({
            'message': 'Kenya Payroll Calculator API',
            'description': 'Calculate net pay with KRA-compliant deductions and reliefs',
            'version': '1.0',
            'method': 'POST',
            'required_fields': ['gross_salary'],
            'optional_fields': [
                'pension_contribution',
                'insurance_premiums',
                'medical_fund_contribution',
                'mortgage_interest',
                'helb_deduction',
                'other_voluntary_deductions'
            ],
            'sample_request': {
                'gross_salary': 150000,
                'pension_contribution': 15000,
                'insurance_premiums': 3000,
                'medical_fund_contribution': 8000,
                'mortgage_interest': 20000,
                'helb_deduction': 2500,
                'other_voluntary_deductions': 5000
            },
            'calculation_features': [
                'PAYE Tax (10% - 35% brackets)',
                'NSSF Contribution (6%)',
                'SHIF Contribution (2.75%)',
                'Affordable Housing Levy (1.5%)',
                'Insurance Relief (15% up to KSh 5,000)',
                'Pension Relief (up to KSh 30,000)',
                'Medical Fund Relief (up to KSh 15,000)',
                'Mortgage Interest Relief (up to KSh 30,000)',
                'Personal Relief (KSh 2,400)'
            ]
        })
    
    try:
        # Parse input data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.data
        
        # Validate and extract gross salary (required)
        try:
            gross_salary = Decimal(str(data.get('gross_salary', 0)))
            if gross_salary <= 0:
                return Response({
                    'error': 'Gross salary must be greater than 0',
                    'code': 'INVALID_SALARY'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (InvalidOperation, ValueError):
            return Response({
                'error': 'Invalid gross salary format. Please provide a valid number.',
                'code': 'INVALID_FORMAT'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract optional inputs with defaults
        try:
            # Helper function to safely convert to Decimal, handling empty strings
            def safe_decimal(value, default=0):
                if value is None or value == '' or value == 'null':
                    return Decimal(str(default))
                return Decimal(str(value))
            
            pension_contribution = safe_decimal(data.get('pension_contribution'), 0)
            insurance_premiums = safe_decimal(data.get('insurance_premiums'), 0)
            medical_fund_contribution = safe_decimal(data.get('medical_fund_contribution'), 0)
            mortgage_interest = safe_decimal(data.get('mortgage_interest'), 0)
            helb_deduction = safe_decimal(data.get('helb_deduction'), 0)
            other_voluntary_deductions = safe_decimal(data.get('other_voluntary_deductions'), 0)
        except (InvalidOperation, ValueError):
            return Response({
                'error': 'Invalid number format in optional fields',
                'code': 'INVALID_FORMAT'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate reasonable limits
        if gross_salary > Decimal('10000000'):  # 10 million limit
            return Response({
                'error': 'Gross salary exceeds reasonable limit (KSh 10,000,000)',
                'code': 'SALARY_TOO_HIGH'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # --- PERFORM CALCULATIONS ---
        
        # 1. Calculate statutory deductions
        nssf_deduction = calculate_nssf(gross_salary)
        shif_deduction = calculate_shif(gross_salary)
        ahl_employee_deduction, ahl_employer_contribution = calculate_ahl(gross_salary)
        
        # 2. Calculate reliefs and deductions
        PENSION_MAX_RELIEF = Decimal('30000.00')
        pension_relief_amount = min(pension_contribution, PENSION_MAX_RELIEF)
        
        medical_fund_deduction = calculate_post_retirement_medical_deduction(medical_fund_contribution)
        mortgage_interest_relief = calculate_mortgage_interest_relief(mortgage_interest)
        
        # 3. Calculate taxable income
        taxable_income = gross_salary - (
            nssf_deduction + 
            shif_deduction + 
            ahl_employee_deduction + 
            pension_relief_amount +
            medical_fund_deduction +
            mortgage_interest_relief
        )
        taxable_income = max(taxable_income, Decimal('0.00'))
        
        # 4. Calculate PAYE
        paye_before_insurance_relief = calculate_paye(taxable_income)
        insurance_relief = calculate_insurance_relief(insurance_premiums)
        paye_after_relief = max(paye_before_insurance_relief - insurance_relief, Decimal('0.00'))
        
        # 5. Calculate total deductions
        total_statutory_deductions = (
            paye_after_relief + 
            nssf_deduction + 
            shif_deduction + 
            ahl_employee_deduction + 
            helb_deduction
        )
        
        total_voluntary_deductions = pension_contribution + other_voluntary_deductions
        total_deductions = total_statutory_deductions + total_voluntary_deductions
        
        # 6. Calculate net pay
        net_pay = gross_salary - total_deductions
        
        # --- PREPARE RESPONSE ---
        response_data = {
            'success': True,
            'calculation_date': '2025-09-21',  # Current date
            'inputs': {
                'gross_salary': float(gross_salary),
                'pension_contribution': float(pension_contribution),
                'insurance_premiums': float(insurance_premiums),
                'medical_fund_contribution': float(medical_fund_contribution),
                'mortgage_interest': float(mortgage_interest),
                'helb_deduction': float(helb_deduction),
                'other_voluntary_deductions': float(other_voluntary_deductions)
            },
            'statutory_deductions': {
                'paye_tax': {
                    'amount': float(paye_after_relief),
                    'description': 'Pay As You Earn Tax (after reliefs)',
                    'calculation_note': f'Taxable income: KSh {float(taxable_income):,.2f}'
                },
                'nssf': {
                    'amount': float(nssf_deduction),
                    'description': 'National Social Security Fund (6%)',
                    'rate': '6%'
                },
                'shif': {
                    'amount': float(shif_deduction),
                    'description': 'Social Health Insurance Fund (2.75%)',
                    'rate': '2.75%'
                },
                'ahl': {
                    'amount': float(ahl_employee_deduction),
                    'description': 'Affordable Housing Levy (1.5%)',
                    'rate': '1.5%',
                    'employer_contribution': float(ahl_employer_contribution)
                },
                'helb': {
                    'amount': float(helb_deduction),
                    'description': 'Higher Education Loans Board'
                },
                'total': float(total_statutory_deductions)
            },
            'reliefs_applied': {
                'pension_relief': {
                    'contribution': float(pension_contribution),
                    'relief_amount': float(pension_relief_amount),
                    'cap': 30000,
                    'description': 'Pension contribution relief (capped at KSh 30,000)'
                },
                'insurance_relief': {
                    'premiums': float(insurance_premiums),
                    'relief_amount': float(insurance_relief),
                    'rate': '15%',
                    'cap': 5000,
                    'description': 'Insurance relief (15% up to KSh 5,000)'
                },
                'medical_fund_relief': {
                    'contribution': float(medical_fund_contribution),
                    'relief_amount': float(medical_fund_deduction),
                    'cap': 15000,
                    'description': 'Post-retirement medical fund (up to KSh 15,000)'
                },
                'mortgage_relief': {
                    'interest': float(mortgage_interest),
                    'relief_amount': float(mortgage_interest_relief),
                    'cap': 30000,
                    'description': 'Mortgage interest relief (up to KSh 30,000)'
                },
                'personal_relief': {
                    'amount': 2400,
                    'description': 'Standard personal relief (included in PAYE calculation)'
                }
            },
            'voluntary_deductions': {
                'pension_contribution': float(pension_contribution),
                'other_deductions': float(other_voluntary_deductions),
                'total': float(total_voluntary_deductions)
            },
            'summary': {
                'gross_salary': float(gross_salary),
                'total_deductions': float(total_deductions),
                'net_pay': float(net_pay),
                'effective_tax_rate': float((paye_after_relief / gross_salary) * 100) if gross_salary > 0 else 0
            },
            'disclaimer': 'This calculator provides estimates based on current KRA rates. Consult a tax professional for specific advice.',
            'powered_by': 'Kenya Payroll System'
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'error': f'Calculation error: {str(e)}',
            'code': 'CALCULATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
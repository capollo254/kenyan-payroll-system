# apps/reports/generators.py (Refactored)

from .utils import queryset_to_csv

def generate_payroll_summary(payroll_run_id):
    """
    Generates a CSV summary of a single payroll run.
    """
    # ... (same initial setup to get payslips) ...

    # Define the fields you want in the report
    fields_to_export = [
        "employee__user__first_name", 
        "employee__user__last_name", 
        "gross_salary", 
        "overtime_pay", 
        "total_gross_income",
        "paye_tax", 
        "nssf_deduction", 
        "shif_deduction", 
        "ahl_deduction",
        "helb_deduction",
        "total_deductions", 
        "net_pay"
    ]

    # Use the utility function to convert the queryset to CSV
    csv_data = queryset_to_csv(payslips, fields=fields_to_export)
    
    return csv_data
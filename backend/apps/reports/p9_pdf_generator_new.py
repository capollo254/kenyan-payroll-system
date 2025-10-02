"""
Official KRA P9 PDF Generator - Exact KRA Format
Generates Kenya Revenue Authority P9 Income Tax Deduction Cards
in the exact official format with landscape orientation
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from decimal import Decimal
import os
from django.conf import settings
from django.http import HttpResponse
from io import BytesIO


class P9PDFGenerator:
    """Generate official KRA P9 Income Tax Deduction Card PDFs in landscape format"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.page_width, self.page_height = landscape(A4)  # Landscape orientation
        
        # Official KRA P9 styles
        self.kra_title_style = ParagraphStyle(
            'KRATitle',
            fontName='Helvetica-Bold',
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=2*mm
        )
        
        self.kra_header_style = ParagraphStyle(
            'KRAHeader',
            fontName='Helvetica-Bold',
            fontSize=9,
            alignment=TA_CENTER,
            spaceBefore=1*mm,
            spaceAfter=1*mm
        )
        
        self.kra_section_style = ParagraphStyle(
            'KRASection',
            fontName='Helvetica-Bold',
            fontSize=8,
            alignment=TA_LEFT,
            spaceBefore=1*mm
        )
        
        self.kra_normal_style = ParagraphStyle(
            'KRANormal',
            fontName='Helvetica',
            fontSize=7,
            alignment=TA_LEFT
        )

    def generate_p9_pdf(self, p9_report, file_path=None):
        """Generate official KRA P9 Income Tax Deduction Card PDF in landscape format"""
        
        if file_path is None:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                                  rightMargin=10*mm, leftMargin=10*mm,
                                  topMargin=10*mm, bottomMargin=10*mm)
        else:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4),
                                  rightMargin=10*mm, leftMargin=10*mm, 
                                  topMargin=10*mm, bottomMargin=10*mm)
        
        story = []
        
        # Official KRA Header - exact format
        story.append(Paragraph("KENYA REVENUE AUTHORITY", self.kra_title_style))
        story.append(Paragraph("INCOME TAX DEPARTMENT", self.kra_header_style))
        story.append(Paragraph(f"INCOME TAX DEDUCTION CARD YEAR ... {p9_report.tax_year}", self.kra_header_style))
        story.append(Spacer(1, 3*mm))
        
        # Employee Information Section - exact format
        story.append(self._create_official_kra_employee_section(p9_report))
        story.append(Spacer(1, 3*mm))
        
        # Main Monthly Table - all columns as per KRA format
        story.append(self._create_official_kra_monthly_table(p9_report))
        story.append(Spacer(1, 3*mm))
        
        # Bottom Summary Section
        story.append(self._create_official_kra_summary_section(p9_report))
        story.append(Spacer(1, 3*mm))
        
        # Important Notes Section
        story.append(self._create_official_kra_notes_section())
        
        # Build PDF
        doc.build(story)
        
        if file_path is None:
            buffer.seek(0)
            return buffer
        return file_path

    def create_http_response(self, p9_report):
        """Create HTTP response with P9 PDF for download"""
        buffer = self.generate_p9_pdf(p9_report)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="P9_{p9_report.employee_name.replace(" ", "_")}_{p9_report.tax_year}.pdf"'
        response.write(buffer.getvalue())
        buffer.close()
        
        return response

    def save_pdf_file(self, p9_report, file_path=None):
        """Save P9 PDF to file system"""
        if file_path is None:
            # Create directory in media root
            directory = os.path.join(settings.MEDIA_ROOT, 'p9_reports')
            os.makedirs(directory, exist_ok=True)
            
            filename = f"P9_{p9_report.employee_name.replace(' ', '_')}_{p9_report.tax_year}.pdf"
            file_path = os.path.join(directory, filename)
        else:
            # If a specific file path is provided, ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        
        # Generate PDF and save to file
        self.generate_p9_pdf(p9_report, file_path=file_path)
        return file_path
    
    def _create_official_kra_employee_section(self, p9_report):
        """Create official KRA employee information section - exact format"""
        
        # Top section with Employee Name and P.I.N. fields
        employee_parts = p9_report.employee_name.split() if p9_report.employee_name else ['', '']
        first_name = employee_parts[0] if len(employee_parts) > 0 else ''
        other_names = ' '.join(employee_parts[1:]) if len(employee_parts) > 1 else ''
        
        data = [
            [
                'Employee\'s Name:', p9_report.employee_name or '', 
                'Employer\'s P.I.N.:', p9_report.employer_pin or ''
            ],
            [
                'Employee\'s First Name:', first_name,
                'Employee\'s P.I.N.:', p9_report.employee_pin or ''
            ],
            [
                'Employee\'s Other Names:', other_names,
                'NHIF P.I.N.:', ''  # Not in our model
            ],
            [
                '', '',
                'Employee\'s SHIF Number:', ''  # Not in our model
            ]
        ]
        
        # Calculate column widths for landscape
        total_width = self.page_width - 20*mm  # accounting for margins
        col_widths = [total_width * 0.2, total_width * 0.3, total_width * 0.2, total_width * 0.3]
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Left column labels bold
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Right column labels bold
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        return table
    
    def _create_official_kra_monthly_table(self, p9_report):
        """Create the official KRA monthly breakdown table with all columns"""
        
        # Column headers as per official KRA format
        headers = [
            ['MONTH', 'Basic Salary', 'Benefits Non Cash', 'Value of Quarters', 'Total Gross Pay',
             'Defined Contribution\nRetirement scheme', 'Affordable\nHousing Levy\n(AHL)',
             'Social Health\nInsurance Fund\n(SHIF)', 'Post Retirement\nMedical Fund\n(PRMF)',
             'Owner\nOccupied\nInterest', 'Total Deductions\n(Sum of\nE+F+G+H+I)', 'Chargeable Pay\n(D-J)',
             'Tax\nCharged\nK.sh', 'Personal\nRelief\nK.sh', 'Insurance\nRelief\nK.sh', 'PAYE Tax (L-M-N)']
        ]
        
        # Add sub-headers
        sub_headers = [
            ['', 'K.shs\nA', 'K.shs\nB', 'K.shs\nC', 'K.shs\nD',
             'K.shs\nE', 'K.shs\nF', 'K.shs\nG', 'K.shs\nH',
             'K.shs\nI', 'K.shs\nJ', 'K.shs\nK', 'K.shs\nL',
             'K.shs\nM', 'K.shs\nN', 'K.shs\nO']
        ]
        
        # Additional calculation notes
        calc_notes = [
            ['', 'E1\n30% of A', 'E3\nFixed\n20,000 p.a', '', '',
             'Actual Contribution', '', '', '', '', '', '', '', '', '', '']
        ]
        
        # Combine headers
        data = headers + sub_headers + calc_notes
        
        # Monthly data
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        monthly_breakdowns = p9_report.monthly_breakdown.all().order_by('month')
        monthly_dict = {mb.month: mb for mb in monthly_breakdowns}
        
        # Personal relief per month (28,800 / 12 = 2,400)
        monthly_personal_relief = Decimal('2400.00')
        
        for month_num, month_name in enumerate(months, 1):
            if month_num in monthly_dict:
                mb = monthly_dict[month_num]
                
                # Calculate values for this month
                basic_salary = mb.basic_salary or Decimal('0.00')
                benefits = mb.gross_pay - basic_salary if mb.gross_pay > basic_salary else Decimal('0.00')
                value_quarters = Decimal('0.00')  # Not tracked separately
                gross_pay = mb.gross_pay or Decimal('0.00')
                
                # Deductions
                nssf = basic_salary * Decimal('0.06') if basic_salary > 0 else Decimal('0.00')  # 6% NSSF
                if nssf > Decimal('2160.00'):  # Cap at 2,160
                    nssf = Decimal('2160.00')
                
                ahl = mb.ahl or Decimal('0.00')
                shif = mb.shif or Decimal('0.00')
                prmf = Decimal('0.00')  # Not implemented
                owner_interest = Decimal('0.00')  # Not implemented
                
                total_deductions = nssf + ahl + shif + prmf + owner_interest
                chargeable_pay = gross_pay - total_deductions
                
                # Tax calculations
                tax_charged = self._calculate_tax_charged(chargeable_pay)
                insurance_relief = Decimal('0.00')  # Not implemented
                paye_tax = tax_charged - monthly_personal_relief - insurance_relief
                if paye_tax < 0:
                    paye_tax = Decimal('0.00')
                
                row_data = [
                    month_name,
                    f'{basic_salary:,.2f}',
                    f'{benefits:,.2f}',
                    f'{value_quarters:,.2f}',
                    f'{gross_pay:,.2f}',
                    f'{nssf:,.2f}',
                    f'{ahl:,.2f}',
                    f'{shif:,.2f}',
                    f'{prmf:,.2f}',
                    f'{owner_interest:,.2f}',
                    f'{total_deductions:,.2f}',
                    f'{chargeable_pay:,.2f}',
                    f'{tax_charged:,.2f}',
                    f'{monthly_personal_relief:,.2f}',
                    f'{insurance_relief:,.2f}',
                    f'{paye_tax:,.2f}'
                ]
            else:
                # Empty month
                row_data = [month_name] + ['0.00'] * 15
            
            data.append(row_data)
        
        # Total row
        total_row = [
            'TOTAL',
            f'{p9_report.total_basic_salary:,.2f}',
            f'{p9_report.total_benefits_non_cash:,.2f}',
            f'{p9_report.total_value_of_quarters:,.2f}',
            f'{p9_report.total_gross_pay:,.2f}',
            f'{p9_report.retirement_actual:,.2f}',
            f'{p9_report.total_ahl:,.2f}',
            f'{p9_report.total_shif:,.2f}',
            f'{p9_report.total_prmf:,.2f}',
            '0.00',  # Owner interest
            f'{p9_report.total_deductions:,.2f}',
            f'{p9_report.chargeable_pay:,.2f}',
            f'{p9_report.tax_charged:,.2f}',
            f'{p9_report.total_personal_relief:,.2f}',
            f'{p9_report.total_insurance_relief:,.2f}',
            f'{p9_report.total_paye_tax:,.2f}'
        ]
        data.append(total_row)
        
        # Calculate column widths for landscape orientation
        total_width = self.page_width - 20*mm
        col_widths = [total_width * 0.08] + [total_width * 0.058] * 15  # Distribute remaining width
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Headers
            ('FONTNAME', (0, 0), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 2), 6),
            ('BACKGROUND', (0, 0), (-1, 2), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Monthly data
            ('FONTNAME', (0, 3), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 3), (-1, -2), 6),
            ('ALIGN', (1, 3), (-1, -1), 'RIGHT'),
            
            # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 6),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        return table
    
    def _create_official_kra_summary_section(self, p9_report):
        """Create the official KRA bottom summary section"""
        data = [
            ['To be completed by Employer at end of year', '', ''],
            ['', '', ''],
            ['TOTAL CHARGEABLE PAY (COL K)', f'K.sh {p9_report.chargeable_pay:,.2f}', 
             f'TOTAL TAX (COL O) K.sh {p9_report.total_paye_tax:,.2f}'],
        ]
        
        table = Table(data, colWidths=[self.page_width * 0.4, self.page_width * 0.3, self.page_width * 0.3])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 9),
            ('ALIGN', (1, 2), (-1, 2), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (1, 2), (-1, 2), 0.5, colors.black),
        ]))
        return table
    
    def _create_official_kra_notes_section(self):
        """Create the official KRA important notes section"""
        notes_text = """
<b>IMPORTANT</b><br/>
1. Use P9A<br/>
(a) For all taxable Employees and where director/employees receives benefits in addition to cash emoluments<br/>
(b) Where an Employee is eligible for deduction on owner occupier interest and the total interest payable in the year is K.shs. 150,000/= and above<br/>
(c) Where an employee contributes to a post retirement medical fund<br/>
(d) Photocopy of interest certificate and statement of account from the Financial Institution<br/>
(e) The DECLARATION duly signed by the employee<br/><br/>
2. (a) Deductible interest in respect of any month prior to December 2024 must not exceed K.shs. 25,000/= and commencing December 2024 must not exceed 20,000/=<br/>
(b) Deductible pension contribution in respect of any month prior to December 2024 must not exceed K.shs. 20,000/= and commencing December 2024 must not exceed 30,000/=<br/>
(c) Deductible contribution to a post retirement medical fund in respect of any month is effective from December 2024 must not exceed K.shs 15,000/=<br/>
(d) Deductible Contribution to the Social Health Insurance Fund (SHIF) and deductions made towards 'Affordable Housing Levy (AHL)' are effective December 2024<br/>
(e) Personal Relief is K.shs. 2400 per Month or 28,800 per year<br/>
(f) Insurance Relief is 15% of the Premium up to a Maximum of K.shs. 5,000 per month or K.shs. 60,000 per year
        """
        
        paragraph = Paragraph(notes_text, ParagraphStyle(
            'Notes',
            fontName='Helvetica',
            fontSize=6,
            alignment=TA_LEFT,
            leftIndent=5*mm
        ))
        
        return paragraph
    
    def _calculate_tax_charged(self, chargeable_pay):
        """Calculate tax charged based on KRA tax bands"""
        if chargeable_pay <= 0:
            return Decimal('0.00')
        
        # KRA tax bands (monthly)
        if chargeable_pay <= 24000:
            return chargeable_pay * Decimal('0.10')  # 10%
        elif chargeable_pay <= 32333:
            return Decimal('2400.00') + (chargeable_pay - 24000) * Decimal('0.25')  # 25%
        elif chargeable_pay <= 500000:
            return Decimal('4483.25') + (chargeable_pay - 32333) * Decimal('0.30')  # 30%
        elif chargeable_pay <= 800000:
            return Decimal('144783.35') + (chargeable_pay - 500000) * Decimal('0.325')  # 32.5%
        else:
            return Decimal('242283.35') + (chargeable_pay - 800000) * Decimal('0.35')  # 35%
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
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=1.5*mm
        )
        
        self.kra_header_style = ParagraphStyle(
            'KRAHeader',
            fontName='Helvetica-Bold',
            fontSize=8,
            alignment=TA_CENTER,
            spaceBefore=0.5*mm,
            spaceAfter=0.5*mm
        )
        
        # Cell text style for wrapped content
        self.kra_cell_style = ParagraphStyle(
            'KRACell',
            fontName='Helvetica',
            fontSize=5.5,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
            leading=6.5
        )
        
        self.kra_cell_style_right = ParagraphStyle(
            'KRACellRight',
            fontName='Helvetica',
            fontSize=6,
            alignment=TA_RIGHT,
            spaceBefore=0,
            spaceAfter=0,
            leading=7
        )
        
        self.kra_header_cell_style = ParagraphStyle(
            'KRAHeaderCell',
            fontName='Helvetica-Bold',
            fontSize=5.5,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
            leading=6.5
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

    def _wrap_text(self, text, style=None, is_header=False):
        """Convert text to Paragraph for proper text wrapping"""
        if style is None:
            style = self.kra_header_cell_style if is_header else self.kra_cell_style
        return Paragraph(str(text), style)

    def generate_p9_pdf(self, p9_report, file_path=None):
        """Generate official KRA P9 Income Tax Deduction Card PDF in landscape format"""
        
        if file_path is None:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                                  rightMargin=8*mm, leftMargin=8*mm,
                                  topMargin=6*mm, bottomMargin=6*mm)
        else:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4),
                                  rightMargin=8*mm, leftMargin=8*mm, 
                                  topMargin=6*mm, bottomMargin=6*mm)
        
        story = []
        
        # Official KRA Header - exact format
        story.append(Paragraph("KENYA REVENUE AUTHORITY", self.kra_title_style))
        story.append(Paragraph("INCOME TAX DEPARTMENT", self.kra_header_style))
        story.append(Paragraph(f"INCOME TAX DEDUCTION CARD YEAR ... {p9_report.tax_year}", self.kra_header_style))
        story.append(Spacer(1, 2*mm))
        
        # Employee Information Section - exact format
        story.append(self._create_official_kra_employee_section(p9_report))
        story.append(Spacer(1, 1.5*mm))
        
        # Main Monthly Table - all columns as per KRA format
        story.append(self._create_official_kra_monthly_table(p9_report))
        story.append(Spacer(1, 1.5*mm))
        
        # Bottom Summary Section
        story.append(self._create_official_kra_summary_section(p9_report))
        story.append(Spacer(1, 1*mm))
        
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
                'Employer\'s Name:', p9_report.employer_name or '', 
                'Employer\'s P.I.N.:', p9_report.employer_pin or ''
            ],
            [
                'Employee\'s First Name:', first_name,
                'Employee\'s P.I.N.:', p9_report.employee_pin or ''
            ],
            [
                'Employee\'s Other Names:', other_names,
                '', ''  # Empty fields for layout
            ]
        ]
        
        # Calculate column widths for landscape
        total_width = self.page_width - 20*mm  # accounting for margins
        col_widths = [total_width * 0.2, total_width * 0.3, total_width * 0.2, total_width * 0.3]
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Left column labels bold
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Right column labels bold
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ]))
        return table
    
    def _create_official_kra_monthly_table(self, p9_report):
        """Create the official KRA monthly breakdown table with all columns"""
        
        # Column headers as per official KRA format (removed column E) - with text wrapping
        headers = [
            [self._wrap_text('MONTH', is_header=True), 
             self._wrap_text('Basic Salary', is_header=True), 
             self._wrap_text('Benefits Non Cash', is_header=True), 
             self._wrap_text('Value of Quarters', is_header=True), 
             self._wrap_text('Total Gross Pay', is_header=True),
             self._wrap_text('E1<br/>(30% of A)', is_header=True), 
             self._wrap_text('E2<br/>(Actual<br/>Contribution)', is_header=True), 
             self._wrap_text('E3<br/>(Fixed<br/>30,000 p.m)', is_header=True),
             self._wrap_text('Affordable<br/>Housing Levy<br/>(AHL)', is_header=True), 
             self._wrap_text('Social Health<br/>Insurance Fund<br/>(SHIF)', is_header=True), 
             self._wrap_text('Post Retirement<br/>Medical Fund<br/>(PRMF)', is_header=True),
             self._wrap_text('Owner<br/>Occupied<br/>Interest', is_header=True), 
             self._wrap_text('Total Deductions<br/>(Lower of E+F+G+H+I)', is_header=True), 
             self._wrap_text('Chargeable Pay<br/>(D-J)', is_header=True),
             self._wrap_text('Tax<br/>Charged<br/>K.sh', is_header=True), 
             self._wrap_text('Personal<br/>Relief<br/>K.sh', is_header=True), 
             self._wrap_text('Insurance<br/>Relief<br/>K.sh', is_header=True), 
             self._wrap_text('PAYE Tax (L-M-N)', is_header=True)]
        ]
        
        # Add sub-headers with wrapping
        sub_headers = [
            [self._wrap_text('', is_header=True), 
             self._wrap_text('K.shs<br/>A', is_header=True), 
             self._wrap_text('K.shs<br/>B', is_header=True), 
             self._wrap_text('K.shs<br/>C', is_header=True), 
             self._wrap_text('K.shs<br/>D', is_header=True),
             self._wrap_text('K.shs<br/>E1', is_header=True), 
             self._wrap_text('K.shs<br/>E2', is_header=True), 
             self._wrap_text('K.shs<br/>E3', is_header=True),
             self._wrap_text('K.shs<br/>F', is_header=True), 
             self._wrap_text('K.shs<br/>G', is_header=True), 
             self._wrap_text('K.shs<br/>H', is_header=True),
             self._wrap_text('K.shs<br/>I', is_header=True), 
             self._wrap_text('K.shs<br/>J', is_header=True), 
             self._wrap_text('K.shs<br/>K', is_header=True), 
             self._wrap_text('K.shs<br/>L', is_header=True),
             self._wrap_text('K.shs<br/>M', is_header=True), 
             self._wrap_text('K.shs<br/>N', is_header=True), 
             self._wrap_text('K.shs<br/>O', is_header=True)]
        ]
        
        # Additional calculation notes with wrapping
        calc_notes = [
            [self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True),
             self._wrap_text('30% of Basic<br/>Salary', is_header=True), 
             self._wrap_text('Pension +<br/>NSSF', is_header=True), 
             self._wrap_text('Fixed Amount<br/>30,000', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True), 
             self._wrap_text('', is_header=True)]
        ]
        
        # Combine headers
        data = headers + sub_headers + calc_notes
        
        # Initialize totals before processing monthly data
        total_basic = Decimal('0.00')
        total_benefits = Decimal('0.00')
        total_quarters = Decimal('0.00')
        total_gross = Decimal('0.00')
        total_e1 = Decimal('0.00')
        total_e2 = Decimal('0.00')
        total_e3 = Decimal('0.00')
        total_ahl = Decimal('0.00')
        total_shif = Decimal('0.00')
        total_prmf = Decimal('0.00')
        total_owner_interest = Decimal('0.00')
        total_deductions = Decimal('0.00')
        total_chargeable = Decimal('0.00')
        total_tax_charged = Decimal('0.00')
        total_personal_relief = Decimal('0.00')
        total_insurance_relief = Decimal('0.00')
        total_paye = Decimal('0.00')

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
                
                # Retirement contribution calculations - Use actual monthly breakdown data
                # E1: 30% of Basic Salary (Column A)
                e1_thirty_percent = mb.retirement_30_percent_monthly or Decimal('0.00')
                
                # E2: Actual Contribution (NSSF + Pension from payslip data)
                e2_actual_contribution = mb.retirement_actual_monthly or Decimal('0.00')
                
                # E3: Fixed amount 30,000 per month
                e3_fixed_amount = mb.retirement_fixed_monthly or Decimal('30000.00')
                
                # Total retirement contribution (E = Lower of E1, E2, E3)
                effective_retirement = min(e1_thirty_percent, e2_actual_contribution, e3_fixed_amount)
                
                # Other deductions
                ahl = mb.ahl or Decimal('0.00')
                shif = mb.shif or Decimal('0.00')
                prmf = Decimal('0.00')  # Not implemented
                owner_interest = Decimal('0.00')  # Not implemented
                
                total_deductions = effective_retirement + ahl + shif + prmf + owner_interest
                chargeable_pay = gross_pay - total_deductions
                
                # Tax calculations
                tax_charged = self._calculate_tax_charged(chargeable_pay)
                insurance_relief = Decimal('0.00')  # Not implemented
                paye_tax = tax_charged - monthly_personal_relief - insurance_relief
                if paye_tax < 0:
                    paye_tax = Decimal('0.00')
                
                # Accumulate totals for the year
                total_basic += basic_salary
                total_benefits += benefits
                total_quarters += value_quarters
                total_gross += gross_pay
                total_e1 += e1_thirty_percent
                total_e2 += e2_actual_contribution
                total_e3 += e3_fixed_amount
                total_ahl += ahl
                total_shif += shif
                total_prmf += prmf
                total_owner_interest += owner_interest
                # Don't add to total_deductions yet - will calculate later from totals
                total_chargeable += chargeable_pay
                total_tax_charged += tax_charged  # Sum the monthly tax charged amounts
                total_personal_relief += monthly_personal_relief
                total_insurance_relief += insurance_relief
                total_paye += paye_tax
                
                row_data = [
                    self._wrap_text(month_name),
                    self._wrap_text(f'{basic_salary:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{benefits:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{value_quarters:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{gross_pay:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{e1_thirty_percent:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{e2_actual_contribution:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{e3_fixed_amount:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{ahl:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{shif:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{prmf:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{owner_interest:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{total_deductions:,.2f}', self.kra_cell_style_right),  # Uses lower of E1, E2, E3
                    self._wrap_text(f'{chargeable_pay:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{tax_charged:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{monthly_personal_relief:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{insurance_relief:,.2f}', self.kra_cell_style_right),
                    self._wrap_text(f'{paye_tax:,.2f}', self.kra_cell_style_right)
                ]
            else:
                # Empty month with wrapped text
                empty_cells = [self._wrap_text('0.00', self.kra_cell_style_right)] * 17
                row_data = [self._wrap_text(month_name)] + empty_cells
            
            data.append(row_data)
        
        # Calculate final totals after processing all months
        # Column J: Total Deductions = Lower of E (min of E1, E2, E3) + F + G + H + I
        lower_of_e = min(total_e1, total_e2, total_e3)
        total_deductions = lower_of_e + total_ahl + total_shif + total_prmf + total_owner_interest
        
        # Column K: Chargeable Pay = Total Gross Pay - Total Deductions
        total_chargeable = total_gross - total_deductions
        
        # Column L: Tax Charged is already summed from monthly calculations
        # (total_tax_charged is now the sum of monthly tax_charged amounts)
        
        # Column O: PAYE Tax = Tax Charged - Personal Relief - Insurance Relief
        total_paye = max(Decimal('0.00'), total_tax_charged - total_personal_relief - total_insurance_relief)
        
        # Total row with calculated totals from monthly data
        total_row = [
            self._wrap_text('TOTAL', is_header=True),
            self._wrap_text(f'{total_basic:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_benefits:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_quarters:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_gross:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_e1:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_e2:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_e3:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_ahl:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_shif:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_prmf:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_owner_interest:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_deductions:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_chargeable:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_tax_charged:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_personal_relief:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_insurance_relief:,.2f}', self.kra_header_cell_style),
            self._wrap_text(f'{total_paye:,.2f}', self.kra_header_cell_style)
        ]
        data.append(total_row)
        
        # Calculate column widths for landscape orientation (18 columns instead of 19)
        total_width = self.page_width - 20*mm
        col_widths = [total_width * 0.06] + [total_width * 0.052] * 17  # Distribute remaining width across 18 columns
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Headers - font styling handled by Paragraph objects
            ('BACKGROUND', (0, 0), (-1, 2), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Monthly data - alignment handled by Paragraph objects
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ]))
        
        # Store calculated totals for summary section
        self._calculated_totals = {
            'total_chargeable': total_chargeable,
            'total_paye': total_paye
        }
        
        return table
    
    def _create_official_kra_summary_section(self, p9_report):
        """Create the official KRA bottom summary section using calculated totals"""
        # Use calculated totals from monthly data if available
        if hasattr(self, '_calculated_totals'):
            total_chargeable = self._calculated_totals['total_chargeable']
            total_paye = self._calculated_totals['total_paye']
        else:
            # Fallback to P9Report model values
            total_chargeable = p9_report.chargeable_pay
            total_paye = p9_report.total_paye_tax
        
        data = [
            ['To be completed by Employer at end of year', '', ''],
            ['', '', ''],
            [f'TOTAL CHARGEABLE PAY (COL K): K.sh {total_chargeable:,.2f}', '', 
             f'TOTAL TAX (COL O): K.sh {total_paye:,.2f}'],
        ]
        
        table = Table(data, colWidths=[self.page_width * 0.5, self.page_width * 0.2, self.page_width * 0.3])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('FONTNAME', (2, 2), (2, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (0, 2), 8),
            ('FONTSIZE', (2, 2), (2, 2), 8),
            ('ALIGN', (0, 2), (0, 2), 'LEFT'),
            ('ALIGN', (2, 2), (2, 2), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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
    
    def _calculate_tax_on_annual_chargeable_pay(self, annual_chargeable_pay):
        """Calculate tax charged based on KRA annual tax brackets"""
        if annual_chargeable_pay <= 0:
            return Decimal('0.00')
        
        # 2025 KRA tax brackets (annual amounts)
        # Band 1: 0 - 288,000 (24,000 * 12) at 10%
        if annual_chargeable_pay <= 288000:
            return annual_chargeable_pay * Decimal('0.10')
        
        # Band 2: 288,001 - 388,000 (32,333 * 12) at 25%  
        elif annual_chargeable_pay <= 388000:
            return Decimal('28800.00') + (annual_chargeable_pay - 288000) * Decimal('0.25')
        
        # Band 3: 388,001 - 6,000,000 (500,000 * 12) at 30%
        elif annual_chargeable_pay <= 6000000:
            return Decimal('53800.00') + (annual_chargeable_pay - 388000) * Decimal('0.30')
        
        # Band 4: 6,000,001 - 9,600,000 (800,000 * 12) at 32.5%
        elif annual_chargeable_pay <= 9600000:
            return Decimal('1737400.00') + (annual_chargeable_pay - 6000000) * Decimal('0.325')
        
        # Band 5: Above 9,600,000 at 35%
        else:
            return Decimal('2907400.00') + (annual_chargeable_pay - 9600000) * Decimal('0.35')
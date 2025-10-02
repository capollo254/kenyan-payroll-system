# apps/payroll/pdf_generator.py

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from django.conf import settings
from decimal import Decimal
import os
from io import BytesIO
from apps.core.company_models import CompanySettings

class PayslipPDFGenerator:
    """Generate PDF payslips with company logo and detailed deductions"""
    
    def __init__(self, payslip):
        self.payslip = payslip
        self.company_settings = CompanySettings.get_settings()
        
    def generate_pdf(self):
        """Generate and return PDF as HTTP response"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build the PDF content
        story = []
        
        # Add company header with logo
        story.extend(self._build_header())
        story.append(Spacer(1, 0.2*inch))
        
        # Add payslip title
        story.extend(self._build_title())
        story.append(Spacer(1, 0.2*inch))
        
        # Add employee and payroll run info
        story.extend(self._build_employee_info())
        story.append(Spacer(1, 0.2*inch))
        
        # Add earnings section
        story.extend(self._build_earnings_section())
        story.append(Spacer(1, 0.2*inch))
        
        # Add deductions section
        story.extend(self._build_deductions_section())
        story.append(Spacer(1, 0.2*inch))
        
        # Add summary
        story.extend(self._build_summary())
        
        # Build PDF
        doc.build(story)
        
        # Return HTTP response
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        filename = f"payslip_{self.payslip.employee.user.first_name}_{self.payslip.employee.user.last_name}_{self.payslip.payroll_run.period_start_date.strftime('%Y_%m')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def _get_styles(self):
        """Get custom styles for the PDF"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CompanyName',
            parent=styles['Title'],
            fontSize=18,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        styles.add(ParagraphStyle(
            name='PayslipTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.darkblue,
            backColor=colors.lightgrey
        ))
        
        return styles
    
    def _build_header(self):
        """Build company header with logo"""
        elements = []
        styles = self._get_styles()
        
        # Try to add company logo
        if self.company_settings.logo:
            try:
                logo_path = os.path.join(settings.MEDIA_ROOT, str(self.company_settings.logo))
                if os.path.exists(logo_path):
                    logo = Image(logo_path, width=2*inch, height=1*inch)
                    logo.hAlign = 'CENTER'
                    elements.append(logo)
                    elements.append(Spacer(1, 0.1*inch))
            except Exception:
                pass  # If logo fails, continue without it
        
        # Company name
        company_name = Paragraph(self.company_settings.company_name, styles['CompanyName'])
        elements.append(company_name)
        
        # Company address
        if self.company_settings.address_line_1:
            address_parts = []
            if self.company_settings.address_line_1:
                address_parts.append(self.company_settings.address_line_1)
            if self.company_settings.address_line_2:
                address_parts.append(self.company_settings.address_line_2)
            if self.company_settings.city:
                city_part = self.company_settings.city
                if self.company_settings.postal_code:
                    city_part += f", {self.company_settings.postal_code}"
                address_parts.append(city_part)
            if self.company_settings.country:
                address_parts.append(self.company_settings.country)
            
            address_text = "<br/>".join(address_parts)
            address_para = Paragraph(address_text, styles['Normal'])
            address_para.alignment = TA_CENTER
            elements.append(address_para)
        
        # Contact info
        contact_parts = []
        if self.company_settings.phone:
            contact_parts.append(f"Tel: {self.company_settings.phone}")
        if self.company_settings.email:
            contact_parts.append(f"Email: {self.company_settings.email}")
        if self.company_settings.website:
            contact_parts.append(f"Web: {self.company_settings.website}")
        
        if contact_parts:
            contact_text = " | ".join(contact_parts)
            contact_para = Paragraph(contact_text, styles['Normal'])
            contact_para.alignment = TA_CENTER
            elements.append(contact_para)
        
        return elements
    
    def _build_title(self):
        """Build payslip title"""
        styles = self._get_styles()
        title = Paragraph("PAYSLIP", styles['PayslipTitle'])
        return [title]
    
    def _build_employee_info(self):
        """Build employee and payroll period information with text wrapping"""
        styles = self._get_styles()
        
        # Create wrapped text elements for long names and data
        employee_name = Paragraph(f"{self.payslip.employee.user.get_full_name()}", styles['Normal'])
        employee_email = Paragraph(self.payslip.employee.user.email, styles['Normal'])
        employee_id = Paragraph(str(getattr(self.payslip.employee.job_info, 'company_employee_id', 'N/A')), styles['Normal'])
        
        period_text = Paragraph(f"{self.payslip.payroll_run.period_start_date} to {self.payslip.payroll_run.period_end_date}", styles['Normal'])
        run_date = Paragraph(str(self.payslip.payroll_run.run_date), styles['Normal'])
        payslip_id = Paragraph(str(self.payslip.id), styles['Normal'])
        
        # Employee and period info table with wrapped text
        data = [
            [Paragraph('<b>Employee Information</b>', styles['Normal']), '', Paragraph('<b>Payroll Information</b>', styles['Normal']), ''],
            [Paragraph('<b>Name:</b>', styles['Normal']), employee_name, Paragraph('<b>Period:</b>', styles['Normal']), period_text],
            [Paragraph('<b>Email:</b>', styles['Normal']), employee_email, Paragraph('<b>Run Date:</b>', styles['Normal']), run_date],
            [Paragraph('<b>Employee ID:</b>', styles['Normal']), employee_id, Paragraph('<b>Payslip ID:</b>', styles['Normal']), payslip_id],
        ]
        
        # Improved column widths for A4 page (total width: ~7.5 inches)
        table = Table(data, colWidths=[1.3*inch, 2.4*inch, 1.3*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
            ('BACKGROUND', (2, 0), (3, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Changed to TOP for better text wrapping
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return [table]
    
    def _build_earnings_section(self):
        """Build earnings section with text wrapping"""
        styles = self._get_styles()
        
        elements = []
        
        # Section header
        header = Paragraph("EARNINGS", styles['SectionHeader'])
        elements.append(header)
        
        # Earnings table with wrapped text
        earnings_data = [
            [Paragraph('<b>Description</b>', styles['Normal']), Paragraph('<b>Amount (KES)</b>', styles['Normal'])],
            [Paragraph('Basic Salary', styles['Normal']), Paragraph(f"{self.payslip.gross_salary:,.2f}", styles['Normal'])],
        ]
        
        if self.payslip.overtime_pay > 0:
            earnings_data.append([
                Paragraph('Overtime Pay', styles['Normal']), 
                Paragraph(f"{self.payslip.overtime_pay:,.2f}", styles['Normal'])
            ])
        
        earnings_data.append([
            Paragraph('<b>Total Gross Income</b>', styles['Normal']), 
            Paragraph(f"<b>{self.payslip.total_gross_income:,.2f}</b>", styles['Normal'])
        ])
        
        # Better column widths for earnings table
        earnings_table = Table(earnings_data, colWidths=[5*inch, 2.5*inch])
        earnings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Changed to TOP for better text wrapping
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(earnings_table)
        return elements
    
    def _build_deductions_section(self):
        """Build detailed deductions section with text wrapping"""
        styles = self._get_styles()
        elements = []
        
        # Section header
        header = Paragraph("DEDUCTIONS", styles['SectionHeader'])
        elements.append(header)
        
        # Get all deductions
        deductions = self.payslip.deduction_items.all()
        
        # Build deductions table with wrapped text
        deductions_data = [
            [Paragraph('<b>Description</b>', styles['Normal']), 
             Paragraph('<b>Type</b>', styles['Normal']), 
             Paragraph('<b>Amount (KES)</b>', styles['Normal'])],
        ]
        
        for deduction in deductions:
            deduction_type = 'Statutory' if deduction.is_statutory else 'Voluntary'
            deductions_data.append([
                Paragraph(str(deduction.deduction_type), styles['Normal']),
                Paragraph(deduction_type, styles['Normal']),
                Paragraph(f"{deduction.amount:,.2f}", styles['Normal'])
            ])
        
        deductions_data.append([
            Paragraph('<b>Total Deductions</b>', styles['Normal']), 
            Paragraph('', styles['Normal']), 
            Paragraph(f"<b>{self.payslip.total_deductions:,.2f}</b>", styles['Normal'])
        ])
        
        # Better column widths for deductions table  
        deductions_table = Table(deductions_data, colWidths=[3.5*inch, 2*inch, 2*inch])
        deductions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Changed to TOP for better text wrapping
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(deductions_table)
        return elements
    
    def _build_summary(self):
        """Build payslip summary with text wrapping"""
        styles = self._get_styles()
        elements = []
        
        # Section header
        header = Paragraph("SUMMARY", styles['SectionHeader'])
        elements.append(header)
        
        # Summary table with wrapped text
        summary_data = [
            [Paragraph('Total Gross Income', styles['Normal']), Paragraph(f"{self.payslip.total_gross_income:,.2f}", styles['Normal'])],
            [Paragraph('Total Deductions', styles['Normal']), Paragraph(f"({self.payslip.total_deductions:,.2f})", styles['Normal'])],
            [Paragraph('<b>NET PAY</b>', styles['Normal']), Paragraph(f"<b>{self.payslip.net_pay:,.2f}</b>", styles['Normal'])],
        ]
        
        # Better column widths for summary table
        summary_table = Table(summary_data, colWidths=[5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Changed to TOP for better text wrapping
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.darkgreen),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(summary_table)
        
        # Add footer note
        elements.append(Spacer(1, 0.3*inch))
        footer_text = "This is a computer-generated payslip. No signature is required."
        footer = Paragraph(footer_text, styles['Normal'])
        footer.alignment = TA_CENTER
        elements.append(footer)
        
        return elements
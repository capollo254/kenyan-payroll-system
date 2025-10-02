# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import ReportGenerationLog, P9Report, P9MonthlyBreakdown
from .serializers import ReportGenerationLogSerializer
from .p9_pdf_generator import P9PDFGenerator
from .bulk_p9_generator import BulkP9Generator
from apps.employees.models import Employee
import os
import json

class ReportViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for generating and managing reports.
    """
    queryset = ReportGenerationLog.objects.all().order_by('-generation_date')
    serializer_class = ReportGenerationLogSerializer
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # The user generating the report is the currently authenticated user
        user = self.request.user
        try:
            employee = Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee profile not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # For this example, we'll simulate a file path.
        # In a real app, this would be a more complex generation process.
        report_type = self.request.data.get('report_type')
        start_date = self.request.data.get('start_date')
        end_date = self.request.data.get('end_date')

        file_path = f"reports/{report_type}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"

        serializer.save(
            generated_by=employee,
            file_path=file_path,
            start_date=start_date,
            end_date=end_date
        )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Action to download a generated report.
        """
        report_log = self.get_object()
        # This is a placeholder. A real implementation would serve the file.
        file_exists = os.path.exists(report_log.file_path)

        if not file_exists:
            return Response(
                {"error": "Report file not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": "Report download would be triggered.", "file_path": report_log.file_path},
            status=status.HTTP_200_OK
        )


class P9ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for P9 Tax Report management and PDF generation
    """
    queryset = P9Report.objects.all().order_by('-tax_year', 'employee__user__first_name')
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter P9 reports based on user role"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            # Admins can see all P9 reports
            return P9Report.objects.all().order_by('-tax_year', 'employee__user__first_name')
        else:
            # Regular employees can only see their own P9 reports
            try:
                employee = user.employee_profile
                return P9Report.objects.filter(employee=employee).order_by('-tax_year')
            except AttributeError:
                # User has no employee profile
                return P9Report.objects.none()
    
    def get_serializer_class(self):
        # You'll need to create P9ReportSerializer
        from .serializers import P9ReportSerializer
        return P9ReportSerializer

    def perform_create(self, serializer):
        """Auto-assign employee when creating P9"""
        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            # For regular employees, auto-assign their employee profile
            try:
                employee = user.employee_profile
                serializer.save(employee=employee)
            except AttributeError:
                raise ValidationError("User has no associated employee profile")
        else:
            serializer.save()

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download P9 as KRA-formatted PDF"""
        p9_report = self.get_object()
        pdf_generator = P9PDFGenerator()
        
        try:
            response = pdf_generator.create_http_response(p9_report)
            return response
        except Exception as e:
            return Response(
                {"error": f"Failed to generate PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    @method_decorator(staff_member_required)
    def bulk_generate(self, request):
        """Generate P9 reports for multiple employees from payslip data"""
        
        tax_year = request.data.get('tax_year', timezone.now().year)
        employee_ids = request.data.get('employee_ids', None)
        from_payslips = request.data.get('from_payslips', True)
        
        bulk_generator = BulkP9Generator(tax_year=tax_year)
        
        try:
            results = bulk_generator.generate_bulk_p9(
                employee_ids=employee_ids,
                from_payslips=from_payslips
            )
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Bulk generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    @method_decorator(staff_member_required)
    def bulk_pdf_download(self, request):
        """Generate and download ZIP file of P9 PDFs for multiple employees"""
        
        tax_year = request.data.get('tax_year', timezone.now().year)
        p9_ids = request.data.get('p9_ids', None)
        
        # Get P9 reports
        p9_reports = P9Report.objects.filter(tax_year=tax_year)
        if p9_ids:
            p9_reports = p9_reports.filter(id__in=p9_ids)
        
        bulk_generator = BulkP9Generator(tax_year=tax_year)
        
        try:
            results = bulk_generator.generate_bulk_pdfs(p9_reports, create_zip=True)
            
            if results['zip_file']:
                # Return ZIP file for download
                zip_path = results['zip_file']['path']
                
                with open(zip_path, 'rb') as zip_file:
                    response = HttpResponse(zip_file.read(), content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="P9_Reports_{tax_year}_All.zip"'
                    return response
            else:
                return Response(
                    {"error": "No ZIP file created", "results": results},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": f"Bulk PDF generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def payslip_summary(self, request):
        """Get summary of available payslip data for P9 generation"""
        
        tax_year = request.query_params.get('year', timezone.now().year)
        user = request.user
        
        # For regular employees, only show their own data
        if not user.is_staff and not user.is_superuser:
            try:
                employee = user.employee_profile
                employee_id = employee.id
            except AttributeError:
                return Response(
                    {"error": "User has no associated employee profile"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            employee_id = request.query_params.get('employee_id', None)
        
        bulk_generator = BulkP9Generator(tax_year=tax_year)
        
        try:
            if employee_id:
                # Get summary for specific employee
                from apps.employees.models import Employee
                from apps.payroll.models import Payslip
                from decimal import Decimal
                
                employee = get_object_or_404(Employee, id=employee_id)
                payslips = Payslip.objects.filter(
                    employee=employee,
                    payroll_run__run_date__year=tax_year
                )
                
                total_payslips = payslips.count()
                total_gross_pay = sum(Decimal(str(p.total_gross_income or 0)) for p in payslips)
                total_paye_tax = sum(Decimal(str(p.paye_tax or 0)) for p in payslips)
                total_nssf = sum(Decimal(str(p.nssf_contribution or 0)) for p in payslips)
                
                return Response({
                    'tax_year': tax_year,
                    'employee': {
                        'id': employee.id,
                        'name': employee.get_full_name(),
                        'employee_number': employee.employee_number,
                    },
                    'total_payslips': total_payslips,
                    'total_gross_pay': float(total_gross_pay),
                    'total_paye_tax': float(total_paye_tax),
                    'total_nssf': float(total_nssf)
                }, status=status.HTTP_200_OK)
            else:
                # Get summary for all employees (admin only)
                summary = bulk_generator.get_payslip_summary(
                    employee_id=None,
                    tax_year=tax_year
                )
                
                return Response({
                    'tax_year': tax_year,
                    'employee_count': len(summary),
                    'employees': summary
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to get payslip summary: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate P9 taxes and totals"""
        p9_report = self.get_object()
        
        try:
            # Recalculate all fields
            p9_report.calculate_totals()
            p9_report.save()
            
            return Response({
                'message': 'P9 calculations updated successfully',
                'gross_pay': float(p9_report.total_gross_pay),
                'paye_tax': float(p9_report.total_paye_tax),
                'chargeable_pay': float(p9_report.chargeable_pay)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Recalculation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
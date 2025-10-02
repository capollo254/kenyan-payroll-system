// static/admin/js/p9_auto_populate.js

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Auto-populate functionality
        $('#populate-btn').on('click', function() {
            const employeeSelect = $('#id_employee');
            const taxYearInput = $('#id_tax_year');
            const statusDiv = $('#populate-status');
            const button = $(this);
            
            const employeeId = employeeSelect.val();
            const taxYear = taxYearInput.val();
            
            if (!employeeId || !taxYear) {
                statusDiv.html('<div style="color: red;">⚠️ Please select an employee and enter a tax year first.</div>');
                return;
            }
            
            // Disable button and show loading
            button.prop('disabled', true).text('🔄 Loading...');
            statusDiv.html('<div style="color: blue;">📡 Fetching payroll data...</div>');
            
            // Make AJAX request
            $.post('/admin/reports/p9report/populate-from-payroll/', {
                'employee_id': employeeId,
                'tax_year': taxYear,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            })
            .done(function(response) {
                if (response.success) {
                    // Populate main form fields
                    const data = response.data;
                    
                    $('#id_employee_name').val(data.employee_name);
                    $('#id_employee_pin').val(data.employee_pin);
                    $('#id_total_basic_salary').val(data.total_basic_salary.toFixed(2));
                    $('#id_total_gross_pay').val(data.total_gross_pay.toFixed(2));
                    $('#id_total_ahl').val(data.total_ahl.toFixed(2));
                    $('#id_total_shif').val(data.total_shif.toFixed(2));
                    $('#id_retirement_actual').val(data.retirement_actual.toFixed(2));
                    $('#id_total_deductions').val(data.total_deductions.toFixed(2));
                    $('#id_chargeable_pay').val(data.chargeable_pay.toFixed(2));
                    $('#id_total_personal_relief').val(data.total_personal_relief.toFixed(2));
                    $('#id_total_insurance_relief').val(data.total_insurance_relief.toFixed(2));
                    $('#id_total_paye_tax').val(data.total_paye_tax.toFixed(2));
                    
                    // Populate monthly breakdown inline forms
                    populateMonthlyBreakdown(data.monthly_data);
                    
                    statusDiv.html(`
                        <div style="background: #d4edda; color: #155724; padding: 10px; border-radius: 4px; border: 1px solid #c3e6cb;">
                            ✅ <strong>Successfully populated from ${data.payslips_count} payslips!</strong><br/>
                            • Gross Pay: KES ${data.total_gross_pay.toLocaleString()}<br/>
                            • PAYE Tax: KES ${data.total_paye_tax.toLocaleString()}<br/>
                            • Monthly breakdowns added: ${data.monthly_data.length}
                        </div>
                    `);
                } else {
                    statusDiv.html(`<div style="color: red;">❌ ${response.error}</div>`);
                }
            })
            .fail(function(xhr) {
                statusDiv.html('<div style="color: red;">❌ Network error occurred. Please try again.</div>');
            })
            .always(function() {
                // Re-enable button
                button.prop('disabled', false).text('🔄 Auto-Populate from Payroll Data');
            });
        });
        
        // Auto-refresh payroll data summary when employee or tax year changes
        $('#id_employee, #id_tax_year').on('change', function() {
            // Reset populate status
            $('#populate-status').html('');
        });
        
        function populateMonthlyBreakdown(monthlyData) {
            // Clear existing inline forms
            $('.dynamic-p9monthlybreakdown_set tbody tr').not('.add-row').remove();
            
            // Add new rows for each month
            monthlyData.forEach(function(month, index) {
                // Add new inline form
                const totalForms = parseInt($('#id_p9monthlybreakdown_set-TOTAL_FORMS').val());
                const newFormHtml = $('.add-row').prev().clone();
                
                // Update form index
                newFormHtml.html(newFormHtml.html().replace(/__prefix__/g, totalForms));
                
                // Insert before add-row
                $('.add-row').before(newFormHtml);
                
                // Populate values
                const prefix = `p9monthlybreakdown_set-${totalForms}`;
                $(`#id_${prefix}-month`).val(month.month);
                $(`#id_${prefix}-basic_salary`).val(month.basic_salary.toFixed(2));
                $(`#id_${prefix}-gross_pay`).val(month.gross_pay.toFixed(2));
                $(`#id_${prefix}-ahl`).val(month.ahl.toFixed(2));
                $(`#id_${prefix}-shif`).val(month.shif.toFixed(2));
                $(`#id_${prefix}-total_deductions`).val(month.total_deductions.toFixed(2));
                $(`#id_${prefix}-chargeable_pay`).val(month.chargeable_pay.toFixed(2));
                $(`#id_${prefix}-paye_tax`).val(month.paye_tax.toFixed(2));
                
                // Update total forms count
                $('#id_p9monthlybreakdown_set-TOTAL_FORMS').val(totalForms + 1);
            });
        }
    });
    
})(django.jQuery);
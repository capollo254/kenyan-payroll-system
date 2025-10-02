// src/components/payslip/PayslipDetailView.js

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api/auth';

const PayslipDetailView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [payslip, setPayslip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    fetchPayslipDetail();
  }, [id]);

  const fetchPayslipDetail = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await api.get(`payroll/payslips/${id}/`, {
        headers: {
          Authorization: `Token ${token}`,
        },
      });
      setPayslip(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching payslip:', err);
      if (err.response && err.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        navigate('/login');
      } else {
        setError('Failed to load payslip details');
      }
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    try {
      setDownloadingPdf(true);
      const token = localStorage.getItem('token');
      
      const response = await api.get(`payroll/payslips/${id}/download_pdf/`, {
        headers: {
          Authorization: `Token ${token}`,
        },
        responseType: 'blob',
      });

      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename
      const employeeName = payslip?.employee?.user?.first_name && payslip?.employee?.user?.last_name
        ? `${payslip.employee.user.first_name}_${payslip.employee.user.last_name}`
        : 'Employee';
      const period = payslip?.payroll_run?.period_start_date 
        ? payslip.payroll_run.period_start_date.split('-').slice(0, 2).join('_')
        : 'current';
      
      link.setAttribute('download', `payslip_${employeeName}_${period}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading PDF:', err);
      setError('Failed to download PDF');
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="container page">
        <div className="loading-spinner">Loading payslip details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container page">
        <div className="error-message">{error}</div>
        <button onClick={() => navigate(-1)} className="btn btn-secondary">
          Go Back
        </button>
      </div>
    );
  }

  if (!payslip) {
    return (
      <div className="container page">
        <div className="error-message">Payslip not found</div>
        <button onClick={() => navigate(-1)} className="btn btn-secondary">
          Go Back
        </button>
      </div>
    );
  }

  const { employee, payroll_run, company_settings } = payslip;

  return (
    <div className="container page" style={{ maxWidth: '800px', margin: '0 auto' }}>
      {/* Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <button onClick={() => navigate(-1)} className="btn btn-secondary">
          ← Back
        </button>
        <button 
          onClick={downloadPDF} 
          className="btn btn-primary"
          disabled={downloadingPdf}
        >
          {downloadingPdf ? 'Generating PDF...' : '📄 Download PDF'}
        </button>
      </div>

      {/* Company Header */}
      {company_settings && (
        <div className="company-header" style={{ textAlign: 'center', marginBottom: '30px', borderBottom: '2px solid #eee', paddingBottom: '20px' }}>
          {company_settings.logo_url && (
            <img 
              src={company_settings.logo_url} 
              alt="Company Logo" 
              style={{ maxHeight: '80px', marginBottom: '10px' }}
            />
          )}
          <h1 style={{ color: '#2c3e50', marginBottom: '5px' }}>{company_settings.company_name}</h1>
          {company_settings.address_line_1 && (
            <div style={{ color: '#666', fontSize: '14px' }}>
              <p style={{ margin: '2px 0' }}>{company_settings.address_line_1}</p>
              {company_settings.address_line_2 && <p style={{ margin: '2px 0' }}>{company_settings.address_line_2}</p>}
              <p style={{ margin: '2px 0' }}>
                {company_settings.city && `${company_settings.city}, `}
                {company_settings.postal_code && `${company_settings.postal_code}, `}
                {company_settings.country}
              </p>
              {(company_settings.phone || company_settings.email) && (
                <p style={{ margin: '2px 0' }}>
                  {company_settings.phone && `Tel: ${company_settings.phone}`}
                  {company_settings.phone && company_settings.email && ' | '}
                  {company_settings.email && `Email: ${company_settings.email}`}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Payslip Title */}
      <h2 style={{ textAlign: 'center', color: '#2c3e50', marginBottom: '30px' }}>PAYSLIP</h2>

      {/* Employee and Payroll Information */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div>
            <h3 style={{ color: '#3498db', borderBottom: '2px solid #3498db', paddingBottom: '5px' }}>Employee Information</h3>
            <p><strong>Name:</strong> {employee?.user?.first_name} {employee?.user?.last_name}</p>
            <p><strong>Email:</strong> {employee?.user?.email}</p>
            <p><strong>Employee ID:</strong> {employee?.employee_id}</p>
          </div>
          <div>
            <h3 style={{ color: '#3498db', borderBottom: '2px solid #3498db', paddingBottom: '5px' }}>Payroll Information</h3>
            <p><strong>Period:</strong> {payroll_run?.period_start_date} to {payroll_run?.period_end_date}</p>
            <p><strong>Run Date:</strong> {payroll_run?.run_date}</p>
            <p><strong>Payslip ID:</strong> {payslip.id}</p>
          </div>
        </div>
      </div>

      {/* Earnings Section */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3 style={{ color: '#27ae60', borderBottom: '2px solid #27ae60', paddingBottom: '5px' }}>EARNINGS</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '10px', alignItems: 'center' }}>
          <span>Basic Salary</span>
          <span style={{ fontWeight: 'bold' }}>KES {parseFloat(payslip.gross_salary || 0).toLocaleString()}</span>
          
          {parseFloat(payslip.overtime_pay || 0) > 0 && (
            <>
              <span>Overtime Pay</span>
              <span style={{ fontWeight: 'bold' }}>KES {parseFloat(payslip.overtime_pay).toLocaleString()}</span>
            </>
          )}
          
          <div style={{ borderTop: '1px solid #eee', marginTop: '10px', paddingTop: '10px', gridColumn: '1 / -1' }}></div>
          <span style={{ fontWeight: 'bold' }}>Total Gross Income</span>
          <span style={{ fontWeight: 'bold', color: '#27ae60' }}>KES {parseFloat(payslip.total_gross_income || 0).toLocaleString()}</span>
        </div>
      </div>

      {/* Deductions Section */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3 style={{ color: '#e74c3c', borderBottom: '2px solid #e74c3c', paddingBottom: '5px' }}>DEDUCTIONS</h3>
        
        {/* Statutory Deductions */}
        <div style={{ marginBottom: '15px' }}>
          <h4 style={{ color: '#c0392b', marginBottom: '10px' }}>Statutory Deductions</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '10px', alignItems: 'center' }}>
            {payslip.statutory_deductions && payslip.statutory_deductions.length > 0 ? (
              payslip.statutory_deductions.map((deduction, index) => (
                <React.Fragment key={index}>
                  <span>{deduction.deduction_type}</span>
                  <span style={{ fontWeight: 'bold' }}>KES {parseFloat(deduction.amount).toLocaleString()}</span>
                </React.Fragment>
              ))
            ) : (
              <>
                {parseFloat(payslip.paye_tax || 0) > 0 && (
                  <>
                    <span>PAYE Tax</span>
                    <span style={{ fontWeight: 'bold' }}>KES {parseFloat(payslip.paye_tax).toLocaleString()}</span>
                  </>
                )}
                {parseFloat(payslip.nssf_deduction || 0) > 0 && (
                  <>
                    <span>NSSF</span>
                    <span style={{ fontWeight: 'bold' }}>KES {parseFloat(payslip.nssf_deduction).toLocaleString()}</span>
                  </>
                )}
                {parseFloat(payslip.shif_deduction || 0) > 0 && (
                  <>
                    <span>SHIF</span>
                    <span style={{ fontWeight: 'bold' }}>KES {parseFloat(payslip.shif_deduction).toLocaleString()}</span>
                  </>
                )}
                {parseFloat(payslip.ahl_deduction || 0) > 0 && (
                  <>
                    <span>AHL</span>
                    <span style={{ fontWeight: 'bold' }}>KES {parseFloat(payslip.ahl_deduction).toLocaleString()}</span>
                  </>
                )}
                {parseFloat(payslip.helb_deduction || 0) > 0 && (
                  <>
                    <span>HELB</span>
                    <span style={{ fontWeight: 'bold' }}>KES {parseFloat(payslip.helb_deduction).toLocaleString()}</span>
                  </>
                )}
              </>
            )}
          </div>
        </div>

        {/* Voluntary Deductions */}
        {payslip.voluntary_deductions && payslip.voluntary_deductions.length > 0 && (
          <div style={{ marginBottom: '15px' }}>
            <h4 style={{ color: '#8e44ad', marginBottom: '10px' }}>Voluntary Deductions</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '10px', alignItems: 'center' }}>
              {payslip.voluntary_deductions.map((deduction, index) => (
                <React.Fragment key={index}>
                  <span>{deduction.deduction_type}</span>
                  <span style={{ fontWeight: 'bold' }}>KES {parseFloat(deduction.amount).toLocaleString()}</span>
                </React.Fragment>
              ))}
            </div>
          </div>
        )}

        {/* Total Deductions */}
        <div style={{ borderTop: '2px solid #e74c3c', marginTop: '15px', paddingTop: '10px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '10px', alignItems: 'center' }}>
            <span style={{ fontWeight: 'bold' }}>Total Deductions</span>
            <span style={{ fontWeight: 'bold', color: '#e74c3c' }}>KES {parseFloat(payslip.total_deductions || 0).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Summary Section */}
      <div className="card" style={{ backgroundColor: '#f8f9fa', border: '2px solid #28a745' }}>
        <h3 style={{ color: '#155724', borderBottom: '2px solid #28a745', paddingBottom: '5px' }}>SUMMARY</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '15px', alignItems: 'center', fontSize: '16px' }}>
          <span style={{ fontWeight: 'bold' }}>Total Gross Income</span>
          <span style={{ fontWeight: 'bold' }}>KES {parseFloat(payslip.total_gross_income || 0).toLocaleString()}</span>
          
          <span style={{ fontWeight: 'bold' }}>Total Deductions</span>
          <span style={{ fontWeight: 'bold', color: '#dc3545' }}>(KES {parseFloat(payslip.total_deductions || 0).toLocaleString()})</span>
          
          <div style={{ borderTop: '2px solid #28a745', marginTop: '10px', paddingTop: '15px', gridColumn: '1 / -1' }}></div>
          <span style={{ fontWeight: 'bold', fontSize: '20px', color: '#155724' }}>NET PAY</span>
          <span style={{ fontWeight: 'bold', fontSize: '20px', color: '#28a745' }}>KES {parseFloat(payslip.net_pay || 0).toLocaleString()}</span>
        </div>
      </div>

      {/* Footer Note */}
      <div style={{ textAlign: 'center', marginTop: '30px', color: '#666', fontSize: '12px' }}>
        <p>This is a computer-generated payslip. No signature is required.</p>
      </div>
    </div>
  );
};

export default PayslipDetailView;
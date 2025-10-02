// src/pages/employee/MyP9ReportsPage.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMyP9Reports, generateP9, downloadP9PDF, getPayslipSummary } from '../../api/p9';

const MyP9ReportsPage = () => {
  const [p9Reports, setP9Reports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [payslipSummary, setPayslipSummary] = useState(null);
  const navigate = useNavigate();

  const fetchP9Reports = async () => {
    try {
      setLoading(true);
      const data = await getMyP9Reports();
      setP9Reports(data.results || data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch P9 reports:', err);
      if (err.message.includes('401') || err.message.includes('unauthorized')) {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        navigate('/login');
      }
      setError('Failed to load P9 reports. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchP9Reports();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleGenerateP9 = async () => {
    try {
      setGenerating(true);
      setError(null);

      // First check payslip data for the year
      try {
        const summary = await getPayslipSummary(selectedYear);
        setPayslipSummary(summary);

        if (summary.total_payslips === 0) {
          setError(`No payslip data found for ${selectedYear}. P9 cannot be generated without payroll data.`);
          return;
        }
      } catch (summaryError) {
        console.warn('Could not fetch payslip summary:', summaryError);
      }

      // Generate P9
      await generateP9(selectedYear);
      
      // Refresh the list
      await fetchP9Reports();
      
      alert(`P9 report for ${selectedYear} has been generated successfully!`);
    } catch (err) {
      console.error('Failed to generate P9:', err);
      setError(`Failed to generate P9 for ${selectedYear}: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadPDF = async (p9Id, taxYear) => {
    try {
      await downloadP9PDF(p9Id);
    } catch (err) {
      console.error('Failed to download PDF:', err);
      alert('Failed to download P9 PDF. Please try again.');
    }
  };

  const getAvailableYears = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let year = currentYear; year >= currentYear - 5; year--) {
      years.push(year);
    }
    return years;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 2,
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-GB');
  };

  if (loading) {
    return (
      <div className="container page">
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <h3>Loading P9 Tax Reports...</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="container page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div>
          <h2>My P9 Tax Forms</h2>
          <p style={{ color: 'var(--text-muted)', margin: '5px 0' }}>
            Access and generate your annual P9 tax certificates
          </p>
        </div>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: '20px' }}>
          {error}
        </div>
      )}

      {/* Generate P9 Section */}
      <div className="card" style={{ marginBottom: '30px' }}>
        <h3>Generate New P9 Report</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginTop: '15px', flexWrap: 'wrap' }}>
          <div>
            <label htmlFor="year-select" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Select Tax Year:
            </label>
            <select
              id="year-select"
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              style={{ 
                padding: '8px 12px', 
                borderRadius: '4px', 
                border: '1px solid var(--border-color)',
                fontSize: '14px'
              }}
            >
              {getAvailableYears().map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
          
          <button
            onClick={handleGenerateP9}
            disabled={generating}
            className="btn btn-primary"
            style={{ alignSelf: 'flex-end' }}
          >
            {generating ? 'Generating...' : `Generate P9 for ${selectedYear}`}
          </button>
        </div>

        {payslipSummary && (
          <div style={{ 
            marginTop: '15px', 
            padding: '15px', 
            backgroundColor: 'var(--card-background)', 
            borderRadius: '4px',
            border: '1px solid var(--border-color)'
          }}>
            <h4 style={{ margin: '0 0 10px 0' }}>Payroll Data Summary for {selectedYear}:</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
              <div><strong>Total Payslips:</strong> {payslipSummary.total_payslips}</div>
              <div><strong>Gross Pay:</strong> {formatCurrency(payslipSummary.total_gross_pay)}</div>
              <div><strong>PAYE Tax:</strong> {formatCurrency(payslipSummary.total_paye_tax)}</div>
              <div><strong>NSSF Contributions:</strong> {formatCurrency(payslipSummary.total_nssf)}</div>
            </div>
          </div>
        )}
      </div>

      {/* Existing P9 Reports */}
      <div className="card">
        <h3>Your P9 Reports</h3>
        
        {p9Reports.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <h4>No P9 Reports Available</h4>
            <p>Generate your first P9 report using the form above.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Tax Year</th>
                  <th>Generated Date</th>
                  <th>Gross Pay</th>
                  <th>PAYE Tax</th>
                  <th>NSSF Contribution</th>
                  <th>Chargeable Pay</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {p9Reports.map((report) => (
                  <tr key={report.id}>
                    <td>
                      <strong>{report.tax_year}</strong>
                    </td>
                    <td>{formatDate(report.created_at)}</td>
                    <td>{formatCurrency(report.total_gross_pay)}</td>
                    <td>{formatCurrency(report.total_paye_tax)}</td>
                    <td>{formatCurrency(report.total_nssf_contribution)}</td>
                    <td>{formatCurrency(report.chargeable_pay)}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          onClick={() => handleDownloadPDF(report.id, report.tax_year)}
                          className="btn btn-primary btn-sm"
                          title="Download as PDF"
                        >
                          📄 Download PDF
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Information Section */}
      <div className="card" style={{ marginTop: '20px' }}>
        <h4>About P9 Tax Forms</h4>
        <div style={{ color: 'var(--text-muted)', lineHeight: '1.6' }}>
          <p>
            <strong>What is a P9 Form?</strong> The P9 form is an annual tax certificate that shows your total income, 
            tax deductions, and other statutory contributions for a specific tax year.
          </p>
          <ul>
            <li>Required for tax compliance and filing returns with KRA</li>
            <li>Shows breakdown of monthly gross pay, PAYE tax, and NSSF contributions</li>
            <li>Includes personal relief and other tax benefits</li>
            <li>Valid for loan applications and visa processes</li>
          </ul>
          <p>
            <strong>Need Help?</strong> If you cannot find a P9 for a specific year or notice discrepancies, 
            please contact the HR department.
          </p>
        </div>
      </div>
    </div>
  );
};

export default MyP9ReportsPage;
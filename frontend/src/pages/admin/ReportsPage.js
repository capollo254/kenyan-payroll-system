// src/pages/admin/ReportsPage.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPayrollRuns } from '../../api/payroll';
import { getEmployees } from '../../api/employees';
import Button from '../../components/common/Button';
import InputField from '../../components/common/InputField';

const ReportsPage = () => {
  const [activeReport, setActiveReport] = useState('payroll-summary');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    department: '',
    employee: ''
  });
  const navigate = useNavigate();

  const reportTypes = [
    { id: 'payroll-summary', name: 'Payroll Summary', description: 'Overall payroll statistics and totals' },
    { id: 'tax-report', name: 'Tax Report', description: 'PAYE tax deductions and liability' },
    { id: 'employee-earnings', name: 'Employee Earnings', description: 'Individual employee earning reports' },
    { id: 'deductions-report', name: 'Deductions Report', description: 'All statutory and voluntary deductions' },
    { id: 'department-costs', name: 'Department Costs', description: 'Payroll costs by department' },
    { id: 'year-end-report', name: 'Year-End Report', description: 'Annual summary for tax filing' }
  ];

  const generateReport = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock report generation - in real app, this would call specific report APIs
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API delay
      
      // Generate mock data based on report type
      let mockData = {};
      
      switch (activeReport) {
        case 'payroll-summary':
          mockData = {
            totalEmployees: 18,
            totalGrossPay: 2450000,
            totalDeductions: 485000,
            totalNetPay: 1965000,
            averageSalary: 136111,
            periodCovered: `${filters.startDate || '2025-01-01'} to ${filters.endDate || '2025-09-30'}`
          };
          break;
        case 'tax-report':
          mockData = {
            totalPAYE: 245000,
            totalNSSF: 98000,
            totalSHIF: 67000,
            totalAHL: 42000,
            totalHELB: 33000,
            periodCovered: `${filters.startDate || '2025-01-01'} to ${filters.endDate || '2025-09-30'}`
          };
          break;
        case 'employee-earnings':
          mockData = {
            employees: [
              { name: 'Employee User', grossPay: 65000, deductions: 12500, netPay: 52500 },
              { name: 'John Doe', grossPay: 85000, deductions: 18500, netPay: 66500 },
              { name: 'Jane Smith', grossPay: 95000, deductions: 22000, netPay: 73000 },
              { name: 'Alice Johnson', grossPay: 75000, deductions: 16000, netPay: 59000 },
              { name: 'Bob Wilson', grossPay: 105000, deductions: 25500, netPay: 79500 }
            ]
          };
          break;
        default:
          mockData = { message: `${reportTypes.find(r => r.id === activeReport)?.name} data generated successfully.` };
      }
      
      setReportData(mockData);
    } catch (err) {
      console.error('Failed to generate report:', err);
      setError('Failed to generate report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const exportReport = (format) => {
    alert(`Exporting report as ${format.toUpperCase()}... (Feature would be implemented in production)`);
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="container page">
      <h2>Reports & Analytics</h2>
      <p>Generate various reports for payroll analysis and compliance.</p>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '30px', marginTop: '30px' }}>
        
        {/* Report Types Sidebar */}
        <div className="card">
          <h3>Report Types</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', marginTop: '15px' }}>
            {reportTypes.map((report) => (
              <button
                key={report.id}
                onClick={() => {
                  setActiveReport(report.id);
                  setReportData(null);
                }}
                style={{
                  padding: '10px',
                  border: '1px solid var(--border-color)',
                  backgroundColor: activeReport === report.id ? 'var(--primary-color)' : 'white',
                  color: activeReport === report.id ? 'white' : 'var(--dark-color)',
                  cursor: 'pointer',
                  borderRadius: '5px',
                  textAlign: 'left'
                }}
              >
                <div style={{ fontWeight: 'bold' }}>{report.name}</div>
                <div style={{ fontSize: '0.8rem', opacity: 0.8, marginTop: '2px' }}>
                  {report.description}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Report Content */}
        <div>
          {/* Filters */}
          <div className="card" style={{ marginBottom: '20px' }}>
            <h3>{reportTypes.find(r => r.id === activeReport)?.name}</h3>
            <p>{reportTypes.find(r => r.id === activeReport)?.description}</p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '20px' }}>
              <InputField
                label="Start Date"
                type="date"
                name="startDate"
                value={filters.startDate}
                onChange={handleFilterChange}
              />
              <InputField
                label="End Date"
                type="date"
                name="endDate"
                value={filters.endDate}
                onChange={handleFilterChange}
              />
              <div className="form-group">
                <label>Department</label>
                <select
                  name="department"
                  value={filters.department}
                  onChange={handleFilterChange}
                >
                  <option value="">All Departments</option>
                  <option value="hr">Human Resources</option>
                  <option value="it">Information Technology</option>
                  <option value="finance">Finance</option>
                  <option value="marketing">Marketing</option>
                </select>
              </div>
            </div>

            <div style={{ marginTop: '20px' }}>
              <Button onClick={generateReport} disabled={loading} className="btn-primary">
                {loading ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>
          </div>

          {/* Report Results */}
          {error && <div className="alert alert-error">{error}</div>}
          
          {reportData && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3>Report Results</h3>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-sm btn-secondary" onClick={() => exportReport('pdf')}>
                    Export PDF
                  </button>
                  <button className="btn btn-sm btn-secondary" onClick={() => exportReport('excel')}>
                    Export Excel
                  </button>
                  <button className="btn btn-sm btn-secondary" onClick={() => exportReport('csv')}>
                    Export CSV
                  </button>
                </div>
              </div>

              {/* Payroll Summary Report */}
              {activeReport === 'payroll-summary' && (
                <div>
                  <p><strong>Period:</strong> {reportData.periodCovered}</p>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '20px' }}>
                    <div style={{ textAlign: 'center', padding: '20px', backgroundColor: 'var(--light-color)', borderRadius: '5px' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary-color)' }}>
                        {reportData.totalEmployees}
                      </div>
                      <div>Total Employees</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '20px', backgroundColor: 'var(--light-color)', borderRadius: '5px' }}>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success-color)' }}>
                        KES {reportData.totalGrossPay.toLocaleString()}
                      </div>
                      <div>Total Gross Pay</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '20px', backgroundColor: 'var(--light-color)', borderRadius: '5px' }}>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--danger-color)' }}>
                        KES {reportData.totalDeductions.toLocaleString()}
                      </div>
                      <div>Total Deductions</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '20px', backgroundColor: 'var(--light-color)', borderRadius: '5px' }}>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--info-color)' }}>
                        KES {reportData.totalNetPay.toLocaleString()}
                      </div>
                      <div>Total Net Pay</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tax Report */}
              {activeReport === 'tax-report' && (
                <div>
                  <p><strong>Period:</strong> {reportData.periodCovered}</p>
                  <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                    <thead>
                      <tr style={{ backgroundColor: 'var(--light-color)' }}>
                        <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Tax Type</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>Amount (KES)</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>PAYE Tax</td>
                        <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                          {reportData.totalPAYE.toLocaleString()}
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>NSSF Contributions</td>
                        <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                          {reportData.totalNSSF.toLocaleString()}
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>SHIF Contributions</td>
                        <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                          {reportData.totalSHIF.toLocaleString()}
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>AHL Contributions</td>
                        <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                          {reportData.totalAHL.toLocaleString()}
                        </td>
                      </tr>
                      <tr>
                        <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>HELB Deductions</td>
                        <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                          {reportData.totalHELB.toLocaleString()}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}

              {/* Employee Earnings Report */}
              {activeReport === 'employee-earnings' && reportData.employees && (
                <div>
                  <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                    <thead>
                      <tr style={{ backgroundColor: 'var(--light-color)' }}>
                        <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Employee</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>Gross Pay</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>Deductions</th>
                        <th style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>Net Pay</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reportData.employees.map((emp, index) => (
                        <tr key={index}>
                          <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{emp.name}</td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                            KES {emp.grossPay.toLocaleString()}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                            KES {emp.deductions.toLocaleString()}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', border: '1px solid var(--border-color)' }}>
                            KES {emp.netPay.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Other Reports */}
              {!['payroll-summary', 'tax-report', 'employee-earnings'].includes(activeReport) && (
                <div>
                  <p>{reportData.message}</p>
                  <p style={{ color: 'var(--secondary-color)', fontStyle: 'italic' }}>
                    This report type would contain specific data relevant to {reportTypes.find(r => r.id === activeReport)?.name.toLowerCase()}.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
// src/pages/employee/EmployeeDashboard.js

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMyProfile } from '../../api/employees';
import { getPayslips } from '../../api/payroll';

const EmployeeDashboard = () => {
  const [profile, setProfile] = useState(null);
  const [recentPayslip, setRecentPayslip] = useState(null);
  const [yearlyTotal, setYearlyTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch profile data
        const profileData = await getMyProfile();
        setProfile(profileData);

        // Fetch payslips to get recent data and yearly total
        const payslipsData = await getPayslips();
        if (payslipsData && payslipsData.length > 0) {
          // Get most recent payslip
          const sortedPayslips = payslipsData.sort((a, b) => 
            new Date(b.payroll_run.period_end_date) - new Date(a.payroll_run.period_end_date)
          );
          setRecentPayslip(sortedPayslips[0]);

          // Calculate yearly total (current year)
          const currentYear = new Date().getFullYear();
          const yearlyPayslips = payslipsData.filter(payslip => 
            new Date(payslip.payroll_run.period_end_date).getFullYear() === currentYear
          );
          const total = yearlyPayslips.reduce((sum, payslip) => sum + parseFloat(payslip.net_pay || 0), 0);
          setYearlyTotal(total);
        }
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        if (err.response && err.response.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          navigate('/login');
        }
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [navigate]);

  if (loading) {
    return <div className="container page">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="container page error">{error}</div>;
  }

  return (
    <div className="container page">
      <h2>Employee Dashboard</h2>
      <p>Welcome back, {profile?.full_name || 'Employee'}!</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '30px' }}>
        
        {/* Recent Payslip Card */}
        <div className="card">
          <h3>Most Recent Payslip</h3>
          {recentPayslip ? (
            <div>
              <p><strong>Period:</strong> {recentPayslip.payroll_run?.period_start_date} to {recentPayslip.payroll_run?.period_end_date}</p>
              <p><strong>Gross Pay:</strong> KES {parseFloat(recentPayslip.total_gross_income || 0).toLocaleString()}</p>
              <p><strong>Net Pay:</strong> KES {parseFloat(recentPayslip.net_pay || 0).toLocaleString()}</p>
              <button 
                className="btn btn-primary" 
                onClick={() => navigate('/employee/payslips')}
                style={{ marginTop: '10px' }}
              >
                View All Payslips
              </button>
            </div>
          ) : (
            <p>No payslips available yet.</p>
          )}
        </div>

        {/* Yearly Total Card */}
        <div className="card">
          <h3>Year to Date Earnings</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success-color)', margin: '10px 0' }}>
            KES {yearlyTotal.toLocaleString()}
          </p>
          <p>Total net pay for {new Date().getFullYear()}</p>
        </div>

        {/* Profile Summary Card */}
        <div className="card">
          <h3>Profile Summary</h3>
          {profile ? (
            <div>
              <p><strong>Employee ID:</strong> {profile.employee_id || 'N/A'}</p>
              <p><strong>Department:</strong> {profile.job_information?.department || 'N/A'}</p>
              <p><strong>Position:</strong> {profile.job_information?.job_title || 'N/A'}</p>
              <button 
                className="btn btn-secondary" 
                onClick={() => navigate('/employee/profile')}
                style={{ marginTop: '10px' }}
              >
                Update Profile
              </button>
            </div>
          ) : (
            <p>Profile information not available.</p>
          )}
        </div>

        {/* Quick Actions Card */}
        <div className="card">
          <h3>Quick Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/employee/payslips')}
            >
              View Payslips
            </button>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/employee/p9-reports')}
            >
              📄 P9 Tax Forms
            </button>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/employee/leave-requests')}
            >
              Request Leave
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => navigate('/employee/profile')}
            >
              Update Profile
            </button>
          </div>
        </div>

        {/* P9 Tax Reports Card */}
        <div className="card">
          <h3>P9 Tax Reports</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '15px' }}>
            Access your annual tax certificates for compliance and applications
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ padding: '10px', backgroundColor: 'var(--card-background)', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
              <p><strong>Current Tax Year:</strong> {new Date().getFullYear()}</p>
              <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
                Generate P9 forms for tax filing and official documentation
              </p>
            </div>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/employee/p9-reports')}
            >
              📊 Access P9 Reports
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeDashboard;
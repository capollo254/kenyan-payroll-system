// src/pages/admin/DashboardPage.js

import React, { useEffect, useState } from 'react';
import { getEmployees } from '../../api/employees';
import { getPayrollRuns } from '../../api/payroll';
import DashboardWidget from '../../components/dashboard/DashboardWidget';
import { useNavigate } from 'react-router-dom';

const DashboardPage = () => {
  const [employees, setEmployees] = useState([]);
  const [payrollRuns, setPayrollRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const employeesData = await getEmployees();
        setEmployees(employeesData);
        
        const payrollRunsData = await getPayrollRuns();
        setPayrollRuns(payrollRunsData);
        
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
    fetchData();
  }, [navigate]);

  if (loading) {
    return <div className="container page">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="container page error">{error}</div>;
  }

  const lastPayrollRun = payrollRuns.length > 0 ? payrollRuns[0] : null;

  return (
    <div className="container page">
      <h2>Admin Dashboard</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        <DashboardWidget 
          title="Total Employees" 
          value={employees.length} 
          description="Number of active employees in the system." 
        />
        {lastPayrollRun && (
          <DashboardWidget 
            title="Last Payroll Run" 
            value={new Date(lastPayrollRun.run_date).toLocaleDateString()}
            description="Date of the most recent payroll." 
          />
        )}
      </div>
      <div style={{ marginTop: '20px' }}>
        <h3>Recent Payroll Runs</h3>
        {payrollRuns.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Run Date</th>
                  <th>Period</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {payrollRuns.slice(0, 5).map(run => (
                  <tr key={run.id}>
                    <td>{new Date(run.run_date).toLocaleDateString()}</td>
                    <td>{new Date(run.period_start_date).toLocaleDateString()} - {new Date(run.period_end_date).toLocaleDateString()}</td>
                    <td>{run.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No recent payroll runs to display.</p>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
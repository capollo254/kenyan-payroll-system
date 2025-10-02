// src/pages/admin/AdminDashboard.js

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getEmployees, getMyProfile } from '../../api/employees';
import { getPayrollRuns } from '../../api/payroll';
import DashboardWidget from '../../components/dashboard/DashboardWidget';
import AdminProfileWidget from '../../components/common/AdminProfileWidget';

const AdminDashboard = () => {
  const [employees, setEmployees] = useState([]);
  const [payrollRuns, setPayrollRuns] = useState([]);
  const [adminProfile, setAdminProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch admin profile
        const profileData = await getMyProfile();
        setAdminProfile(profileData);

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
  const activeEmployees = employees.filter(emp => emp.user.is_active).length;
  const pendingTasks = [
    'Review pending leave requests',
    'Process monthly payroll',
    'Update employee benefits',
    'Generate tax reports'
  ];

  return (
    <div className="container page">
      {/* Admin Profile Header */}
      <AdminProfileWidget profile={adminProfile} showFullDetails={true} />

      <h2>Administrator Dashboard</h2>
      <p>Welcome to the payroll management system administrative panel.</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '30px' }}>
        
        {/* Total Employees Widget */}
        <DashboardWidget 
          title="Total Employees" 
          value={employees.length} 
          description={`${activeEmployees} active employees in the system.`}
        />

        {/* Recent Payroll Run Widget */}
        {lastPayrollRun && (
          <DashboardWidget 
            title="Last Payroll Run" 
            value={lastPayrollRun.period_start_date}
            description={`Period: ${lastPayrollRun.period_start_date} to ${lastPayrollRun.period_end_date}`}
          />
        )}

        {/* System Statistics */}
        <div className="card">
          <h3>System Overview</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Total Employees:</span>
              <strong>{employees.length}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Active Employees:</span>
              <strong>{activeEmployees}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Payroll Runs:</span>
              <strong>{payrollRuns.length}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Inactive Users:</span>
              <strong>{employees.length - activeEmployees}</strong>
            </div>
          </div>
        </div>

        {/* Upcoming Tasks */}
        <div className="card">
          <h3>Upcoming Tasks</h3>
          <ul style={{ margin: '10px 0', paddingLeft: '20px' }}>
            {pendingTasks.map((task, index) => (
              <li key={index} style={{ margin: '8px 0' }}>{task}</li>
            ))}
          </ul>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3>Quick Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/admin/payroll')}
            >
              Process Payroll
            </button>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/admin/employees')}
            >
              Manage Employees
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => navigate('/admin/reports')}
            >
              Generate Reports
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => navigate('/admin/user-management')}
            >
              User Management
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h3>Recent Activity</h3>
          <div style={{ fontSize: '0.9rem', color: 'var(--secondary-color)' }}>
            <p>• Payroll processed for September 2025</p>
            <p>• 3 new employees added this month</p>
            <p>• Tax reports generated</p>
            <p>• System backup completed</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
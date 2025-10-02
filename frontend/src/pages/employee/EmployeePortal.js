// src/pages/employee/EmployeePortal.js

import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/common/Button';

const EmployeePortal = () => {
  const navigate = useNavigate();

  return (
    <div className="container page">
      <h2>Welcome, Employee!</h2>
      <p>This is your personal payroll portal. You can view your payslips and manage your profile information here.</p>
      
      <div style={{ display: 'flex', gap: '20px', marginTop: '30px' }}>
        <Button onClick={() => navigate('/employee/dashboard/payslips')} className="btn-primary">
          View My Payslips
        </Button>
        <Button onClick={() => navigate('/employee/dashboard/profile')} className="btn-secondary">
          Manage My Profile
        </Button>
      </div>

      <div style={{ marginTop: '40px' }}>
        {/* We can add a simple summary here, e.g., "Last Payslip Received: [Date]" */}
        <h3>Your Latest Payslip</h3>
        <p>No recent payslip data available.</p>
      </div>
    </div>
  );
};

export default EmployeePortal;
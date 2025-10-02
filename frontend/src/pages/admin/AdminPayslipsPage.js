// src/pages/admin/AdminPayslipsPage.js

import React, { useEffect, useState } from 'react';
import { getPayslips } from '../../api/payroll';
import { useNavigate } from 'react-router-dom';
import PayslipCard from '../../components/payslip/PayslipCard';

const AdminPayslipsPage = () => {
  const [payslips, setPayslips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPayslips = async () => {
      try {
        const data = await getPayslips();
        setPayslips(data);
      } catch (err) {
        console.error('Failed to fetch payslips:', err);
        if (err.response && err.response.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          navigate('/login');
        }
        setError('Could not load payslips. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPayslips();
  }, [navigate]);

  if (loading) {
    return <div className="container page">Loading payslips...</div>;
  }

  if (error) {
    return <div className="container page error">{error}</div>;
  }

  return (
    <div className="container page">
      <h2>My Payslips</h2>
      {payslips.length > 0 ? (
        <div>
          {payslips.map(payslip => (
            <PayslipCard key={payslip.id} payslip={payslip} />
          ))}
        </div>
      ) : (
        <p>No payslips found.</p>
      )}
    </div>
  );
};

export default AdminPayslipsPage;
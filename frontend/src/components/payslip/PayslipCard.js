// src/components/payslip/PayslipCard.js

import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * A component to display a single payslip in a card format.
 * @param {object} props - Component props.
 * @param {object} props.payslip - The payslip data object.
 */
const PayslipCard = ({ payslip }) => {
  const navigate = useNavigate();
  
  // Get employee name from nested object
  const employeeName = payslip.employee?.full_name || 'Unknown Employee';
  
  const handleViewDetails = () => {
    navigate(`/payslip/${payslip.id}`);
  };
  
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
        <div>
          <h3>Payslip for {employeeName}</h3>
          <p><strong>Period:</strong> {payslip.payroll_run?.period_start_date} to {payslip.payroll_run?.period_end_date}</p>
        </div>
        <button 
          onClick={handleViewDetails}
          className="btn btn-primary"
          style={{ fontSize: '14px', padding: '8px 16px' }}
        >
          View Details
        </button>
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '250px', marginBottom: '15px' }}>
          <h4>Earnings</h4>
          <p>Gross Salary: KES {parseFloat(payslip.gross_salary).toLocaleString()}</p>
          <p>Overtime Pay: KES {parseFloat(payslip.overtime_pay).toLocaleString()}</p>
          <p><strong>Total Gross Income:</strong> KES {parseFloat(payslip.total_gross_income).toLocaleString()}</p>
        </div>
        <div style={{ flex: 1, minWidth: '250px', marginBottom: '15px' }}>
          <h4>Deductions</h4>
          <p>PAYE Tax: KES {parseFloat(payslip.paye_tax).toLocaleString()}</p>
          <p>NSSF: KES {parseFloat(payslip.nssf_deduction).toLocaleString()}</p>
          <p>SHIF: KES {parseFloat(payslip.shif_deduction).toLocaleString()}</p>
          <p>AHL: KES {parseFloat(payslip.ahl_deduction).toLocaleString()}</p>
          <p>HELB: KES {parseFloat(payslip.helb_deduction).toLocaleString()}</p>
          <p><strong>Total Deductions:</strong> KES {parseFloat(payslip.total_deductions).toLocaleString()}</p>
        </div>
      </div>
      <h3 style={{ marginTop: '15px' }}>Net Pay: <span style={{ color: '#28a745' }}>KES {parseFloat(payslip.net_pay).toLocaleString()}</span></h3>
    </div>
  );
};

export default PayslipCard;
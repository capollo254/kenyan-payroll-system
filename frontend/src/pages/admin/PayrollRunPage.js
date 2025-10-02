// src/pages/admin/PayrollRunPage.js

import React, { useState } from 'react';
import CreatePayrollRunForm from '../../components/forms/CreatePayrollRunForm';

const PayrollRunPage = () => {
  const [successMessage, setSuccessMessage] = useState(null);

  const handleRunCreated = () => {
    setSuccessMessage("Payroll run initiated successfully. Payslips are being generated.");
  };

  return (
    <div className="container page">
      <h2>Payroll Run</h2>
      {successMessage && <div className="message success">{successMessage}</div>}
      <CreatePayrollRunForm onRunCreated={handleRunCreated} />
    </div>
  );
};

export default PayrollRunPage;
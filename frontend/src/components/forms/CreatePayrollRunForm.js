// src/components/forms/CreatePayrollRunForm.js

import React, { useState } from 'react';
import InputField from '../common/InputField';
import Button from '../common/Button';
import { createPayrollRun } from '../../api/payroll';

/**
 * A form component to create a new payroll run.
 * @param {object} props - Component props.
 * @param {function} props.onRunCreated - Callback function to run on successful payroll run creation.
 */
const CreatePayrollRunForm = ({ onRunCreated }) => {
  const [runDate, setRunDate] = useState('');
  const [periodStartDate, setPeriodStartDate] = useState('');
  const [periodEndDate, setPeriodEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const data = {
        run_date: runDate,
        period_start_date: periodStartDate,
        period_end_date: periodEndDate,
      };
      await createPayrollRun(data);
      setSuccess('Payroll run created successfully! Payslips are being generated.');
      onRunCreated();
    } catch (err) {
      console.error('Error creating payroll run:', err);
      setError('Failed to create payroll run. Please check the dates.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Run New Payroll</h2>
      <form onSubmit={handleSubmit}>
        <InputField
          label="Run Date"
          type="date"
          value={runDate}
          onChange={(e) => setRunDate(e.target.value)}
          required
        />
        <InputField
          label="Payroll Period Start Date"
          type="date"
          value={periodStartDate}
          onChange={(e) => setPeriodStartDate(e.target.value)}
          required
        />
        <InputField
          label="Payroll Period End Date"
          type="date"
          value={periodEndDate}
          onChange={(e) => setPeriodEndDate(e.target.value)}
          required
        />
        {error && <p className="error">{error}</p>}
        {success && <p className="message success">{success}</p>}
        <Button type="submit" className="btn-success" disabled={loading}>
          {loading ? 'Running...' : 'Create Payroll Run'}
        </Button>
      </form>
    </div>
  );
};

export default CreatePayrollRunForm;
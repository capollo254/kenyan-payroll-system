// src/pages/admin/PayrollPage.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPayrollRuns, createPayrollRun } from '../../api/payroll';
import { getEmployees } from '../../api/employees';
import { getStatutoryRates, updateStatutoryRates } from '../../api/compliance';
import { getVoluntaryDeductions, createVoluntaryDeduction, deleteVoluntaryDeduction, 
         getEmployeeBenefits, createEmployeeBenefit, deleteEmployeeBenefit } from '../../api/deductions';
import Button from '../../components/common/Button';
import InputField from '../../components/common/InputField';
import AdminProfileWidget from '../../components/common/AdminProfileWidget';

const PayrollPage = () => {
  const [activeTab, setActiveTab] = useState('run');
  const [payrollRuns, setPayrollRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [runData, setRunData] = useState({
    period_start_date: '',
    period_end_date: ''
  });
  
  // Deductions and Benefits state
  const [activeDeductionTab, setActiveDeductionTab] = useState('statutory');
  const [statutoryRates, setStatutoryRates] = useState({
    nssf_rate: '6.0',
    shif_rate: '2.75',
    ahl_rate: '1.5'
  });
  const [voluntaryDeductions, setVoluntaryDeductions] = useState([
    { id: 1, name: 'Employee Savings', type: 'percentage', rate: '5.0', description: 'Monthly savings plan' },
    { id: 2, name: 'Union Dues', type: 'fixed', rate: '500', description: 'Monthly union contribution' }
  ]);
  const [benefits, setBenefits] = useState([
    { id: 1, name: 'Transport Allowance', type: 'fixed', amount: '5000', description: 'Monthly transport allowance' },
    { id: 2, name: 'Medical Insurance', type: 'percentage', amount: '2.0', description: 'Health insurance contribution' }
  ]);
  const [newDeduction, setNewDeduction] = useState({ name: '', type: 'fixed', rate: '', description: '' });
  const [newBenefit, setNewBenefit] = useState({ name: '', type: 'fixed', amount: '', description: '' });
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchPayrollRuns();
  }, []);

  const fetchPayrollRuns = async () => {
    try {
      const data = await getPayrollRuns();
      setPayrollRuns(data || []);
    } catch (err) {
      console.error('Failed to fetch payroll runs:', err);
      setError('Failed to load payroll history.');
    }
  };

  const handleRunPayroll = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await createPayrollRun(runData);
      setSuccess('Payroll run initiated successfully! Payslips are being generated.');
      setRunData({ period_start_date: '', period_end_date: '' });
      await fetchPayrollRuns(); // Refresh the list
    } catch (err) {
      console.error('Failed to run payroll:', err);
      setError('Failed to initiate payroll run. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Data loading useEffect
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load payroll runs
      const payrollData = await getPayrollRuns();
      setPayrollRuns(payrollData.results || payrollData);
      
      // Load statutory rates
      const ratesData = await getStatutoryRates();
      setStatutoryRates({
        nssf_rate: ratesData.nssf?.rate_percentage || 6.0,
        shif_rate: ratesData.shif?.rate_percentage || 2.75,
        ahl_rate: ratesData.ahl?.rate_percentage || 1.5
      });
      
      // Load voluntary deductions
      const deductionsData = await getVoluntaryDeductions();
      setVoluntaryDeductions(deductionsData.results || deductionsData || []);
      
      // Load benefits
      const benefitsData = await getEmployeeBenefits();
      setBenefits(benefitsData.results || benefitsData || []);
      
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load payroll data. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  };

  // Statutory rates handlers
  const handleStatutoryRateChange = (e) => {
    setStatutoryRates({
      ...statutoryRates,
      [e.target.name]: parseFloat(e.target.value) || 0
    });
  };

  const saveStatutoryRates = async () => {
    try {
      setLoading(true);
      await updateStatutoryRates({
        nssf_rate: statutoryRates.nssf_rate / 100, // Convert percentage to decimal
        shif_rate: statutoryRates.shif_rate / 100,
        ahl_rate: statutoryRates.ahl_rate / 100,
        effective_date: new Date().toISOString().split('T')[0]
      });
      setSuccess('Statutory rates updated successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to update statutory rates:', err);
      setError('Failed to update statutory rates. Please try again.');
      setTimeout(() => setError(null), 3000);
    } finally {
      setLoading(false);
    }
  };

  // Voluntary deductions handlers
  const handleNewDeductionChange = (e) => {
    setNewDeduction({
      ...newDeduction,
      [e.target.name]: e.target.value
    });
  };

  const addVoluntaryDeduction = async (e) => {
    e.preventDefault();
    if (newDeduction.name && newDeduction.rate) {
      try {
        setLoading(true);
        const deductionData = {
          name: newDeduction.name,
          deduction_type: 'other',
          calculation_type: newDeduction.type,
          amount: parseFloat(newDeduction.rate),
          description: newDeduction.description,
          start_date: new Date().toISOString().split('T')[0],
          is_active: true
        };
        
        const newDeductionObj = await createVoluntaryDeduction(deductionData);
        setVoluntaryDeductions([...voluntaryDeductions, newDeductionObj]);
        setNewDeduction({ name: '', type: 'fixed', rate: '', description: '' });
        setSuccess('Deduction added successfully!');
        setTimeout(() => setSuccess(null), 3000);
      } catch (err) {
        console.error('Failed to add deduction:', err);
        setError('Failed to add deduction. Please try again.');
        setTimeout(() => setError(null), 3000);
      } finally {
        setLoading(false);
      }
    }
  };

  const removeVoluntaryDeduction = async (id) => {
    try {
      setLoading(true);
      await deleteVoluntaryDeduction(id);
      setVoluntaryDeductions(voluntaryDeductions.filter(d => d.id !== id));
      setSuccess('Deduction removed successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to remove deduction:', err);
      setError('Failed to remove deduction. Please try again.');
      setTimeout(() => setError(null), 3000);
    } finally {
      setLoading(false);
    }
  };

  // Benefits handlers
  const handleNewBenefitChange = (e) => {
    setNewBenefit({
      ...newBenefit,
      [e.target.name]: e.target.value
    });
  };

  const addBenefit = async (e) => {
    e.preventDefault();
    if (newBenefit.name && newBenefit.amount) {
      try {
        setLoading(true);
        const benefitData = {
          name: newBenefit.name,
          benefit_type: 'other',
          calculation_type: newBenefit.type,
          amount: parseFloat(newBenefit.amount),
          description: newBenefit.description,
          is_taxable: true,
          is_active: true
        };
        
        const newBenefitObj = await createEmployeeBenefit(benefitData);
        setBenefits([...benefits, newBenefitObj]);
        setNewBenefit({ name: '', type: 'fixed', amount: '', description: '' });
        setSuccess('Benefit added successfully!');
        setTimeout(() => setSuccess(null), 3000);
      } catch (err) {
        console.error('Failed to add benefit:', err);
        setError('Failed to add benefit. Please try again.');
        setTimeout(() => setError(null), 3000);
      } finally {
        setLoading(false);
      }
    }
  };

  const removeBenefit = async (id) => {
    try {
      setLoading(true);
      await deleteEmployeeBenefit(id);
      setBenefits(benefits.filter(b => b.id !== id));
      setSuccess('Benefit removed successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to remove benefit:', err);
      setError('Failed to remove benefit. Please try again.');
      setTimeout(() => setError(null), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setRunData({
      ...runData,
      [e.target.name]: e.target.value
    });
  };

  const tabStyle = (tabName) => ({
    padding: '10px 20px',
    border: 'none',
    backgroundColor: activeTab === tabName ? 'var(--primary-color)' : 'var(--light-color)',
    color: activeTab === tabName ? 'white' : 'var(--dark-color)',
    cursor: 'pointer',
    borderRadius: '5px 5px 0 0',
    marginRight: '5px'
  });

  const deductionTabStyle = (tabName) => ({
    padding: '8px 16px',
    border: 'none',
    backgroundColor: activeDeductionTab === tabName ? 'var(--primary-color)' : 'var(--light-color)',
    color: activeDeductionTab === tabName ? 'white' : 'var(--dark-color)',
    cursor: 'pointer',
    borderRadius: '5px',
    marginRight: '10px',
    fontSize: '14px'
  });

  return (
    <div className="container page">
      {/* Admin Profile Widget */}
      <AdminProfileWidget />
      
      <h2>Payroll Management</h2>
      
      {/* Tab Navigation */}
      <div style={{ marginBottom: '20px', borderBottom: '1px solid var(--border-color)' }}>
        <button style={tabStyle('run')} onClick={() => setActiveTab('run')}>
          Run Payroll
        </button>
        <button style={tabStyle('history')} onClick={() => setActiveTab('history')}>
          Payroll History
        </button>
        <button style={tabStyle('deductions')} onClick={() => setActiveTab('deductions')}>
          Deductions & Benefits
        </button>
      </div>

      {success && <div className="alert alert-success">{success}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Run Payroll Tab */}
      {activeTab === 'run' && (
        <div className="card">
          <h3>Generate Payroll Run</h3>
          <p>Create a new payroll run for all active employees. This will calculate salaries, deductions, and generate payslips.</p>
          
          <form onSubmit={handleRunPayroll} style={{ marginTop: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              <InputField
                label="Period Start Date"
                type="date"
                name="period_start_date"
                value={runData.period_start_date}
                onChange={handleInputChange}
                required
              />
              <InputField
                label="Period End Date"
                type="date"
                name="period_end_date"
                value={runData.period_end_date}
                onChange={handleInputChange}
                required
              />
            </div>
            
            <div style={{ marginTop: '20px' }}>
              <Button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'Processing...' : 'Run Payroll'}
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Payroll History Tab */}
      {activeTab === 'history' && (
        <div className="card">
          <h3>Payroll History</h3>
          <p>View all previous payroll runs and their details.</p>
          
          {payrollRuns.length > 0 ? (
            <div style={{ overflowX: 'auto', marginTop: '20px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--light-color)' }}>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Run Date</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Period</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Total Net Pay</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Total Deductions</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {payrollRuns.map((run) => (
                    <tr key={run.id}>
                      <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{run.run_date}</td>
                      <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                        {run.period_start_date} to {run.period_end_date}
                      </td>
                      <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                        KES {parseFloat(run.total_net_pay || 0).toLocaleString()}
                      </td>
                      <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                        KES {parseFloat(run.total_deductions || 0).toLocaleString()}
                      </td>
                      <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                        <button className="btn btn-sm btn-secondary">View Details</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No payroll runs found.</p>
          )}
        </div>
      )}

      {/* Deductions & Benefits Tab */}
      {activeTab === 'deductions' && (
        <div className="card">
          <h3>Deductions & Benefits Management</h3>
          <p>Manage standard deductions like taxes and social security, as well as benefits like health insurance.</p>
          
          {/* Sub-tab Navigation */}
          <div style={{ marginTop: '20px', marginBottom: '20px' }}>
            <button style={deductionTabStyle('statutory')} onClick={() => setActiveDeductionTab('statutory')}>
              Statutory Rates
            </button>
            <button style={deductionTabStyle('voluntary')} onClick={() => setActiveDeductionTab('voluntary')}>
              Voluntary Deductions
            </button>
            <button style={deductionTabStyle('benefits')} onClick={() => setActiveDeductionTab('benefits')}>
              Employee Benefits
            </button>
          </div>

          {/* Statutory Rates Section */}
          {activeDeductionTab === 'statutory' && (
            <div>
              <h4>Configure Statutory Deduction Rates</h4>
              <p>Set the rates for mandatory government deductions.</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '20px' }}>
                <InputField
                  label="NSSF Rate (%)"
                  type="number"
                  name="nssf_rate"
                  value={statutoryRates.nssf_rate}
                  onChange={handleStatutoryRateChange}
                  step="0.1"
                  min="0"
                  max="100"
                />
                <InputField
                  label="SHIF Rate (%)"
                  type="number"
                  name="shif_rate"
                  value={statutoryRates.shif_rate}
                  onChange={handleStatutoryRateChange}
                  step="0.1"
                  min="0"
                  max="100"
                />
                <InputField
                  label="AHL Rate (%)"
                  type="number"
                  name="ahl_rate"
                  value={statutoryRates.ahl_rate}
                  onChange={handleStatutoryRateChange}
                  step="0.1"
                  min="0"
                  max="100"
                />
              </div>
              
              <div style={{ marginTop: '20px' }}>
                <Button onClick={saveStatutoryRates} className="btn-primary">
                  Save Statutory Rates
                </Button>
              </div>
            </div>
          )}

          {/* Voluntary Deductions Section */}
          {activeDeductionTab === 'voluntary' && (
            <div>
              <h4>Manage Voluntary Deductions</h4>
              <p>Add and manage optional deductions like savings, loans, and insurance.</p>
              
              {/* Add New Deduction Form */}
              <div className="card" style={{ backgroundColor: 'var(--light-color)', marginTop: '20px' }}>
                <h5>Add New Deduction</h5>
                <form onSubmit={addVoluntaryDeduction}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                    <InputField
                      label="Deduction Name"
                      type="text"
                      name="name"
                      value={newDeduction.name}
                      onChange={handleNewDeductionChange}
                      required
                    />
                    <div className="form-group">
                      <label htmlFor="deduction-type">Type</label>
                      <select
                        id="deduction-type"
                        name="type"
                        value={newDeduction.type}
                        onChange={handleNewDeductionChange}
                        required
                      >
                        <option value="fixed">Fixed Amount (KES)</option>
                        <option value="percentage">Percentage (%)</option>
                      </select>
                    </div>
                    <InputField
                      label={newDeduction.type === 'percentage' ? 'Rate (%)' : 'Amount (KES)'}
                      type="number"
                      name="rate"
                      value={newDeduction.rate}
                      onChange={handleNewDeductionChange}
                      step={newDeduction.type === 'percentage' ? '0.1' : '1'}
                      min="0"
                      required
                    />
                    <InputField
                      label="Description"
                      type="text"
                      name="description"
                      value={newDeduction.description}
                      onChange={handleNewDeductionChange}
                    />
                  </div>
                  <div style={{ marginTop: '15px' }}>
                    <Button type="submit" className="btn-primary">Add Deduction</Button>
                  </div>
                </form>
              </div>

              {/* Existing Deductions List */}
              <div style={{ marginTop: '20px' }}>
                <h5>Current Voluntary Deductions</h5>
                {voluntaryDeductions.length > 0 ? (
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
                      <thead>
                        <tr style={{ backgroundColor: 'var(--light-color)' }}>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Name</th>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Type</th>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Rate/Amount</th>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Description</th>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {voluntaryDeductions.map((deduction) => (
                          <tr key={deduction.id}>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{deduction.name}</td>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                              {deduction.type === 'percentage' ? 'Percentage' : 'Fixed Amount'}
                            </td>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                              {deduction.type === 'percentage' ? `${deduction.rate}%` : `KES ${deduction.rate}`}
                            </td>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{deduction.description}</td>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                              <button 
                                className="btn btn-sm btn-danger"
                                onClick={() => removeVoluntaryDeduction(deduction.id)}
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p style={{ fontStyle: 'italic', color: 'var(--muted-color)' }}>No voluntary deductions configured.</p>
                )}
              </div>
            </div>
          )}

          {/* Benefits Section */}
          {activeDeductionTab === 'benefits' && (
            <div>
              <h4>Manage Employee Benefits</h4>
              <p>Configure employee benefits like allowances and insurance.</p>
              
              {/* Add New Benefit Form */}
              <div className="card" style={{ backgroundColor: 'var(--light-color)', marginTop: '20px' }}>
                <h5>Add New Benefit</h5>
                <form onSubmit={addBenefit}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                    <InputField
                      label="Benefit Name"
                      type="text"
                      name="name"
                      value={newBenefit.name}
                      onChange={handleNewBenefitChange}
                      required
                    />
                    <div className="form-group">
                      <label htmlFor="benefit-type">Type</label>
                      <select
                        id="benefit-type"
                        name="type"
                        value={newBenefit.type}
                        onChange={handleNewBenefitChange}
                        required
                      >
                        <option value="fixed">Fixed Amount (KES)</option>
                        <option value="percentage">Percentage (%)</option>
                      </select>
                    </div>
                    <InputField
                      label={newBenefit.type === 'percentage' ? 'Rate (%)' : 'Amount (KES)'}
                      type="number"
                      name="amount"
                      value={newBenefit.amount}
                      onChange={handleNewBenefitChange}
                      step={newBenefit.type === 'percentage' ? '0.1' : '1'}
                      min="0"
                      required
                    />
                    <InputField
                      label="Description"
                      type="text"
                      name="description"
                      value={newBenefit.description}
                      onChange={handleNewBenefitChange}
                    />
                  </div>
                  <div style={{ marginTop: '15px' }}>
                    <Button type="submit" className="btn-primary">Add Benefit</Button>
                  </div>
                </form>
              </div>

              {/* Existing Benefits List */}
              <div style={{ marginTop: '20px' }}>
                <h5>Current Employee Benefits</h5>
                {benefits.length > 0 ? (
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
                      <thead>
                        <tr style={{ backgroundColor: 'var(--light-color)' }}>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Name</th>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Type</th>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Amount</th>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Description</th>
                          <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {benefits.map((benefit) => (
                          <tr key={benefit.id}>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{benefit.name}</td>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                              {benefit.type === 'percentage' ? 'Percentage' : 'Fixed Amount'}
                            </td>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                              {benefit.type === 'percentage' ? `${benefit.amount}%` : `KES ${benefit.amount}`}
                            </td>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{benefit.description}</td>
                            <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                              <button 
                                className="btn btn-sm btn-danger"
                                onClick={() => removeBenefit(benefit.id)}
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p style={{ fontStyle: 'italic', color: 'var(--muted-color)' }}>No employee benefits configured.</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PayrollPage;
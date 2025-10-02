// src/pages/admin/SettingsPage.js

import React, { useState } from 'react';
import Button from '../../components/common/Button';
import InputField from '../../components/common/InputField';

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('company');
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  
  const [companySettings, setCompanySettings] = useState({
    companyName: 'PlayLearn Academy',
    address: '123 Business Street, Nairobi, Kenya',
    phone: '+254 700 123 456',
    email: 'info@playlearnacademy.co.ke',
    taxId: 'A12345678Z',
    registrationNumber: 'C.12345',
    bankAccount: '1234567890',
    bankName: 'Equity Bank',
    bankBranch: 'Westlands'
  });

  const [payrollSettings, setPayrollSettings] = useState({
    payPeriod: 'monthly',
    payDay: '25',
    currency: 'KES',
    overtimeRate: '1.5',
    defaultWorkingHours: '8',
    defaultWorkingDays: '22',
    taxYear: '2025'
  });

  const [systemSettings, setSystemSettings] = useState({
    timezone: 'Africa/Nairobi',
    dateFormat: 'DD/MM/YYYY',
    numberFormat: 'comma',
    emailNotifications: true,
    smsNotifications: false,
    backupFrequency: 'daily',
    sessionTimeout: '60'
  });

  const [taxRates, setTaxRates] = useState({
    nssfRate: '6.0',
    shifRate: '2.75',
    ahlRate: '1.5',
    payeTiers: [
      { min: 0, max: 24000, rate: 10 },
      { min: 24001, max: 32333, rate: 25 },
      { min: 32334, max: 500000, rate: 30 },
      { min: 500001, max: 800000, rate: 32.5 },
      { min: 800001, max: Infinity, rate: 35 }
    ]
  });

  const handleCompanyChange = (e) => {
    setCompanySettings({
      ...companySettings,
      [e.target.name]: e.target.value
    });
  };

  const handlePayrollChange = (e) => {
    setPayrollSettings({
      ...payrollSettings,
      [e.target.name]: e.target.value
    });
  };

  const handleSystemChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSystemSettings({
      ...systemSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSaveSettings = async (settingsType) => {
    try {
      // Mock save operation
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess(`${settingsType} settings saved successfully!`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(`Failed to save ${settingsType} settings.`);
      setTimeout(() => setError(null), 3000);
    }
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

  return (
    <div className="container page">
      <h2>System Settings</h2>
      <p>Configure global payroll settings, company information, and system-wide options.</p>

      {/* Tab Navigation */}
      <div style={{ marginBottom: '20px', borderBottom: '1px solid var(--border-color)' }}>
        <button style={tabStyle('company')} onClick={() => setActiveTab('company')}>
          Company Info
        </button>
        <button style={tabStyle('payroll')} onClick={() => setActiveTab('payroll')}>
          Payroll Settings
        </button>
        <button style={tabStyle('taxes')} onClick={() => setActiveTab('taxes')}>
          Tax Rates
        </button>
        <button style={tabStyle('system')} onClick={() => setActiveTab('system')}>
          System Settings
        </button>
      </div>

      {success && <div className="alert alert-success">{success}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Company Information Tab */}
      {activeTab === 'company' && (
        <div className="card">
          <h3>Company Information</h3>
          <p>Update your company details and legal information.</p>
          
          <form onSubmit={(e) => { e.preventDefault(); handleSaveSettings('Company'); }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
              <InputField
                label="Company Name"
                type="text"
                name="companyName"
                value={companySettings.companyName}
                onChange={handleCompanyChange}
                required
              />
              <InputField
                label="Tax ID"
                type="text"
                name="taxId"
                value={companySettings.taxId}
                onChange={handleCompanyChange}
                required
              />
              <InputField
                label="Registration Number"
                type="text"
                name="registrationNumber"
                value={companySettings.registrationNumber}
                onChange={handleCompanyChange}
                required
              />
              <InputField
                label="Phone Number"
                type="tel"
                name="phone"
                value={companySettings.phone}
                onChange={handleCompanyChange}
                required
              />
              <InputField
                label="Email Address"
                type="email"
                name="email"
                value={companySettings.email}
                onChange={handleCompanyChange}
                required
              />
              <InputField
                label="Bank Name"
                type="text"
                name="bankName"
                value={companySettings.bankName}
                onChange={handleCompanyChange}
              />
              <InputField
                label="Bank Account Number"
                type="text"
                name="bankAccount"
                value={companySettings.bankAccount}
                onChange={handleCompanyChange}
              />
              <InputField
                label="Bank Branch"
                type="text"
                name="bankBranch"
                value={companySettings.bankBranch}
                onChange={handleCompanyChange}
              />
            </div>
            
            <div className="form-group" style={{ marginTop: '20px' }}>
              <label htmlFor="address">Company Address</label>
              <textarea
                id="address"
                name="address"
                value={companySettings.address}
                onChange={handleCompanyChange}
                rows="3"
                style={{ width: '100%', padding: '10px', border: '1px solid var(--border-color)', borderRadius: '5px' }}
                required
              />
            </div>

            <div style={{ marginTop: '20px' }}>
              <Button type="submit" className="btn-primary">
                Save Company Information
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Payroll Settings Tab */}
      {activeTab === 'payroll' && (
        <div className="card">
          <h3>Payroll Configuration</h3>
          <p>Configure default payroll processing parameters.</p>
          
          <form onSubmit={(e) => { e.preventDefault(); handleSaveSettings('Payroll'); }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label htmlFor="payPeriod">Pay Period</label>
                <select
                  id="payPeriod"
                  name="payPeriod"
                  value={payrollSettings.payPeriod}
                  onChange={handlePayrollChange}
                  required
                >
                  <option value="weekly">Weekly</option>
                  <option value="bi-weekly">Bi-Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                </select>
              </div>
              
              <InputField
                label="Pay Day (Day of Month)"
                type="number"
                name="payDay"
                value={payrollSettings.payDay}
                onChange={handlePayrollChange}
                min="1"
                max="31"
                required
              />
              
              <div className="form-group">
                <label htmlFor="currency">Currency</label>
                <select
                  id="currency"
                  name="currency"
                  value={payrollSettings.currency}
                  onChange={handlePayrollChange}
                  required
                >
                  <option value="KES">KES - Kenyan Shilling</option>
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                </select>
              </div>
              
              <InputField
                label="Overtime Rate Multiplier"
                type="number"
                name="overtimeRate"
                value={payrollSettings.overtimeRate}
                onChange={handlePayrollChange}
                step="0.1"
                required
              />
              
              <InputField
                label="Default Working Hours per Day"
                type="number"
                name="defaultWorkingHours"
                value={payrollSettings.defaultWorkingHours}
                onChange={handlePayrollChange}
                min="1"
                max="24"
                required
              />
              
              <InputField
                label="Default Working Days per Month"
                type="number"
                name="defaultWorkingDays"
                value={payrollSettings.defaultWorkingDays}
                onChange={handlePayrollChange}
                min="1"
                max="31"
                required
              />
              
              <InputField
                label="Tax Year"
                type="number"
                name="taxYear"
                value={payrollSettings.taxYear}
                onChange={handlePayrollChange}
                min="2020"
                max="2030"
                required
              />
            </div>

            <div style={{ marginTop: '20px' }}>
              <Button type="submit" className="btn-primary">
                Save Payroll Settings
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Tax Rates Tab */}
      {activeTab === 'taxes' && (
        <div className="card">
          <h3>Tax Rates Configuration</h3>
          <p>Configure statutory deduction rates and PAYE tax brackets.</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            <InputField
              label="NSSF Rate (%)"
              type="number"
              value={taxRates.nssfRate}
              onChange={(e) => setTaxRates({...taxRates, nssfRate: e.target.value})}
              step="0.1"
              min="0"
              max="100"
            />
            <InputField
              label="SHIF Rate (%)"
              type="number"
              value={taxRates.shifRate}
              onChange={(e) => setTaxRates({...taxRates, shifRate: e.target.value})}
              step="0.1"
              min="0"
              max="100"
            />
            <InputField
              label="AHL Rate (%)"
              type="number"
              value={taxRates.ahlRate}
              onChange={(e) => setTaxRates({...taxRates, ahlRate: e.target.value})}
              step="0.1"
              min="0"
              max="100"
            />
          </div>

          <h4>PAYE Tax Brackets</h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '15px' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--light-color)' }}>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Minimum (KES)</th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Maximum (KES)</th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Rate (%)</th>
              </tr>
            </thead>
            <tbody>
              {taxRates.payeTiers.map((tier, index) => (
                <tr key={index}>
                  <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                    {tier.min.toLocaleString()}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                    {tier.max === Infinity ? 'Above' : tier.max.toLocaleString()}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                    {tier.rate}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: '20px' }}>
            <Button onClick={() => handleSaveSettings('Tax rates')} className="btn-primary">
              Save Tax Rates
            </Button>
          </div>
        </div>
      )}

      {/* System Settings Tab */}
      {activeTab === 'system' && (
        <div className="card">
          <h3>System Configuration</h3>
          <p>Configure system-wide preferences and operational settings.</p>
          
          <form onSubmit={(e) => { e.preventDefault(); handleSaveSettings('System'); }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label htmlFor="timezone">Timezone</label>
                <select
                  id="timezone"
                  name="timezone"
                  value={systemSettings.timezone}
                  onChange={handleSystemChange}
                  required
                >
                  <option value="Africa/Nairobi">Africa/Nairobi (EAT)</option>
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">America/New_York (EST)</option>
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="dateFormat">Date Format</label>
                <select
                  id="dateFormat"
                  name="dateFormat"
                  value={systemSettings.dateFormat}
                  onChange={handleSystemChange}
                  required
                >
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="numberFormat">Number Format</label>
                <select
                  id="numberFormat"
                  name="numberFormat"
                  value={systemSettings.numberFormat}
                  onChange={handleSystemChange}
                  required
                >
                  <option value="comma">1,234.56</option>
                  <option value="space">1 234.56</option>
                  <option value="period">1.234,56</option>
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="backupFrequency">Backup Frequency</label>
                <select
                  id="backupFrequency"
                  name="backupFrequency"
                  value={systemSettings.backupFrequency}
                  onChange={handleSystemChange}
                  required
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              
              <InputField
                label="Session Timeout (minutes)"
                type="number"
                name="sessionTimeout"
                value={systemSettings.sessionTimeout}
                onChange={handleSystemChange}
                min="5"
                max="480"
                required
              />
            </div>

            <div style={{ marginTop: '30px' }}>
              <h4>Notification Settings</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px' }}>
                <label>
                  <input
                    type="checkbox"
                    name="emailNotifications"
                    checked={systemSettings.emailNotifications}
                    onChange={handleSystemChange}
                    style={{ marginRight: '8px' }}
                  />
                  Enable Email Notifications
                </label>
                <label>
                  <input
                    type="checkbox"
                    name="smsNotifications"
                    checked={systemSettings.smsNotifications}
                    onChange={handleSystemChange}
                    style={{ marginRight: '8px' }}
                  />
                  Enable SMS Notifications
                </label>
              </div>
            </div>

            <div style={{ marginTop: '20px' }}>
              <Button type="submit" className="btn-primary">
                Save System Settings
              </Button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
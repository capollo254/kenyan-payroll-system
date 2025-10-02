// src/components/EmployeeBankingDetails.js

import React, { useState, useEffect } from 'react';
import {
  getMyBankingDetails,
  updateMyBankingDetails,
  validateBankingInfo,
  formatBankingInfo,
  getAccountTypes,
  getMobileMoneyProviders,
  getKenyanBanks
} from '../api/employees';

const EmployeeBankingDetails = () => {
  const [bankingData, setBankingData] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [formData, setFormData] = useState({});

  // Get dropdown options
  const accountTypes = getAccountTypes();
  const mobileMoneyProviders = getMobileMoneyProviders();
  const kenyanBanks = getKenyanBanks();

  useEffect(() => {
    fetchBankingDetails();
  }, []);

  const fetchBankingDetails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getMyBankingDetails();
      setBankingData(data);
      setFormData({
        bank_name: data.bank_name || '',
        bank_code: data.bank_code || '',
        bank_branch: data.bank_branch || '',
        bank_branch_code: data.bank_branch_code || '',
        bank_account_number: data.bank_account_number || '',
        account_type: data.account_type || '',
        account_holder_name: data.account_holder_name || data.full_name || '',
        mobile_money_provider: data.mobile_money_provider || '',
        mobile_money_number: data.mobile_money_number || ''
      });
    } catch (err) {
      setError('Failed to fetch banking details: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Auto-fill bank code when bank is selected
    if (name === 'bank_name') {
      const selectedBank = kenyanBanks.find(bank => bank.name === value);
      if (selectedBank) {
        setFormData(prev => ({
          ...prev,
          bank_code: selectedBank.code
        }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const updatedData = await updateMyBankingDetails(formData);
      setBankingData(updatedData);
      setIsEditing(false);
      setSuccess('Banking details updated successfully!');
    } catch (err) {
      setError('Failed to update banking details: ' + err.message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      bank_name: bankingData.bank_name || '',
      bank_code: bankingData.bank_code || '',
      bank_branch: bankingData.bank_branch || '',
      bank_branch_code: bankingData.bank_branch_code || '',
      bank_account_number: bankingData.bank_account_number || '',
      account_type: bankingData.account_type || '',
      account_holder_name: bankingData.account_holder_name || bankingData.full_name || '',
      mobile_money_provider: bankingData.mobile_money_provider || '',
      mobile_money_number: bankingData.mobile_money_number || ''
    });
    setError(null);
  };

  const validation = bankingData ? validateBankingInfo(bankingData) : null;
  const formattedInfo = bankingData ? formatBankingInfo(bankingData) : null;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading banking details...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Banking Information</h2>
          <p className="text-gray-600">
            Employee: <span className="font-semibold">{bankingData?.full_name}</span>
          </p>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Edit Banking Details
          </button>
        )}
      </div>

      {/* Banking Completion Status */}
      {validation && (
        <div className={`mb-6 p-4 rounded-lg border ${
          validation.isComplete 
            ? 'bg-green-50 border-green-200' 
            : 'bg-yellow-50 border-yellow-200'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">
                {validation.isComplete ? '✅ Banking Information Complete' : '⚠️ Banking Information Incomplete'}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Completion: {validation.completionPercentage}%
              </p>
            </div>
            {!validation.isComplete && (
              <div className="text-sm text-gray-600">
                Missing: {validation.missingFields.join(', ')}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Success/Error Messages */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-green-800">{success}</p>
        </div>
      )}
      
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Banking Details Content */}
      {isEditing ? (
        // Edit Form
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Bank Information Section */}
            <div className="col-span-2">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 border-b pb-2">
                Bank Account Information
              </h3>
            </div>

            {/* Bank Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bank Name *
              </label>
              <select
                name="bank_name"
                value={formData.bank_name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select Bank</option>
                {kenyanBanks.map((bank) => (
                  <option key={bank.code} value={bank.name}>
                    {bank.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Bank Code */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bank Code *
              </label>
              <input
                type="text"
                name="bank_code"
                value={formData.bank_code}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 68"
                required
              />
            </div>

            {/* Bank Branch */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bank Branch *
              </label>
              <input
                type="text"
                name="bank_branch"
                value={formData.bank_branch}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Westlands Branch"
                required
              />
            </div>

            {/* Branch Code */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Branch Code *
              </label>
              <input
                type="text"
                name="bank_branch_code"
                value={formData.bank_branch_code}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 068"
                required
              />
            </div>

            {/* Account Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Account Number *
              </label>
              <input
                type="text"
                name="bank_account_number"
                value={formData.bank_account_number}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Bank account number"
                required
              />
            </div>

            {/* Account Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Account Type *
              </label>
              <select
                name="account_type"
                value={formData.account_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select Account Type</option>
                {accountTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Account Holder Name */}
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Account Holder Name
              </label>
              <input
                type="text"
                name="account_holder_name"
                value={formData.account_holder_name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="As it appears on bank account"
              />
            </div>

            {/* Mobile Money Section */}
            <div className="col-span-2">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 border-b pb-2 mt-6">
                Mobile Money Information (Optional)
              </h3>
            </div>

            {/* Mobile Money Provider */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mobile Money Provider
              </label>
              <select
                name="mobile_money_provider"
                value={formData.mobile_money_provider}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Provider</option>
                {mobileMoneyProviders.map((provider) => (
                  <option key={provider.value} value={provider.value}>
                    {provider.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Mobile Money Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mobile Money Number
              </label>
              <input
                type="text"
                name="mobile_money_number"
                value={formData.mobile_money_number}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 0712345678"
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-4 pt-6 border-t">
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
              disabled={isSaving}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Banking Details'}
            </button>
          </div>
        </form>
      ) : (
        // Display Mode
        <div className="space-y-6">
          {/* Bank Account Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900 border-b pb-2">
              Bank Account Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-sm font-medium text-gray-500">Bank Name</span>
                <p className="text-gray-900">{bankingData?.bank_name || 'Not specified'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Bank Code</span>
                <p className="text-gray-900">{bankingData?.bank_code || 'Not specified'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Branch</span>
                <p className="text-gray-900">{bankingData?.bank_branch || 'Not specified'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Branch Code</span>
                <p className="text-gray-900">{bankingData?.bank_branch_code || 'Not specified'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Account Number</span>
                <p className="text-gray-900 font-mono">{bankingData?.bank_account_number || 'Not specified'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Account Type</span>
                <p className="text-gray-900">{bankingData?.account_type_display || 'Not specified'}</p>
              </div>
              <div className="md:col-span-2">
                <span className="text-sm font-medium text-gray-500">Account Holder</span>
                <p className="text-gray-900">{bankingData?.account_holder_name || 'Not specified'}</p>
              </div>
            </div>
          </div>

          {/* Mobile Money Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900 border-b pb-2">
              Mobile Money Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-sm font-medium text-gray-500">Provider</span>
                <p className="text-gray-900">{bankingData?.mobile_money_provider_display || 'Not configured'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Phone Number</span>
                <p className="text-gray-900 font-mono">{bankingData?.mobile_money_number || 'Not configured'}</p>
              </div>
            </div>
          </div>

          {/* Quick Summary */}
          {formattedInfo && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Quick Summary</h4>
              <p className="text-sm text-gray-600">
                <strong>Account:</strong> {formattedInfo.fullAccountInfo}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Branch:</strong> {formattedInfo.branchInfo}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Mobile Money:</strong> {formattedInfo.mobileMoneyInfo}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Status:</strong> 
                <span className={`ml-1 ${formattedInfo.isComplete ? 'text-green-600' : 'text-yellow-600'}`}>
                  {formattedInfo.isComplete ? 'Complete' : 'Incomplete'}
                </span>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EmployeeBankingDetails;
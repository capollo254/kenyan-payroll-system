// src/api/employees.js

import api from './auth';

/**
 * A helper function to get the authentication headers.
 * This ensures that every request to a protected endpoint includes the user's token.
 * @returns {object} The headers object with the Authorization token.
 */
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error("No authentication token found. Please log in.");
  }
  return {
    headers: {
      Authorization: `Token ${token}`,
    },
  };
};

/**
 * Fetches a list of all employees from the backend.
 * This is typically an admin-only endpoint.
 * @returns {Promise<Array>} A list of employee objects.
 */
export const getEmployees = async () => {
  try {
    // First, try to get the count of total employees
    const response = await api.get('employees/employees/?page_size=100', getAuthHeaders());
    
    // Handle paginated response - return just the results array
    if (response.data && typeof response.data === 'object' && 'results' in response.data) {
      let allEmployees = response.data.results;
      
      // If there are more pages, fetch them all
      if (response.data.next) {
        let nextUrl = response.data.next;
        while (nextUrl) {
          const nextResponse = await api.get(nextUrl.replace(api.defaults.baseURL, ''), getAuthHeaders());
          allEmployees = [...allEmployees, ...nextResponse.data.results];
          nextUrl = nextResponse.data.next;
        }
      }
      
      return allEmployees;
    }
    // Fallback for non-paginated response
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error fetching employees:', error);
    throw error;
  }
};

/**
 * Fetches the current user's employee profile.
 * @returns {Promise<object>} The current user's employee object.
 */
export const getMyProfile = async () => {
  try {
    const response = await api.get('employees/employees/me/', getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching my profile:', error);
    throw error;
  }
};

/**
 * Fetches a single employee's details by their ID.
 * @param {number} employeeId - The ID of the employee to fetch.
 * @returns {Promise<object>} The employee object.
 */
export const getEmployee = async (employeeId) => {
  try {
    const response = await api.get(`employees/employees/${employeeId}/`, getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error(`Error fetching employee with ID ${employeeId}:`, error);
    throw error;
  }
};

/**
 * Creates a new employee by sending a POST request to the backend.
 * @param {object} employeeData - The data for the new employee.
 * @returns {Promise<object>} The newly created employee object.
 */
export const createEmployee = async (employeeData) => {
  try {
    const response = await api.post('employees/employees/', employeeData, getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error('Error creating new employee:', error);
    throw error;
  }
};

/**
 * Updates an existing employee by their ID.
 * @param {number} employeeId - The ID of the employee to update.
 * @param {object} employeeData - The updated data for the employee.
 * @returns {Promise<object>} The updated employee object.
 */
export const updateEmployee = async (employeeId, employeeData) => {
  try {
    const response = await api.put(`employees/employees/${employeeId}/`, employeeData, getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error(`Error updating employee with ID ${employeeId}:`, error);
    throw error;
  }
};

/**
 * Deletes an employee by their ID.
 * @param {number} employeeId - The ID of the employee to delete.
 * @returns {Promise<void>}
 */
export const deleteEmployee = async (employeeId) => {
  try {
    await api.delete(`employees/employees/${employeeId}/`, getAuthHeaders());
  } catch (error) {
    console.error(`Error deleting employee with ID ${employeeId}:`, error);
    throw error;
  }
};

// ========== BANKING INFORMATION ENDPOINTS ==========

/**
 * Fetches the current user's banking details.
 * @returns {Promise<object>} The current user's banking information.
 */
export const getMyBankingDetails = async () => {
  try {
    const response = await api.get('employees/employees/banking_details/', getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching my banking details:', error);
    throw error;
  }
};

/**
 * Fetches banking details for a specific employee by ID (admin only).
 * @param {number} employeeId - The ID of the employee.
 * @returns {Promise<object>} The employee's banking information.
 */
export const getBankingDetailsByEmployeeId = async (employeeId) => {
  try {
    const response = await api.get(`employees/employees/${employeeId}/banking_details_by_id/`, getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error(`Error fetching banking details for employee ID ${employeeId}:`, error);
    throw error;
  }
};

/**
 * Updates the current user's banking details.
 * @param {object} bankingData - The banking data to update.
 * @param {string} [bankingData.bank_name] - Full bank name.
 * @param {string} [bankingData.bank_code] - Central Bank assigned bank code.
 * @param {string} [bankingData.bank_branch] - Bank branch name.
 * @param {string} [bankingData.bank_branch_code] - Specific branch code.
 * @param {string} [bankingData.bank_account_number] - Bank account number.
 * @param {string} [bankingData.account_type] - Type of account (savings, current, fixed).
 * @param {string} [bankingData.account_holder_name] - Account holder name.
 * @param {string} [bankingData.mobile_money_provider] - Mobile money provider.
 * @param {string} [bankingData.mobile_money_number] - Mobile money phone number.
 * @returns {Promise<object>} The updated banking information.
 */
export const updateMyBankingDetails = async (bankingData) => {
  try {
    const response = await api.put('employees/employees/update_banking_details/', bankingData, getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error('Error updating banking details:', error);
    throw error;
  }
};

/**
 * Partially updates the current user's banking details.
 * @param {object} bankingData - The banking data to update (partial).
 * @returns {Promise<object>} The updated banking information.
 */
export const patchMyBankingDetails = async (bankingData) => {
  try {
    const response = await api.patch('employees/employees/update_banking_details/', bankingData, getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error('Error partially updating banking details:', error);
    throw error;
  }
};

/**
 * Fetches employees with incomplete banking information (admin only).
 * @returns {Promise<object>} Object containing count and list of employees with incomplete banking.
 */
export const getEmployeesWithIncompleteBanking = async () => {
  try {
    const response = await api.get('employees/employees/employees_with_incomplete_banking/', getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching employees with incomplete banking:', error);
    throw error;
  }
};

// ========== BANKING UTILITY FUNCTIONS ==========

/**
 * Validates banking information completeness.
 * @param {object} bankingData - The banking data to validate.
 * @returns {object} Validation result with isComplete flag and missing fields.
 */
export const validateBankingInfo = (bankingData) => {
  const requiredFields = [
    'bank_name',
    'bank_code', 
    'bank_branch',
    'bank_branch_code',
    'bank_account_number',
    'account_type'
  ];
  
  const missingFields = requiredFields.filter(field => 
    !bankingData[field] || bankingData[field].toString().trim() === ''
  );
  
  return {
    isComplete: missingFields.length === 0,
    missingFields: missingFields,
    completionPercentage: Math.round(((requiredFields.length - missingFields.length) / requiredFields.length) * 100)
  };
};

/**
 * Formats banking information for display.
 * @param {object} bankingData - The banking data to format.
 * @returns {object} Formatted banking information.
 */
export const formatBankingInfo = (bankingData) => {
  if (!bankingData) return null;
  
  return {
    displayName: `${bankingData.bank_name || 'Unknown Bank'}`,
    fullAccountInfo: `${bankingData.bank_name || 'N/A'} - ${bankingData.bank_account_number || 'No Account'}`,
    branchInfo: `${bankingData.bank_branch || 'N/A'} (${bankingData.bank_branch_code || 'N/A'})`,
    accountTypeDisplay: bankingData.account_type_display || 'Not specified',
    mobileMoneyInfo: bankingData.mobile_money_provider_display && bankingData.mobile_money_number 
      ? `${bankingData.mobile_money_provider_display}: ${bankingData.mobile_money_number}`
      : 'Not configured',
    isComplete: bankingData.has_complete_banking_info || false
  };
};

/**
 * Gets available bank account types for dropdowns.
 * @returns {Array} Array of account type options.
 */
export const getAccountTypes = () => [
  { value: 'savings', label: 'Savings Account' },
  { value: 'current', label: 'Current Account' },
  { value: 'fixed', label: 'Fixed Deposit Account' }
];

/**
 * Gets available mobile money providers for dropdowns.
 * @returns {Array} Array of mobile money provider options.
 */
export const getMobileMoneyProviders = () => [
  { value: 'mpesa', label: 'M-Pesa (Safaricom)' },
  { value: 'airtel', label: 'Airtel Money' },
  { value: 'tkash', label: 'T-Kash (Telkom)' },
  { value: 'equitel', label: 'Equitel' }
];

/**
 * Gets common Kenyan banks for dropdowns.
 * @returns {Array} Array of bank options with codes.
 */
export const getKenyanBanks = () => [
  { name: 'KCB Bank Kenya Limited', code: '01' },
  { name: 'Standard Chartered Bank Kenya Limited', code: '02' },
  { name: 'Barclays Bank of Kenya Limited', code: '03' },
  { name: 'Bank of Baroda (Kenya) Limited', code: '05' },
  { name: 'Kenya Commercial Bank Limited', code: '01' },
  { name: 'Citibank N.A Kenya', code: '16' },
  { name: 'Habib Bank A.G Zurich', code: '17' },
  { name: 'Middle East Bank Kenya Limited', code: '18' },
  { name: 'Bank of Africa Kenya Limited', code: '19' },
  { name: 'Prime Bank Limited', code: '10' },
  { name: 'Co-operative Bank of Kenya Limited', code: '11' },
  { name: 'National Bank of Kenya Limited', code: '12' },
  { name: 'Oriental Commercial Bank Limited', code: '14' },
  { name: 'Chase Bank Kenya Limited', code: '30' },
  { name: 'Stanbic Bank Kenya Limited', code: '31' },
  { name: 'Consolidated Bank of Kenya Limited', code: '23' },
  { name: 'Credit Bank Limited', code: '25' },
  { name: 'Equity Bank Kenya Limited', code: '68' },
  { name: 'Family Bank Limited', code: '70' },
  { name: 'Guaranty Trust Bank (Kenya) Limited', code: '53' },
  { name: 'Guardian Bank Limited', code: '55' },
  { name: 'Gulf African Bank Limited', code: '72' },
  { name: 'I&M Bank Limited', code: '57' },
  { name: 'Jamii Bora Bank Limited', code: '51' },
  { name: 'UBA Kenya Bank Limited', code: '76' },
  { name: 'Victoria Commercial Bank Limited', code: '54' },
  { name: 'Diamond Trust Bank Kenya Limited', code: '63' },
  { name: 'Ecobank Kenya Limited', code: '43' },
  { name: 'Sidian Bank Limited', code: '74' },
  { name: 'ABC Bank (Kenya) Limited', code: '35' },
  { name: 'Mayfair Bank Limited', code: '65' }
];
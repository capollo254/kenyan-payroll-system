// src/api/payroll.js

import api from './auth';

/**
 * Helper function to get the authentication headers.
 * Ensures every request includes the Authorization token.
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
 * Fetches the payslips for the logged-in user.
 * The backend should be configured to return only the payslips for the authenticated user.
 * @returns {Promise<Array>} A list of payslip objects.
 */
export const getPayslips = async () => {
  try {
    const response = await api.get('payroll/payslips/', getAuthHeaders());
    // Handle paginated response - return just the results array
    if (response.data && typeof response.data === 'object' && 'results' in response.data) {
      return response.data.results;
    }
    // Fallback for non-paginated response
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error fetching payslips:', error);
    throw error;
  }
};

/**
 * Initiates a new payroll run by sending a POST request to the backend.
 * This is an admin-only action.
 * @param {object} runData - The data for the new payroll run (e.g., dates).
 * @returns {Promise<object>} The response data for the new payroll run.
 */
export const createPayrollRun = async (runData) => {
  try {
    const response = await api.post('payroll/payroll-runs/', runData, getAuthHeaders());
    return response.data;
  } catch (error) {
    console.error('Error creating payroll run:', error);
    throw error;
  }
};

/**
 * Fetches a list of all payroll runs.
 * This is typically an admin-only endpoint.
 * @returns {Promise<Array>} A list of payroll run objects.
 */
export const getPayrollRuns = async () => {
  try {
    const response = await api.get('payroll/payroll-runs/?page_size=100', getAuthHeaders());
    
    // Handle paginated response
    if (response.data && typeof response.data === 'object' && 'results' in response.data) {
      let allRuns = response.data.results;
      
      // If there are more pages, fetch them all
      if (response.data.next) {
        let nextUrl = response.data.next;
        while (nextUrl) {
          const nextResponse = await api.get(nextUrl.replace(api.defaults.baseURL, ''), getAuthHeaders());
          allRuns = [...allRuns, ...nextResponse.data.results];
          nextUrl = nextResponse.data.next;
        }
      }
      
      return allRuns;
    }
    
    // Fallback for non-paginated response
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error fetching payroll runs:', error);
    throw error;
  }
};
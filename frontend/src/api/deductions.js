// api/deductions.js

// The base URL for your Django backend
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Get token from localStorage
const getToken = () => localStorage.getItem('token');

// Voluntary Deductions API
export const getVoluntaryDeductions = async (employeeId = null) => {
  try {
    const token = getToken();
    const url = employeeId 
      ? `${API_BASE_URL}/employees/voluntary-deductions/?employee=${employeeId}`
      : `${API_BASE_URL}/employees/voluntary-deductions/`;
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching voluntary deductions:', error);
    throw error;
  }
};

export const createVoluntaryDeduction = async (deductionData) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/employees/voluntary-deductions/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(deductionData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating voluntary deduction:', error);
    throw error;
  }
};

export const updateVoluntaryDeduction = async (deductionId, deductionData) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/employees/voluntary-deductions/${deductionId}/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(deductionData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating voluntary deduction:', error);
    throw error;
  }
};

export const deleteVoluntaryDeduction = async (deductionId) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/employees/voluntary-deductions/${deductionId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return true;
  } catch (error) {
    console.error('Error deleting voluntary deduction:', error);
    throw error;
  }
};

// Employee Benefits API
export const getEmployeeBenefits = async (employeeId = null) => {
  try {
    const token = getToken();
    const url = employeeId 
      ? `${API_BASE_URL}/employees/benefits/?employee=${employeeId}`
      : `${API_BASE_URL}/employees/benefits/`;
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching employee benefits:', error);
    throw error;
  }
};

export const createEmployeeBenefit = async (benefitData) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/employees/benefits/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(benefitData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating employee benefit:', error);
    throw error;
  }
};

export const updateEmployeeBenefit = async (benefitId, benefitData) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/employees/benefits/${benefitId}/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(benefitData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating employee benefit:', error);
    throw error;
  }
};

export const deleteEmployeeBenefit = async (benefitId) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/employees/benefits/${benefitId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return true;
  } catch (error) {
    console.error('Error deleting employee benefit:', error);
    throw error;
  }
};
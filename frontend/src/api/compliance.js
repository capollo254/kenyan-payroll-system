// api/compliance.js

// The base URL for your Django backend
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Get token from localStorage
const getToken = () => localStorage.getItem('token');

// Statutory Rates API
export const getStatutoryRates = async () => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/compliance/statutory-rates/current_rates/`, {
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
    console.error('Error fetching statutory rates:', error);
    throw error;
  }
};

export const updateStatutoryRates = async (ratesData) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/compliance/statutory-rates/bulk_update/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ratesData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating statutory rates:', error);
    throw error;
  }
};

export const getStatutoryRatesList = async () => {
  try {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/compliance/statutory-rates/`, {
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
    console.error('Error fetching statutory rates list:', error);
    throw error;
  }
};
// src/api/p9.js

const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

// Get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Token ${token}` : '',
  };
};

// Get my P9 reports (employee-specific)
export const getMyP9Reports = async () => {
  const response = await fetch(`${BASE_URL}/reports/p9/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch P9 reports');
  }

  return response.json();
};

// Get specific P9 report
export const getP9Report = async (id) => {
  const response = await fetch(`${BASE_URL}/reports/p9/${id}/`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch P9 report');
  }

  return response.json();
};

// Generate P9 for specific year
export const generateP9 = async (year) => {
  const response = await fetch(`${BASE_URL}/reports/p9/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      tax_year: year
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to generate P9 report');
  }

  return response.json();
};

// Download P9 as PDF
export const downloadP9PDF = async (p9Id) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${BASE_URL}/reports/p9/${p9Id}/download_pdf/`, {
    method: 'GET',
    headers: {
      'Authorization': token ? `Token ${token}` : '',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to download P9 PDF');
  }

  // Handle binary response
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `P9_Report_${p9Id}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Get payslip summary for P9 generation
export const getPayslipSummary = async (year) => {
  const response = await fetch(`${BASE_URL}/reports/p9/payslip_summary/?year=${year}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch payslip summary');
  }

  return response.json();
};
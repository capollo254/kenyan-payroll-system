// api/leaves.js
import { API_URL } from './auth';

// Get token from localStorage
const getToken = () => localStorage.getItem('token');

// Leave Types API
export const getLeaveTypes = async () => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-types/`, {
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
    console.error('Error fetching leave types:', error);
    throw error;
  }
};

// Leave Balances API
export const getLeaveBalances = async () => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-balances/`, {
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
    console.error('Error fetching leave balances:', error);
    throw error;
  }
};

export const getMyLeaveBalance = async () => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-requests/my_balance/`, {
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
    console.error('Error fetching my leave balance:', error);
    throw error;
  }
};

// Leave Requests API
export const getLeaveRequests = async (params = {}) => {
  try {
    const token = getToken();
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_URL}leaves/leave-requests/?${queryParams}`, {
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
    console.error('Error fetching leave requests:', error);
    throw error;
  }
};

export const createLeaveRequest = async (leaveData) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-requests/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(leaveData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || JSON.stringify(errorData) || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating leave request:', error);
    throw error;
  }
};

export const updateLeaveRequest = async (requestId, leaveData) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-requests/${requestId}/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(leaveData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating leave request:', error);
    throw error;
  }
};

export const deleteLeaveRequest = async (requestId) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-requests/${requestId}/`, {
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
    console.error('Error deleting leave request:', error);
    throw error;
  }
};

// Admin Leave Management API
export const getPendingLeaveRequests = async () => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-requests/pending_requests/`, {
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
    console.error('Error fetching pending leave requests:', error);
    throw error;
  }
};

export const approveLeaveRequest = async (requestId) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-requests/${requestId}/approve/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error approving leave request:', error);
    throw error;
  }
};

export const rejectLeaveRequest = async (requestId, rejectionReason) => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-requests/${requestId}/reject/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ rejection_reason: rejectionReason }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error rejecting leave request:', error);
    throw error;
  }
};

export const getLeaveDashboardStats = async () => {
  try {
    const token = getToken();
    const response = await fetch(`${API_URL}leaves/leave-requests/dashboard_stats/`, {
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
    console.error('Error fetching leave dashboard stats:', error);
    throw error;
  }
};
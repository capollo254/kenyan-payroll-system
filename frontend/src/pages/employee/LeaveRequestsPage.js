// src/pages/employee/LeaveRequestsPage.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import InputField from '../../components/common/InputField';
import Button from '../../components/common/Button';
import { 
  getLeaveTypes, 
  getLeaveRequests, 
  createLeaveRequest, 
  getMyLeaveBalance 
} from '../../api/leaves';

const LeaveRequestsPage = () => {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [leaveBalances, setLeaveBalances] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    leave_type: '',
    start_date: '',
    end_date: '',
    reason: '',
    days: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  // Load data from API
  useEffect(() => {
    loadLeaveData();
  }, []);

  const loadLeaveData = async () => {
    try {
      setLoading(true);
      
      const [typesResponse, requestsResponse, balancesResponse] = await Promise.all([
        getLeaveTypes(),
        getLeaveRequests(),
        getMyLeaveBalance()
      ]);

      setLeaveTypes(typesResponse.results || typesResponse);
      setLeaveRequests(requestsResponse.results || requestsResponse);
      setLeaveBalances(balancesResponse.results || balancesResponse);
      setError(null);
    } catch (err) {
      console.error('Failed to load leave data:', err);
      setError('Failed to load leave data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateDays = (start, end) => {
    if (!start || !end) return 0;
    const startDate = new Date(start);
    const endDate = new Date(end);
    const diffTime = Math.abs(endDate - startDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; // Include both start and end days
    return diffDays;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const newFormData = { ...formData, [name]: value };
    
    // Auto-calculate days when dates change
    if (name === 'start_date' || name === 'end_date') {
      newFormData.days = calculateDays(
        name === 'start_date' ? value : formData.start_date,
        name === 'end_date' ? value : formData.end_date
      );
    }
    
    setFormData(newFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    // Validation
    if (!formData.days || formData.days <= 0) {
      setError('Please select valid start and end dates');
      setLoading(false);
      return;
    }

    try {
      await createLeaveRequest({
        leave_type: formData.leave_type,
        start_date: formData.start_date,
        end_date: formData.end_date,
        reason: formData.reason,
        days_requested: formData.days
      });

      setSuccess('Leave request submitted successfully!');
      setFormData({
        leave_type: '',
        start_date: '',
        end_date: '',
        reason: '',
        days: 0
      });
      setShowForm(false);
      
      // Reload leave requests to show the new one
      await loadLeaveData();
    } catch (err) {
      console.error('Failed to submit leave request:', err);
      setError('Failed to submit leave request: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getAvailableBalance = (leaveTypeId) => {
    const balance = leaveBalances.find(b => b.leave_type.id === leaveTypeId);
    return balance ? balance.available_days : 0;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'var(--success-color)';
      case 'rejected': return 'var(--danger-color)';
      case 'pending': return 'var(--warning-color)';
      default: return 'var(--secondary-color)';
    }
  };

  if (loading && leaveRequests.length === 0) {
    return (
      <div className="container page">
        <div style={{ textAlign: 'center', padding: '40px' }}>
          Loading leave data...
        </div>
      </div>
    );
  }

  return (
    <div className="container page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2>Leave Requests</h2>
        <Button 
          onClick={() => setShowForm(!showForm)}
          className="btn-primary"
        >
          {showForm ? 'Cancel' : 'New Leave Request'}
        </Button>
      </div>

      {success && <div className="alert alert-success">{success}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Leave Balance Summary */}
      {leaveBalances.length > 0 && (
        <div className="card" style={{ marginBottom: '30px' }}>
          <h3>Your Leave Balance</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
            {leaveBalances.map((balance) => (
              <div key={balance.id} style={{ 
                padding: '15px', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '8px',
                border: '1px solid #dee2e6'
              }}>
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  {balance.leave_type.name}
                </div>
                <div style={{ fontSize: '14px', color: '#666' }}>
                  Available: <strong>{balance.available_days}</strong> / {balance.allocated_days} days
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Leave Request Form */}
      {showForm && (
        <div className="card" style={{ marginBottom: '30px' }}>
          <h3>Submit New Leave Request</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label htmlFor="leave_type">Leave Type</label>
                <select
                  id="leave_type"
                  name="leave_type"
                  value={formData.leave_type}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select Leave Type</option>
                  {leaveTypes.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.name} ({getAvailableBalance(type.id)} days available)
                    </option>
                  ))}
                </select>
              </div>

              <InputField
                label="Start Date"
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleInputChange}
                required
              />

              <InputField
                label="End Date"
                type="date"
                name="end_date"
                value={formData.end_date}
                onChange={handleInputChange}
                required
              />

              <InputField
                label="Total Days"
                type="number"
                name="days"
                value={formData.days}
                readOnly
                style={{ backgroundColor: '#f8f9fa' }}
              />
            </div>

            <div className="form-group" style={{ marginTop: '20px' }}>
              <label htmlFor="reason">Reason for Leave</label>
              <textarea
                id="reason"
                name="reason"
                value={formData.reason}
                onChange={handleInputChange}
                rows="3"
                style={{ width: '100%', padding: '10px', border: '1px solid var(--border-color)', borderRadius: '5px' }}
                placeholder="Please provide a brief reason for your leave request..."
                required
              />
            </div>

            <div style={{ marginTop: '20px' }}>
              <Button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'Submitting...' : 'Submit Request'}
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Leave Requests History */}
      <div className="card">
        <h3>Leave Request History</h3>
        {leaveRequests.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
              <thead>
                <tr style={{ backgroundColor: 'var(--light-color)' }}>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Type</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Start Date</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>End Date</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Days</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Applied Date</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Reason</th>
                </tr>
              </thead>
              <tbody>
                {leaveRequests.map((request) => (
                  <tr key={request.id}>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                      {request.leave_type_name}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                      {formatDate(request.start_date)}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                      {formatDate(request.end_date)}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                      {request.days}
                    </td>
                    <td style={{ 
                      padding: '12px', 
                      border: '1px solid var(--border-color)',
                      color: getStatusColor(request.status),
                      fontWeight: 'bold'
                    }}>
                      {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                      {formatDate(request.applied_date)}
                    </td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                      {request.reason}
                      {request.rejection_reason && (
                        <div style={{ 
                          marginTop: '5px', 
                          padding: '5px', 
                          backgroundColor: '#f8d7da', 
                          borderRadius: '3px',
                          fontSize: '12px',
                          color: '#721c24'
                        }}>
                          <strong>Rejection Reason:</strong> {request.rejection_reason}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No leave requests found.</p>
        )}
      </div>
    </div>
  );
};

export default LeaveRequestsPage;
import React, { useState, useEffect } from 'react';
import {
  getLeaveRequests,
  approveLeaveRequest,
  rejectLeaveRequest,
  getLeaveDashboardStats
} from '../../api/leaves';
import './LeaveManagement.css';

const LeaveManagement = () => {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [dashboardStats, setDashboardStats] = useState({});
  const [rejectionModal, setRejectionModal] = useState({
    show: false,
    requestId: null,
    reason: ''
  });

  const statusColors = {
    pending: 'status-pending',
    approved: 'status-approved',
    rejected: 'status-rejected'
  };

  useEffect(() => {
    loadLeaveRequests();
    loadDashboardStats();
  }, []);

  useEffect(() => {
    filterRequests();
  }, [filter, leaveRequests]);

  const loadLeaveRequests = async () => {
    try {
      setLoading(true);
      const response = await getLeaveRequests();
      setLeaveRequests(response.results || response);
      setError('');
    } catch (err) {
      setError('Failed to load leave requests: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardStats = async () => {
    try {
      const stats = await getLeaveDashboardStats();
      setDashboardStats(stats);
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
    }
  };

  const filterRequests = () => {
    let filtered = [...leaveRequests];
    
    if (filter !== 'all') {
      filtered = filtered.filter(request => request.status === filter);
    }

    setFilteredRequests(filtered);
  };

  const handleApprove = async (requestId) => {
    try {
      await approveLeaveRequest(requestId);
      await loadLeaveRequests();
      await loadDashboardStats();
      setError('');
    } catch (err) {
      setError('Failed to approve leave request: ' + err.message);
    }
  };

  const handleReject = async () => {
    try {
      await rejectLeaveRequest(rejectionModal.requestId, rejectionModal.reason);
      await loadLeaveRequests();
      await loadDashboardStats();
      setRejectionModal({ show: false, requestId: null, reason: '' });
      setError('');
    } catch (err) {
      setError('Failed to reject leave request: ' + err.message);
    }
  };

  const showRejectionModal = (requestId) => {
    setRejectionModal({ show: true, requestId, reason: '' });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const calculateDuration = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return diffDays;
  };

  if (loading) {
    return (
      <div className="leave-management">
        <div className="loading">Loading leave requests...</div>
      </div>
    );
  }

  return (
    <div className="leave-management">
      <div className="leave-header">
        <h2>Leave Management</h2>
      </div>

      {/* Dashboard Stats */}
      {dashboardStats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Requests</h3>
            <div className="stat-number">{dashboardStats.total_requests || 0}</div>
          </div>
          <div className="stat-card pending">
            <h3>Pending</h3>
            <div className="stat-number">{dashboardStats.pending_requests || 0}</div>
          </div>
          <div className="stat-card approved">
            <h3>Approved</h3>
            <div className="stat-number">{dashboardStats.approved_requests || 0}</div>
          </div>
          <div className="stat-card rejected">
            <h3>Rejected</h3>
            <div className="stat-number">{dashboardStats.rejected_requests || 0}</div>
          </div>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {/* Filter Controls */}
      <div className="filter-controls">
        <label>Filter by status:</label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All Requests</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {/* Leave Requests Table */}
      <div className="leave-table-container">
        <table className="leave-table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Leave Type</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Duration</th>
              <th>Status</th>
              <th>Reason</th>
              <th>Applied Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredRequests.length > 0 ? (
              filteredRequests.map((request) => (
                <tr key={request.id}>
                  <td>
                    <div className="employee-info">
                      <strong>{request.employee_name}</strong>
                      <br />
                      <small>{request.employee_email}</small>
                    </div>
                  </td>
                  <td>{request.leave_type_name}</td>
                  <td>{formatDate(request.start_date)}</td>
                  <td>{formatDate(request.end_date)}</td>
                  <td>{calculateDuration(request.start_date, request.end_date)} days</td>
                  <td>
                    <span className={`status-badge ${statusColors[request.status]}`}>
                      {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                    </span>
                  </td>
                  <td className="reason-cell">
                    <div className="reason-text" title={request.reason}>
                      {request.reason}
                    </div>
                    {request.rejection_reason && (
                      <div className="rejection-reason">
                        <strong>Rejection Reason:</strong> {request.rejection_reason}
                      </div>
                    )}
                  </td>
                  <td>{formatDate(request.applied_date)}</td>
                  <td>
                    {request.status === 'pending' ? (
                      <div className="action-buttons">
                        <button
                          className="btn-approve"
                          onClick={() => handleApprove(request.id)}
                        >
                          Approve
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() => showRejectionModal(request.id)}
                        >
                          Reject
                        </button>
                      </div>
                    ) : (
                      <span className="action-disabled">
                        {request.status === 'approved' ? 'Approved' : 'Rejected'}
                      </span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="9" className="no-data">
                  No leave requests found for the selected filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Rejection Modal */}
      {rejectionModal.show && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Reject Leave Request</h3>
            </div>
            <div className="modal-body">
              <label>Reason for rejection:</label>
              <textarea
                value={rejectionModal.reason}
                onChange={(e) => setRejectionModal({
                  ...rejectionModal,
                  reason: e.target.value
                })}
                placeholder="Please provide a reason for rejecting this leave request..."
                rows="4"
              />
            </div>
            <div className="modal-footer">
              <button
                className="btn-cancel"
                onClick={() => setRejectionModal({ show: false, requestId: null, reason: '' })}
              >
                Cancel
              </button>
              <button
                className="btn-confirm-reject"
                onClick={handleReject}
                disabled={!rejectionModal.reason.trim()}
              >
                Reject Request
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeaveManagement;
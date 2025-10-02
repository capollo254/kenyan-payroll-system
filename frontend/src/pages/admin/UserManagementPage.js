// src/pages/admin/UserManagementPage.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getEmployees } from '../../api/employees';
import Button from '../../components/common/Button';
import InputField from '../../components/common/InputField';

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    firstName: '',
    lastName: '',
    role: 'employee',
    isActive: true,
    department: '',
    position: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const employeesData = await getEmployees();
      // Transform employees data to user format
      const usersData = employeesData.map(emp => ({
        id: emp.id,
        email: emp.user.email,
        firstName: emp.user.first_name,
        lastName: emp.user.last_name,
        fullName: emp.full_name,
        isActive: emp.user.is_active,
        isStaff: emp.user.is_staff,
        role: emp.user.is_staff ? 'admin' : 'employee',
        department: emp.job_information?.department || 'N/A',
        position: emp.job_information?.job_title || 'N/A',
        dateJoined: emp.user.date_joined
      }));
      setUsers(usersData);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      if (err.response && err.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        navigate('/login');
      }
      setError('Failed to load users.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingUser) {
        // Update existing user
        alert('User update functionality would be implemented here');
        // Update users list locally for demo
        setUsers(users.map(user => 
          user.id === editingUser.id 
            ? { ...user, ...formData, fullName: `${formData.firstName} ${formData.lastName}` }
            : user
        ));
      } else {
        // Create new user
        alert('User creation functionality would be implemented here');
        // Add new user to list locally for demo
        const newUser = {
          id: users.length + 1,
          ...formData,
          fullName: `${formData.firstName} ${formData.lastName}`,
          dateJoined: new Date().toISOString().split('T')[0]
        };
        setUsers([...users, newUser]);
      }
      
      setShowForm(false);
      setEditingUser(null);
      setFormData({
        email: '',
        firstName: '',
        lastName: '',
        role: 'employee',
        isActive: true,
        department: '',
        position: ''
      });
    } catch (err) {
      console.error('Failed to save user:', err);
      setError('Failed to save user. Please try again.');
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      role: user.role,
      isActive: user.isActive,
      department: user.department,
      position: user.position
    });
    setShowForm(true);
  };

  const handleDeactivate = async (userId) => {
    if (window.confirm('Are you sure you want to deactivate this user?')) {
      try {
        alert('User deactivation functionality would be implemented here');
        // Update locally for demo
        setUsers(users.map(user => 
          user.id === userId ? { ...user, isActive: false } : user
        ));
      } catch (err) {
        console.error('Failed to deactivate user:', err);
        setError('Failed to deactivate user.');
      }
    }
  };

  const handleActivate = async (userId) => {
    try {
      alert('User activation functionality would be implemented here');
      // Update locally for demo
      setUsers(users.map(user => 
        user.id === userId ? { ...user, isActive: true } : user
      ));
    } catch (err) {
      console.error('Failed to activate user:', err);
      setError('Failed to activate user.');
    }
  };

  if (loading) {
    return <div className="container page">Loading users...</div>;
  }

  return (
    <div className="container page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2>User Management</h2>
        <Button 
          onClick={() => {
            setEditingUser(null);
            setFormData({
              email: '',
              firstName: '',
              lastName: '',
              role: 'employee',
              isActive: true,
              department: '',
              position: ''
            });
            setShowForm(!showForm);
          }}
          className="btn-primary"
        >
          {showForm ? 'Cancel' : 'Add New User'}
        </Button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* User Form */}
      {showForm && (
        <div className="card" style={{ marginBottom: '30px' }}>
          <h3>{editingUser ? 'Edit User' : 'Create New User'}</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              <InputField
                label="Email Address"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
              <InputField
                label="First Name"
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                required
              />
              <InputField
                label="Last Name"
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleInputChange}
                required
              />
              <div className="form-group">
                <label htmlFor="role">Role</label>
                <select
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  required
                >
                  <option value="employee">Employee</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>
              <InputField
                label="Department"
                type="text"
                name="department"
                value={formData.department}
                onChange={handleInputChange}
              />
              <InputField
                label="Position"
                type="text"
                name="position"
                value={formData.position}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group" style={{ marginTop: '20px' }}>
              <label>
                <input
                  type="checkbox"
                  name="isActive"
                  checked={formData.isActive}
                  onChange={handleInputChange}
                  style={{ marginRight: '8px' }}
                />
                Active User
              </label>
            </div>

            <div style={{ marginTop: '20px' }}>
              <Button type="submit" className="btn-primary">
                {editingUser ? 'Update User' : 'Create User'}
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Users List */}
      <div className="card">
        <h3>System Users</h3>
        {users.length > 0 ? (
          <div style={{ overflowX: 'auto', marginTop: '20px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: 'var(--light-color)' }}>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Name</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Email</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Role</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Department</th>
                  <th style={{ padding: '12px', textAlign: 'left', border: '1px solid var(--border-color)' }}>Position</th>
                  <th style={{ padding: '12px', textAlign: 'center', border: '1px solid var(--border-color)' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'center', border: '1px solid var(--border-color)' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{user.fullName}</td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{user.email}</td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        backgroundColor: user.role === 'admin' ? 'var(--warning-color)' : 'var(--info-color)',
                        color: 'white'
                      }}>
                        {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                      </span>
                    </td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{user.department}</td>
                    <td style={{ padding: '12px', border: '1px solid var(--border-color)' }}>{user.position}</td>
                    <td style={{ padding: '12px', textAlign: 'center', border: '1px solid var(--border-color)' }}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        backgroundColor: user.isActive ? 'var(--success-color)' : 'var(--danger-color)',
                        color: 'white'
                      }}>
                        {user.isActive ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', border: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', gap: '5px', justifyContent: 'center' }}>
                        <button 
                          className="btn btn-sm btn-secondary"
                          onClick={() => handleEdit(user)}
                        >
                          Edit
                        </button>
                        {user.isActive ? (
                          <button 
                            className="btn btn-sm btn-danger"
                            onClick={() => handleDeactivate(user.id)}
                          >
                            Deactivate
                          </button>
                        ) : (
                          <button 
                            className="btn btn-sm btn-success"
                            onClick={() => handleActivate(user.id)}
                          >
                            Activate
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No users found.</p>
        )}
      </div>
    </div>
  );
};

export default UserManagementPage;
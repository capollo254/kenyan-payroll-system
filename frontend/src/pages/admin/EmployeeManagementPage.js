// src/pages/admin/EmployeeManagementPage.js

import React, { useEffect, useState } from 'react';
import { getEmployees, deleteEmployee } from '../../api/employees';
import { useNavigate } from 'react-router-dom';
import AddEmployeeForm from '../../components/forms/AddEmployeeForm';
import Button from '../../components/common/Button';

const EmployeeManagementPage = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAdding, setIsAdding] = useState(false);
  const navigate = useNavigate();

  const fetchEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEmployees();
      setEmployees(data);
    } catch (err) {
      console.error('Failed to fetch employees:', err);
      if (err.response && err.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        navigate('/login');
      }
      setError('Could not load employee data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleDelete = async (employeeId) => {
    if (window.confirm("Are you sure you want to delete this employee?")) {
      try {
        await deleteEmployee(employeeId);
        fetchEmployees(); // Refresh the list
      } catch (err) {
        console.error('Failed to delete employee:', err);
        setError('Failed to delete employee.');
      }
    }
  };

  const handleEmployeeAdded = () => {
    setIsAdding(false);
    fetchEmployees(); // Refresh the list after adding a new employee
  };

  if (loading) {
    return <div className="container page">Loading employees...</div>;
  }

  if (error) {
    return <div className="container page error">{error}</div>;
  }

  return (
    <div className="container page">
      <h2>Employee Management</h2>
      <div style={{ marginBottom: '20px' }}>
        {!isAdding && <Button className="btn-success" onClick={() => setIsAdding(true)}>Add New Employee</Button>}
      </div>

      {isAdding ? (
        <AddEmployeeForm onEmployeeAdded={handleEmployeeAdded} onCancel={() => setIsAdding(false)} />
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map(employee => (
                <tr key={employee.id}>
                  <td>{employee.id}</td>
                  <td>{employee.full_name}</td>
                  <td>{employee.user.email}</td>
                  <td>{employee.is_admin ? 'Admin' : 'Employee'}</td>
                  <td>
                    <button onClick={() => handleDelete(employee.id)} style={{ color: 'red', border: 'none', background: 'none', cursor: 'pointer' }}>
                      Delete
                    </button>
                    {/* An "Edit" button could be added here */}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default EmployeeManagementPage;
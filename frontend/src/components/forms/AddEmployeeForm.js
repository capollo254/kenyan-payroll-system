// src/components/forms/AddEmployeeForm.js

import React, { useState } from 'react';
import InputField from '../common/InputField';
import Button from '../common/Button';
import { createEmployee } from '../../api/employees';

/**
 * A form component for adding a new employee.
 * @param {object} props - Component props.
 * @param {function} props.onEmployeeAdded - Callback function to run on successful form submission.
 * @param {function} props.onCancel - Callback function to cancel the form.
 */
const AddEmployeeForm = ({ onEmployeeAdded, onCancel }) => {
  const [formData, setFormData] = useState({
    user: {
      email: '',
      password: '',
    },
    first_name: '',
    last_name: '',
    id_number: '',
    kra_pin: '',
    nssf_number: '',
    nhif_number: '',
    phone_number: '',
    basic_salary: '',
    is_admin: false, // Default to false
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (name === 'email' || name === 'password') {
      setFormData(prev => ({
        ...prev,
        user: { ...prev.user, [name]: value }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createEmployee(formData);
      onEmployeeAdded();
    } catch (err) {
      console.error('Error adding employee:', err);
      setError('Failed to add employee. Please check the data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2>Add New Employee</h2>
      <InputField label="Email" type="email" name="email" value={formData.user.email} onChange={handleChange} required />
      <InputField label="Password" type="password" name="password" value={formData.user.password} onChange={handleChange} required />
      <InputField label="First Name" name="first_name" value={formData.first_name} onChange={handleChange} required />
      <InputField label="Last Name" name="last_name" value={formData.last_name} onChange={handleChange} required />
      <InputField label="ID Number" name="id_number" value={formData.id_number} onChange={handleChange} required />
      <InputField label="KRA PIN" name="kra_pin" value={formData.kra_pin} onChange={handleChange} required />
      <InputField label="NSSF Number" name="nssf_number" value={formData.nssf_number} onChange={handleChange} required />
      <InputField label="NHIF Number" name="nhif_number" value={formData.nhif_number} onChange={handleChange} required />
      <InputField label="Phone Number" name="phone_number" value={formData.phone_number} onChange={handleChange} required />
      <InputField label="Basic Salary" type="number" name="basic_salary" value={formData.basic_salary} onChange={handleChange} required />
      <div className="form-group">
        <label>
          <input
            type="checkbox"
            name="is_admin"
            checked={formData.is_admin}
            onChange={handleChange}
          />
          Is Admin
        </label>
      </div>
      {error && <p className="error">{error}</p>}
      <div style={{ display: 'flex', gap: '10px' }}>
        <Button className="btn-success" type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add Employee'}
        </Button>
        <Button type="button" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  );
};

export default AddEmployeeForm;
// src/pages/auth/LoginPage.js

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../../api/auth';
import InputField from '../../components/common/InputField';
import Button from '../../components/common/Button';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await login(email, password);
      
      if (response && response.token && response.role) {
        localStorage.setItem('token', response.token);
        localStorage.setItem('role', response.role);
        
        // Navigate based on the role returned by the backend
        if (response.role === 'admin') {
          navigate('/admin/dashboard');
        } else {
          navigate('/employee/dashboard');
        }
      } else {
        setError('Login failed. Please try again.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Invalid email or password. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container page" style={{ marginTop: '50px', maxWidth: '400px' }}>
      <h2>Log In</h2>
      <form onSubmit={handleLogin}>
        <InputField 
          label="Email" 
          type="email" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} 
          required 
        />
        <InputField 
          label="Password" 
          type="password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          required 
        />
        <Button type="submit" disabled={loading}>{loading ? 'Logging in...' : 'Login'}</Button>
        {error && <p className="error" style={{ marginTop: '10px' }}>{error}</p>}
      </form>
    </div>
  );
};

export default LoginPage;
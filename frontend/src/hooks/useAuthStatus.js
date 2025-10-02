// src/hooks/useAuthStatus.js

import { useState, useEffect } from 'react';
import { isAuthenticated, checkTokenValidity } from '../api/auth';

/**
 * A custom hook to check the user's authentication and role status.
 * This hook is useful for rendering different content or redirecting users
 * based on their logged-in status and privileges.
 * @returns {object} An object containing authentication status and user info.
 */
const useAuthStatus = () => {
  const [isAuth, setIsAuth] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokenValid, setTokenValid] = useState(true);
  
  useEffect(() => {
    const checkAuthStatus = async () => {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const role = localStorage.getItem('role');
      
      if (!token) {
        setIsAuth(false);
        setIsAdmin(false);
        setUser(null);
        setTokenValid(false);
        setLoading(false);
        return;
      }
      
      // Check basic token existence
      setIsAuth(true);
      setIsAdmin(role === 'admin');
      
      // Verify token validity with backend
      try {
        const validity = await checkTokenValidity();
        
        if (validity.valid) {
          setTokenValid(true);
          setUser(validity.user);
          setIsAuth(true);
          setIsAdmin(role === 'admin');
        } else {
          // Token is invalid
          setTokenValid(false);
          setIsAuth(false);
          setIsAdmin(false);
          setUser(null);
          
          // Clear invalid token
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          localStorage.removeItem('loginTime');
        }
      } catch (error) {
        console.error('Token validation failed:', error);
        // On network error, assume token is still valid but mark as uncertain
        setTokenValid(true);
        setUser(null);
      }
      
      setLoading(false);
    };
    
    checkAuthStatus();
    
    // Set up periodic token validation (every 2 minutes)
    const interval = setInterval(checkAuthStatus, 120000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Function to manually refresh auth status
  const refreshAuthStatus = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setIsAuth(false);
      setIsAdmin(false);
      setUser(null);
      setTokenValid(false);
      return;
    }
    
    try {
      const validity = await checkTokenValidity();
      
      if (validity.valid) {
        setTokenValid(true);
        setUser(validity.user);
        setIsAuth(true);
        setIsAdmin(localStorage.getItem('role') === 'admin');
      } else {
        setTokenValid(false);
        setIsAuth(false);
        setIsAdmin(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth refresh failed:', error);
    }
  };
  
  return { 
    isAuthenticated: isAuth && tokenValid, 
    isAdmin, 
    user,
    loading,
    tokenValid,
    refreshAuthStatus
  };
};

export default useAuthStatus;
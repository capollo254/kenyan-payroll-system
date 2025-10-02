// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import LoginPage from './pages/auth/LoginPage';
import MyPayslipsPage from './pages/employee/MyPayslipsPage';
import MyP9ReportsPage from './pages/employee/MyP9ReportsPage';
import EmployeeManagementPage from './pages/admin/EmployeeManagementPage';
import PayrollRunPage from './pages/admin/PayrollRunPage';
import MyProfilePage from './pages/employee/MyProfilePage';
import EmployeeDashboard from './pages/employee/EmployeeDashboard';
import LeaveRequestsPage from './pages/employee/LeaveRequestsPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import PayrollPage from './pages/admin/PayrollPage';
import AdminPayslipsPage from './pages/admin/AdminPayslipsPage';
import ReportsPage from './pages/admin/ReportsPage';
import UserManagementPage from './pages/admin/UserManagementPage';
import SettingsPage from './pages/admin/SettingsPage';
import LeaveManagement from './pages/admin/LeaveManagement';
import PayslipDetailView from './components/payslip/PayslipDetailView';
import { logout } from './api/auth';

// A simple layout for pages that are not the login screen
const AppLayout = () => {
  const userRole = localStorage.getItem('role');

  return (
    <div>
      <nav className="navbar">
        <h2>Payroll System</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            {userRole === 'employee' && (
              <>
                <a href="/employee/dashboard">Dashboard</a>
                <a href="/employee/payslips">Payslips</a>
                <a href="/employee/p9-reports">P9 Tax Forms</a>
                <a href="/employee/profile">Profile</a>
                <a href="/employee/leave-requests">Leave Requests</a>
              </>
            )}
            {userRole === 'admin' && (
              <>
                <a href="/admin/dashboard">Dashboard</a>
                <a href="/admin/employees">Employees</a>
                <a href="/admin/payroll">Payroll</a>
                <a href="/admin/payslips">My Payslips</a>
                <a href="/admin/leave-management">Leave Management</a>
                <a href="/admin/reports">Reports</a>
                <a href="/admin/user-management">User Management</a>
                <a href="/admin/settings">Settings</a>
              </>
            )}
          </div>
          
          {/* Simple User Display */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '8px 15px',
            background: userRole === 'admin' ? 'rgba(220, 53, 69, 0.1)' : 'rgba(40, 167, 69, 0.1)',
            borderRadius: '20px',
            border: `1px solid ${userRole === 'admin' ? 'rgba(220, 53, 69, 0.3)' : 'rgba(40, 167, 69, 0.3)'}`,
            fontSize: '14px'
          }}>
            <div style={{
              width: '30px',
              height: '30px',
              borderRadius: '50%',
              background: userRole === 'admin' ? '#dc3545' : '#28a745',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              fontWeight: 'bold'
            }}>
              {userRole === 'admin' ? 'A' : 'U'}
            </div>
            <div>
              <div style={{ fontWeight: 'bold', fontSize: '13px' }}>
                {userRole === 'admin' ? 'Administrator' : 'User'}
              </div>
              <div style={{ fontSize: '11px', opacity: '0.8' }}>
                {userRole === 'admin' ? '🔑 Administrator' : '👤 Employee'}
              </div>
            </div>
          </div>

          <button 
            onClick={logout}
            style={{
              background: 'none',
              border: 'none',
              color: 'inherit',
              textDecoration: 'underline',
              cursor: 'pointer',
              fontSize: 'inherit',
              fontFamily: 'inherit'
            }}
          >
            Logout
          </button>
        </div>
      </nav>
      <div className="container">
        <Outlet />
      </div>
    </div>
  );
};

// Simple check for authentication and role-based access
const isAuthenticated = () => !!localStorage.getItem('token');
const getUserRole = () => localStorage.getItem('role');

// A route that requires authentication
const PrivateRoute = ({ children, roleRequired }) => {
  const auth = isAuthenticated();
  const userRole = getUserRole();
  
  if (!auth) {
    return <Navigate to="/login" replace />;
  }

  if (roleRequired && userRole !== roleRequired) {
    return <Navigate to={userRole === 'admin' ? '/admin/dashboard' : '/employee/dashboard'} replace />;
  }

  return children;
};

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/*
          CORRECTED: The root route is moved outside the AppLayout.
          This ensures the redirection logic runs on the initial load.
        */}
        <Route 
          path="/" 
          element={<Navigate to={isAuthenticated() ? `/${getUserRole()}/dashboard` : '/login'} replace />} 
        />
        
        <Route element={<AppLayout />}>
          {/* Employee Protected Routes */}
          <Route
            path="/employee/dashboard"
            element={
              <PrivateRoute roleRequired="employee">
                <EmployeeDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/employee/profile"
            element={
              <PrivateRoute roleRequired="employee">
                <MyProfilePage />
              </PrivateRoute>
            }
          />
          <Route
            path="/employee/payslips"
            element={
              <PrivateRoute roleRequired="employee">
                <MyPayslipsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/employee/p9-reports"
            element={
              <PrivateRoute roleRequired="employee">
                <MyP9ReportsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/employee/leave-requests"
            element={
              <PrivateRoute roleRequired="employee">
                <LeaveRequestsPage />
              </PrivateRoute>
            }
          />
          
          {/* Payslip Detail Route - accessible by both employees and admins */}
          <Route
            path="/payslip/:id"
            element={
              <PrivateRoute>
                <PayslipDetailView />
              </PrivateRoute>
            }
          />
          
          {/* Admin Protected Routes */}
          <Route
            path="/admin/dashboard"
            element={
              <PrivateRoute roleRequired="admin">
                <AdminDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/employees"
            element={
              <PrivateRoute roleRequired="admin">
                <EmployeeManagementPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/payroll"
            element={
              <PrivateRoute roleRequired="admin">
                <PayrollPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/payslips"
            element={
              <PrivateRoute roleRequired="admin">
                <AdminPayslipsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/leave-management"
            element={
              <PrivateRoute roleRequired="admin">
                <LeaveManagement />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/reports"
            element={
              <PrivateRoute roleRequired="admin">
                <ReportsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/user-management"
            element={
              <PrivateRoute roleRequired="admin">
                <UserManagementPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/settings"
            element={
              <PrivateRoute roleRequired="admin">
                <SettingsPage />
              </PrivateRoute>
            }
          />
          {/* Legacy route for backward compatibility */}
          <Route
            path="/admin/payroll-run"
            element={
              <PrivateRoute roleRequired="admin">
                <PayrollRunPage />
              </PrivateRoute>
            }
          />
          
          {/* Fallback for unknown routes */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
// src/components/common/AdminProfileWidget.js

import React from 'react';

const AdminProfileWidget = ({ profile, showFullDetails = false }) => {
  if (!profile) return null;

  const fullName = profile.full_name || `${profile.first_name} ${profile.last_name}`.trim() || 'Administrator';
  const initials = fullName.split(' ').map(n => n.charAt(0)).join('').toUpperCase();

  if (!showFullDetails) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '10px 15px',
        background: 'rgba(220, 53, 69, 0.1)',
        borderRadius: '8px',
        border: '1px solid rgba(220, 53, 69, 0.3)',
        fontSize: '14px'
      }}>
        <div style={{
          width: '35px',
          height: '35px',
          borderRadius: '50%',
          background: '#dc3545',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '14px',
          fontWeight: 'bold'
        }}>
          {initials}
        </div>
        <div>
          <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{fullName}</div>
          <div style={{ fontSize: '12px', opacity: '0.8' }}>🔑 Administrator</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      padding: '20px',
      borderRadius: '10px',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <div style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'rgba(255,255,255,0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          fontWeight: 'bold'
        }}>
          {initials}
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ margin: '0', fontSize: '22px' }}>{fullName}</h3>
          <p style={{ margin: '5px 0', fontSize: '14px', opacity: '0.9' }}>
            <strong>Admin Account:</strong> {profile.email}
          </p>
          <p style={{ margin: '0', fontSize: '12px', opacity: '0.8' }}>
            ID: {profile.employee_id || 'N/A'} | Department: {profile.department || 'Administration'}
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{
            background: 'rgba(255,255,255,0.2)',
            padding: '8px 15px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 'bold',
            marginBottom: '8px'
          }}>
            🔑 ADMINISTRATOR
          </div>
          <div style={{ fontSize: '11px', opacity: '0.8' }}>
            {new Date().toLocaleDateString()} {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
      
      {/* Security Notice */}
      <div style={{
        marginTop: '15px',
        padding: '10px',
        background: 'rgba(255,255,255,0.1)',
        borderRadius: '5px',
        fontSize: '12px'
      }}>
        <strong>⚠️ Security Notice:</strong> You are logged in with administrative privileges. 
        Please ensure you are using your authorized admin account and log out when finished.
      </div>
    </div>
  );
};

export default AdminProfileWidget;
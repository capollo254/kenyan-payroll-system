// src/pages/employee/MyProfilePage.js

import React, { useState, useEffect } from 'react';
import { getMyProfile } from '../../api/employees';

const MyProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const profileData = await getMyProfile();
      setProfile(profileData);
      setError(null);
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError('Failed to load profile information');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container page">
        <h2>My Profile</h2>
        <p>Loading profile...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container page">
        <h2>My Profile</h2>
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchProfile}>Retry</button>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container page">
        <h2>My Profile</h2>
        <p>No profile information found.</p>
      </div>
    );
  }

  return (
    <div className="container page">
      <h2>My Profile</h2>
      
      {/* Personal Information */}
      <div className="profile-section">
        <h3>Personal Information</h3>
        <div className="profile-grid">
          <div className="profile-item">
            <label>Full Name:</label>
            <span>{profile.full_name}</span>
          </div>
          <div className="profile-item">
            <label>Email:</label>
            <span>{profile.email}</span>
          </div>
          <div className="profile-item">
            <label>First Name:</label>
            <span>{profile.first_name}</span>
          </div>
          <div className="profile-item">
            <label>Last Name:</label>
            <span>{profile.last_name}</span>
          </div>
        </div>
      </div>

      {/* Job Information */}
      {profile.job_information && (
        <div className="profile-section">
          <h3>Job Information</h3>
          <div className="profile-grid">
            <div className="profile-item">
              <label>Employee ID:</label>
              <span>{profile.job_information.company_employee_id}</span>
            </div>
            <div className="profile-item">
              <label>Position:</label>
              <span>{profile.job_information.position}</span>
            </div>
            <div className="profile-item">
              <label>Department:</label>
              <span>{profile.job_information.department}</span>
            </div>
            <div className="profile-item">
              <label>Date of Joining:</label>
              <span>{new Date(profile.job_information.date_of_joining).toLocaleDateString()}</span>
            </div>
            <div className="profile-item">
              <label>KRA PIN:</label>
              <span>{profile.job_information.kra_pin}</span>
            </div>
            <div className="profile-item">
              <label>NSSF Number:</label>
              <span>{profile.job_information.nssf_number || 'Not provided'}</span>
            </div>
            <div className="profile-item">
              <label>NHIF Number:</label>
              <span>{profile.job_information.nhif_number || 'Not provided'}</span>
            </div>
          </div>
        </div>
      )}

      {/* Salary Information */}
      <div className="profile-section">
        <h3>Salary Information</h3>
        <div className="profile-grid">
          <div className="profile-item">
            <label>Gross Salary:</label>
            <span>KES {parseFloat(profile.gross_salary).toLocaleString()}</span>
          </div>
          <div className="profile-item">
            <label>Bank Account:</label>
            <span>{profile.bank_account_number || 'Not provided'}</span>
          </div>
          <div className="profile-item">
            <label>HELB Deduction:</label>
            <span>KES {profile.helb_monthly_deduction ? parseFloat(profile.helb_monthly_deduction).toLocaleString() : '0'}</span>
          </div>
        </div>
      </div>

      {/* Voluntary Deductions */}
      {profile.voluntary_deductions && profile.voluntary_deductions.length > 0 && (
        <div className="profile-section">
          <h3>Voluntary Deductions</h3>
          <div className="deductions-list">
            {profile.voluntary_deductions.map((deduction, index) => (
              <div key={index} className="deduction-item">
                <span className="deduction-type">{deduction.deduction_type}</span>
                <span className="deduction-amount">KES {parseFloat(deduction.monthly_amount).toLocaleString()}</span>
                <span className={`deduction-status ${deduction.is_active ? 'active' : 'inactive'}`}>
                  {deduction.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .profile-section {
          margin-bottom: 2rem;
          padding: 1.5rem;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .profile-section h3 {
          margin-top: 0;
          color: #333;
          border-bottom: 2px solid #007bff;
          padding-bottom: 0.5rem;
        }
        
        .profile-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
          margin-top: 1rem;
        }
        
        .profile-item {
          display: flex;
          flex-direction: column;
        }
        
        .profile-item label {
          font-weight: bold;
          color: #555;
          margin-bottom: 0.25rem;
        }
        
        .profile-item span {
          color: #333;
          padding: 0.5rem;
          background: #f8f9fa;
          border-radius: 4px;
        }
        
        .deductions-list {
          margin-top: 1rem;
        }
        
        .deduction-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          background: #f8f9fa;
          border-radius: 4px;
          border-left: 4px solid #007bff;
        }
        
        .deduction-status.active {
          color: #28a745;
          font-weight: bold;
        }
        
        .deduction-status.inactive {
          color: #dc3545;
          font-weight: bold;
        }
        
        .error-message {
          text-align: center;
          padding: 2rem;
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          border-radius: 4px;
          color: #721c24;
        }
        
        .error-message button {
          margin-top: 1rem;
          padding: 0.5rem 1rem;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .error-message button:hover {
          background: #0056b3;
        }
      `}</style>
    </div>
  );
};

export default MyProfilePage;
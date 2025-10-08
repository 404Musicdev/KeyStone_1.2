import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const StudentDashboard = () => {
  const { user, logout } = useAuth();
  
  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  const handleEmergencyReset = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/';
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#0f172a', 
      color: 'white', 
      padding: '40px' 
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '36px', marginBottom: '20px', color: '#3b82f6' }}>
          🎓 Student Dashboard
        </h1>
        
        <div style={{ 
          backgroundColor: '#1e293b', 
          padding: '30px', 
          borderRadius: '10px',
          marginBottom: '20px'
        }}>
          <h2 style={{ color: '#10b981', marginBottom: '15px' }}>
            ✅ SUCCESS: Student Login Working!
          </h2>
          
          <p style={{ marginBottom: '10px' }}>
            <strong>Welcome:</strong> {user?.first_name} {user?.last_name}
          </p>
          <p style={{ marginBottom: '10px' }}>
            <strong>Username:</strong> {user?.username}
          </p>
          <p style={{ marginBottom: '20px' }}>
            <strong>Role:</strong> {user?.role}
          </p>
          
          <div style={{ 
            backgroundColor: '#065f46', 
            padding: '15px', 
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#10b981', marginBottom: '10px' }}>Dashboard Features Available:</h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li>📚 View Learn to Code Assignments</li>
              <li>✏️ Complete Coding Exercises</li>
              <li>📊 Check Grades</li>
              <li>💬 Message Teachers</li>
            </ul>
          </div>
          
          <button 
            onClick={handleLogout}
            style={{ 
              backgroundColor: '#dc2626', 
              color: 'white', 
              padding: '12px 24px',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              marginRight: '10px'
            }}
          >
            🚪 Logout
          </button>
          
          <button 
            onClick={handleEmergencyReset}
            style={{ 
              backgroundColor: '#7c2d12', 
              color: 'white', 
              padding: '8px 16px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            🔥 Emergency Reset
          </button>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
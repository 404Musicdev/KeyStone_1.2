import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const StudentDashboard = () => {
  const { user, isAuthenticated, loading, logout } = useAuth();
  
  // Handle loading state
  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#0f172a', 
        color: 'white', 
        padding: '40px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2>Loading...</h2>
          <p>Please wait while we load your dashboard.</p>
        </div>
      </div>
    );
  }

  // Check if user is a student (students have teacher_id, teachers don't)
  const isStudent = user && user.teacher_id;
  
  console.log('StudentDashboard auth check:', { 
    isAuthenticated, 
    user, 
    isStudent,
    hasTeacherId: !!user?.teacher_id
  });

  // Handle not authenticated or not a student
  if (!isAuthenticated || !user || !isStudent) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#0f172a', 
        color: 'white', 
        padding: '40px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ color: '#ef4444', marginBottom: '20px' }}>Access Denied</h2>
          <p style={{ marginBottom: '20px' }}>You need to be logged in as a student to access this page.</p>
          <p style={{ fontSize: '12px', color: '#666', marginBottom: '20px' }}>
            Debug: isAuth={String(isAuthenticated)}, hasTeacherId={String(!!user?.teacher_id)}
          </p>
          <button 
            onClick={() => window.location.href = '/'}
            style={{ 
              backgroundColor: '#3b82f6', 
              color: 'white', 
              padding: '12px 24px',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

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
            <strong>Welcome:</strong> {user.first_name} {user.last_name}
          </p>
          <p style={{ marginBottom: '10px' }}>
            <strong>Username:</strong> {user.username}
          </p>
          <p style={{ marginBottom: '20px' }}>
            <strong>Role:</strong> Student
          </p>
          
          <div style={{ 
            backgroundColor: '#065f46', 
            padding: '15px', 
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#10b981', marginBottom: '15px' }}>Quick Actions:</h3>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button
                onClick={() => window.location.href = '/student/assignments'}
                style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  padding: '10px 16px',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                📚 View Assignments
              </button>
              <button
                onClick={() => window.location.href = '/student/grades'}
                style={{
                  backgroundColor: '#10b981',
                  color: 'white',
                  padding: '10px 16px',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                📊 My Grades
              </button>
              <button
                onClick={() => window.location.href = '/student/messages'}
                style={{
                  backgroundColor: '#8b5cf6',
                  color: 'white',
                  padding: '10px 16px',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                💬 Messages
              </button>
            </div>
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
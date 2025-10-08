import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

// Simple Assignments View
const StudentAssignments = ({ user }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/student/assignments`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAssignments(data);
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ color: 'white', padding: '20px' }}>Loading assignments...</div>;
  }

  return (
    <div style={{ color: 'white', padding: '20px' }}>
      <h2 style={{ marginBottom: '20px' }}>My Assignments</h2>
      {assignments.length === 0 ? (
        <p>No assignments available yet. Check back later!</p>
      ) : (
        <div style={{ display: 'grid', gap: '15px' }}>
          {assignments.map((assignment) => (
            <div key={assignment.id} style={{
              backgroundColor: '#1e293b',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #374151'
            }}>
              <h3 style={{ color: '#3b82f6', marginBottom: '10px' }}>
                {assignment.assignment.title}
              </h3>
              <p><strong>Subject:</strong> {assignment.assignment.subject}</p>
              <p><strong>Grade:</strong> {assignment.assignment.grade_level}</p>
              <p><strong>Status:</strong> {assignment.completed ? '✅ Completed' : '⏳ Pending'}</p>
              {!assignment.completed && (
                <button
                  onClick={() => window.location.href = `/student/assignment/${assignment.id}`}
                  style={{
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    padding: '8px 16px',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    marginTop: '10px'
                  }}
                >
                  Start Assignment
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Dashboard Home Component
const StudentHome = ({ user, navigate }) => (
  <div>
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
          onClick={() => navigate('/student/assignments')}
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
          onClick={() => navigate('/student/grades')}
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
          onClick={() => navigate('/student/messages')}
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
  </div>
);

const StudentDashboard = () => {
  const { user, isAuthenticated, loading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
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
      padding: '20px' 
    }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '28px', color: '#3b82f6', margin: 0 }}>
            🎓 Student Dashboard
          </h1>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              onClick={handleLogout}
              style={{ 
                backgroundColor: '#dc2626', 
                color: 'white', 
                padding: '8px 16px',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🚪 Logout
            </button>
            <button 
              onClick={handleEmergencyReset}
              style={{ 
                backgroundColor: '#7c2d12', 
                color: 'white', 
                padding: '6px 12px',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              🔥 Reset
            </button>
          </div>
        </div>

        {/* Navigation */}
        <div style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
            <button
              onClick={() => navigate('/student')}
              style={{
                backgroundColor: location.pathname === '/student' ? '#3b82f6' : '#374151',
                color: 'white',
                padding: '10px 20px',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              🏠 Dashboard
            </button>
            <button
              onClick={() => navigate('/student/assignments')}
              style={{
                backgroundColor: location.pathname === '/student/assignments' ? '#3b82f6' : '#374151',
                color: 'white',
                padding: '10px 20px',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              📚 Assignments
            </button>
            <button
              onClick={() => navigate('/student/grades')}
              style={{
                backgroundColor: location.pathname === '/student/grades' ? '#3b82f6' : '#374151',
                color: 'white',
                padding: '10px 20px',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              📊 Grades
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div style={{ 
          backgroundColor: '#1e293b', 
          padding: '30px', 
          borderRadius: '10px',
          minHeight: '400px'
        }}>
          <Routes>
            <Route index element={<StudentHome user={user} navigate={navigate} />} />
            <Route path="assignments" element={<StudentAssignments user={user} />} />
            <Route path="grades" element={
              <div style={{ color: 'white' }}>
                <h2>My Grades</h2>
                <p>Grades will be displayed here once you complete assignments.</p>
              </div>
            } />
            <Route path="messages" element={
              <div style={{ color: 'white' }}>
                <h2>Messages</h2>
                <p>Messages from your teacher will appear here.</p>
              </div>
            } />
            <Route path="*" element={<StudentHome user={user} navigate={navigate} />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
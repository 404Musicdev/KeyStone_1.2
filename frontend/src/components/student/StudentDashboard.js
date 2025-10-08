import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

// Modern Assignments View
const StudentAssignments = ({ user }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/student/assignments`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAssignments(data);
      } else {
        console.error('Failed to fetch assignments:', response.status);
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '200px',
        flexDirection: 'column'
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '4px solid #e5e7eb',
          borderTop: '4px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '15px'
        }}></div>
        <p style={{ color: '#94a3b8', fontSize: '16px' }}>Loading your awesome assignments...</p>
      </div>
    );
  }

  const getSubjectEmoji = (subject) => {
    const emojis = {
      'Learn to Code': '💻',
      'Math': '🧮',
      'Science': '🔬',
      'Reading': '📖',
      'History': '🏛️',
      'English': '📝'
    };
    return emojis[subject] || '📚';
  };

  const getSubjectColor = (subject) => {
    const colors = {
      'Learn to Code': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      'Math': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      'Science': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      'Reading': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      'History': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      'English': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
    };
    return colors[subject] || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  };

  return (
    <div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '30px'
      }}>
        <h2 style={{ 
          fontSize: '28px', 
          margin: 0,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          color: 'transparent',
          fontWeight: 'bold'
        }}>
          📚 My Assignments
        </h2>
      </div>

      {assignments.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '20px',
          color: 'white'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>🎯</div>
          <h3 style={{ fontSize: '24px', marginBottom: '10px' }}>No assignments yet!</h3>
          <p style={{ fontSize: '16px', opacity: 0.9 }}>
            Check back soon for exciting Learn to Code challenges!
          </p>
        </div>
      ) : (
        <div style={{ 
          display: 'grid', 
          gap: '20px',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))'
        }}>
          {assignments.map((assignment, index) => (
            <div key={assignment.id} style={{
              background: getSubjectColor(assignment.assignment.subject),
              padding: '0',
              borderRadius: '16px',
              overflow: 'hidden',
              boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
              transform: 'translateY(0)',
              transition: 'all 0.3s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)';
              e.currentTarget.style.boxShadow = '0 15px 35px rgba(0,0,0,0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 10px 25px rgba(0,0,0,0.1)';
            }}>
              <div style={{ padding: '24px', color: 'white' }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                  <div style={{
                    fontSize: '32px',
                    marginRight: '12px',
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    padding: '8px',
                    borderRadius: '12px'
                  }}>
                    {getSubjectEmoji(assignment.assignment.subject)}
                  </div>
                  <div>
                    <h3 style={{ 
                      fontSize: '18px', 
                      margin: 0, 
                      fontWeight: 'bold',
                      textShadow: '0 2px 4px rgba(0,0,0,0.2)'
                    }}>
                      {assignment.assignment.title}
                    </h3>
                    <p style={{ 
                      fontSize: '14px', 
                      margin: 0, 
                      opacity: 0.9,
                      fontWeight: '500'
                    }}>
                      {assignment.assignment.subject} • {assignment.assignment.grade_level}
                    </p>
                  </div>
                </div>

                <div style={{ 
                  backgroundColor: 'rgba(255,255,255,0.15)', 
                  padding: '12px', 
                  borderRadius: '10px',
                  marginBottom: '20px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '14px', fontWeight: '600' }}>
                      {assignment.completed ? '✅ Completed!' : '⏳ Ready to Start'}
                    </span>
                    {assignment.score !== undefined && assignment.score !== null && (
                      <span style={{ 
                        fontSize: '16px', 
                        fontWeight: 'bold',
                        backgroundColor: 'rgba(255,255,255,0.2)',
                        padding: '4px 8px',
                        borderRadius: '6px'
                      }}>
                        {Math.round(assignment.score)}%
                      </span>
                    )}
                  </div>
                </div>

                {!assignment.completed && (
                  <button
                    onClick={() => window.location.href = `/student/assignment/${assignment.id}`}
                    style={{
                      backgroundColor: 'rgba(255,255,255,0.9)',
                      color: '#1f2937',
                      padding: '12px 24px',
                      border: 'none',
                      borderRadius: '10px',
                      cursor: 'pointer',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      width: '100%',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = 'white';
                      e.target.style.transform = 'scale(1.02)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = 'rgba(255,255,255,0.9)';
                      e.target.style.transform = 'scale(1)';
                    }}
                  >
                    🚀 Start Assignment
                  </button>
                )}
              </div>
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
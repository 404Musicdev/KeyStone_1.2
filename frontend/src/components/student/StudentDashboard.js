import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

// Modern Assignments View
const StudentAssignments = ({ user }) => {
  const navigate = useNavigate();
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
          {assignments.map((assignment) => (
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
                    onClick={() => {
                      console.log('Assignment object:', assignment);
                      console.log('Student Assignment ID:', assignment.student_assignment_id);
                      const url = `/student/assignment/${assignment.student_assignment_id}`;
                      console.log('Navigating to URL:', url);
                      navigate(url);
                    }}
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

// Modern Dashboard Home Component
const StudentHome = ({ user, navigate }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGradeData();
  }, []);

  const fetchGradeData = async () => {
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
      }
    } catch (error) {
      console.error('Error fetching grade data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateOverallGrade = () => {
    const completedAssignments = assignments.filter(a => a.completed && a.score !== undefined && a.score !== null);
    if (completedAssignments.length === 0) return null;
    
    const totalScore = completedAssignments.reduce((sum, a) => sum + a.score, 0);
    return Math.round(totalScore / completedAssignments.length);
  };

  const getGradeColor = (grade) => {
    if (grade >= 90) return 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    if (grade >= 80) return 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)';
    if (grade >= 70) return 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
    return 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
  };

  const getGradeEmoji = (grade) => {
    if (grade >= 90) return '🌟';
    if (grade >= 80) return '😊';
    if (grade >= 70) return '👍';
    return '💪';
  };

  const getGradeMessage = (grade) => {
    if (grade >= 90) return 'Outstanding work!';
    if (grade >= 80) return 'Great job!';
    if (grade >= 70) return 'Good progress!';
    return 'Keep trying!';
  };

  const overallGrade = calculateOverallGrade();
  const completedCount = assignments.filter(a => a.completed).length;
  const totalCount = assignments.length;
  const pendingCount = totalCount - completedCount;

  return (
    <div>
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '30px',
      borderRadius: '20px',
      marginBottom: '30px',
      color: 'white',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '48px', marginBottom: '15px' }}>🎉</div>
      <h2 style={{ 
        fontSize: '32px', 
        margin: '0 0 10px 0',
        fontWeight: 'bold'
      }}>
        Welcome back, {user.first_name}!
      </h2>
      <p style={{ fontSize: '18px', opacity: 0.9, margin: 0 }}>
        Ready to learn something amazing today?
      </p>
    </div>

    {/* Overall Grade - Featured Section */}
    {overallGrade !== null && (
      <div style={{
        background: getGradeColor(overallGrade),
        padding: '30px',
        borderRadius: '20px',
        marginBottom: '25px',
        color: 'white',
        textAlign: 'center',
        boxShadow: '0 15px 35px rgba(0,0,0,0.2)'
      }}>
        <div style={{ fontSize: '64px', marginBottom: '15px' }}>
          {getGradeEmoji(overallGrade)}
        </div>
        <h2 style={{ 
          fontSize: '28px', 
          margin: '0 0 10px 0',
          fontWeight: 'bold'
        }}>
          Overall Grade: {overallGrade}%
        </h2>
        <p style={{ fontSize: '18px', opacity: 0.9, margin: '0 0 10px 0' }}>
          {getGradeMessage(overallGrade)}
        </p>
        <p style={{ fontSize: '14px', opacity: 0.8, margin: 0 }}>
          Based on {completedCount} completed assignment{completedCount !== 1 ? 's' : ''}
        </p>
      </div>
    )}

    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '20px',
      marginBottom: '30px'
    }}>
      {/* Assignment Stats */}
      <div style={{
        background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        padding: '24px',
        borderRadius: '16px',
        color: 'white',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '36px', marginBottom: '10px' }}>📋</div>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>Total Assignments</h3>
        <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>{totalCount}</p>
      </div>

      <div style={{
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        padding: '24px',
        borderRadius: '16px',
        color: 'white',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '36px', marginBottom: '10px' }}>✅</div>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>Completed</h3>
        <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>{completedCount}</p>
      </div>

      <div style={{
        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        padding: '24px',
        borderRadius: '16px',
        color: 'white',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '36px', marginBottom: '10px' }}>⏳</div>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>Pending</h3>
        <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>{pendingCount}</p>
      </div>
    </div>
    
    <div style={{
      backgroundColor: 'rgba(255,255,255,0.05)',
      padding: '25px',
      borderRadius: '16px',
      border: '1px solid rgba(255,255,255,0.1)'
    }}>
      <h3 style={{ 
        fontSize: '24px', 
        marginBottom: '20px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        color: 'transparent',
        fontWeight: 'bold'
      }}>
        🚀 Quick Actions
      </h3>
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '15px' 
      }}>
        <button
          onClick={() => navigate('/student/assignments')}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '16px 20px',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            textAlign: 'center',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
        >
          📚 View Assignments
        </button>
        <button
          onClick={() => navigate('/student/grades')}
          style={{
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            color: 'white',
            padding: '16px 20px',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            textAlign: 'center',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
        >
          📊 My Grades
        </button>
        <button
          onClick={() => navigate('/student/rewards')}
          style={{
            background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            color: 'white',
            padding: '16px 20px',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            textAlign: 'center',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
        >
          🏆 Rewards Store
        </button>
        <button
          onClick={() => navigate('/student/messages')}
          style={{
            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            color: 'white',
            padding: '16px 20px',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            textAlign: 'center',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
        >
          💬 Messages
        </button>
      </div>
    </div>
    </div>
  );
};

// Detailed Grades View
const StudentGrades = ({ user }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGrades();
  }, []);

  const fetchGrades = async () => {
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
      }
    } catch (error) {
      console.error('Error fetching grades:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 80) return '#3b82f6';
    if (score >= 70) return '#f59e0b';
    return '#ef4444';
  };

  const getGradeLetter = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  const completedAssignments = assignments.filter(a => a.completed && a.score !== undefined && a.score !== null);
  const overallGrade = completedAssignments.length > 0 
    ? Math.round(completedAssignments.reduce((sum, a) => sum + a.score, 0) / completedAssignments.length)
    : null;

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '300px',
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
        <p style={{ color: '#94a3b8', fontSize: '16px' }}>Loading your grades...</p>
      </div>
    );
  }

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
          📊 My Grades Report
        </h2>
      </div>

      {/* Overall Grade Summary */}
      {overallGrade !== null && (
        <div style={{
          background: `linear-gradient(135deg, ${getGradeColor(overallGrade)} 0%, ${getGradeColor(overallGrade)}dd 100%)`,
          padding: '25px',
          borderRadius: '16px',
          marginBottom: '25px',
          color: 'white',
          textAlign: 'center'
        }}>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '5px' }}>
                {overallGrade}%
              </div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                Grade: {getGradeLetter(overallGrade)}
              </div>
            </div>
            <div style={{ textAlign: 'left' }}>
              <p style={{ margin: '5px 0', fontSize: '16px' }}>
                📋 Total Assignments: {assignments.length}
              </p>
              <p style={{ margin: '5px 0', fontSize: '16px' }}>
                ✅ Completed: {completedAssignments.length}
              </p>
              <p style={{ margin: '5px 0', fontSize: '16px' }}>
                ⏳ Pending: {assignments.length - completedAssignments.length}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Individual Assignment Grades */}
      {completedAssignments.length > 0 ? (
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ 
            fontSize: '20px', 
            marginBottom: '15px',
            color: '#e5e7eb'
          }}>
            Individual Assignment Grades
          </h3>
          <div style={{ display: 'grid', gap: '15px' }}>
            {completedAssignments.map((assignment, index) => (
              <div key={assignment.id} style={{
                background: 'rgba(255,255,255,0.05)',
                padding: '20px',
                borderRadius: '12px',
                border: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <h4 style={{ 
                    margin: '0 0 8px 0', 
                    fontSize: '18px',
                    color: '#e5e7eb'
                  }}>
                    {assignment.assignment.title}
                  </h4>
                  <p style={{ 
                    margin: '0 0 5px 0', 
                    fontSize: '14px', 
                    opacity: 0.8 
                  }}>
                    {assignment.assignment.subject} • {assignment.assignment.grade_level}
                  </p>
                  {assignment.submitted_at && (
                    <p style={{ 
                      margin: 0, 
                      fontSize: '12px', 
                      opacity: 0.6 
                    }}>
                      Submitted: {new Date(assignment.submitted_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <div style={{
                  textAlign: 'center',
                  padding: '15px 20px',
                  borderRadius: '10px',
                  backgroundColor: getGradeColor(assignment.score),
                  color: 'white',
                  minWidth: '80px'
                }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                    {Math.round(assignment.score)}%
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                    {getGradeLetter(assignment.score)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '20px',
          color: 'white'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>📚</div>
          <h3 style={{ fontSize: '24px', marginBottom: '10px' }}>No Grades Yet</h3>
          <p style={{ fontSize: '16px', opacity: 0.9 }}>
            Complete some assignments to see your grades here!
          </p>
        </div>
      )}
    </div>
  );
};

// Student Assignment View Component
const StudentAssignmentView = ({ user, navigate }) => {
  const { assignmentId } = useParams();
  const [assignment, setAssignment] = useState(null);
  const [answers, setAnswers] = useState({});
  const [codingAnswers, setCodingAnswers] = useState({});
  const [dragDropAnswer, setDragDropAnswer] = useState({});
  const [draggedItem, setDraggedItem] = useState(null);
  const [interactiveWordAnswers, setInteractiveWordAnswers] = useState({});
  const [spellingAnswers, setSpellingAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  // Rewards state
  const [rewards, setRewards] = useState([]);
  const [studentPoints, setStudentPoints] = useState(null);
  const [loadingRewards, setLoadingRewards] = useState(false);

  // Debug logging
  console.log('StudentAssignmentView - assignmentId from useParams:', assignmentId);
  console.log('StudentAssignmentView - all params:', useParams());

  useEffect(() => {
    if (assignmentId) {
      fetchAssignment();
    } else {
      console.error('No assignmentId found in URL params');
      navigate('/student/assignments');
    }
  }, [assignmentId]);

  const fetchAssignment = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/student/assignments/${assignmentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('=== ASSIGNMENT DATA ===', data);
        console.log('Has drag_drop_puzzle?', data.assignment?.drag_drop_puzzle);
        console.log('Questions length:', data.assignment?.questions?.length);
        setAssignment(data);
      } else {
        console.error('Failed to fetch assignment');
        navigate('/student/assignments');
      }
    } catch (error) {
      console.error('Error fetching assignment:', error);
      navigate('/student/assignments');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionIndex, answerIndex) => {
    setAnswers(prevAnswers => ({
      ...prevAnswers,
      [questionIndex]: answerIndex
    }));
  };

  const handleCodingAnswerChange = (exerciseIndex, code) => {
    setCodingAnswers(prevAnswers => ({
      ...prevAnswers,
      [exerciseIndex]: code
    }));
  };

  const handleDragStart = (e, itemId) => {
    setDraggedItem(itemId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, zoneId) => {
    e.preventDefault();
    if (draggedItem) {
      setDragDropAnswer(prev => ({
        ...prev,
        [zoneId]: draggedItem
      }));
      setDraggedItem(null);
    }
  };

  const handleRemoveFromZone = (zoneId) => {
    setDragDropAnswer(prev => {
      const updated = { ...prev };
      delete updated[zoneId];
      return updated;
    });
  };

  const handleWordClick = (activityIndex, word) => {
    if (!assignment.completed) {
      setInteractiveWordAnswers(prev => ({
        ...prev,
        [activityIndex]: word
      }));
    }
  };

  const speakText = (text) => {
    if (!('speechSynthesis' in window)) {
      alert('Text-to-Speech is not supported in your browser. Please try Chrome, Edge, or Safari.');
      return;
    }

    try {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      
      // Small delay to ensure cancel completes
      setTimeout(() => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8; // Slower rate for learning
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        utterance.lang = 'en-US'; // Set language explicitly
        
        // Add event listeners
        utterance.onstart = () => {
          console.log('Speech started');
          setIsSpeaking(true);
        };
        utterance.onend = () => {
          console.log('Speech ended');
          setIsSpeaking(false);
        };
        utterance.onerror = (event) => {
          console.error('Speech error:', event);
          setIsSpeaking(false);
          if (event.error === 'not-allowed') {
            alert('Please allow audio permissions in your browser settings.');
          } else if (event.error === 'synthesis-unavailable') {
            alert('Text-to-Speech is currently unavailable. Please try again.');
          }
        };
        
        window.speechSynthesis.speak(utterance);
      }, 100);
    } catch (error) {
      console.error('TTS Error:', error);
      setIsSpeaking(false);
      alert('Unable to play text-to-speech. Please check your browser settings.');
    }
  };

  const handleSpellingAnswer = (exerciseIndex, answer) => {
    if (!assignment.completed) {
      setSpellingAnswers(prev => ({
        ...prev,
        [exerciseIndex]: answer
      }));
    }
  };

  const handleSubmit = async () => {
    if (!assignment || assignment.completed) return;

    const totalQuestions = assignment.assignment.questions.length;
    const totalCodingExercises = assignment.assignment.coding_exercises?.length || 0;
    const hasDragDropPuzzle = assignment.assignment.drag_drop_puzzle;
    const hasLearnToRead = assignment.assignment.learn_to_read_content;
    const hasSpelling = assignment.assignment.spelling_exercises;
    
    // Check if all questions are answered
    if (totalQuestions > 0 && Object.keys(answers).length < totalQuestions) {
      alert(`Please answer all ${totalQuestions} questions before submitting.`);
      return;
    }

    // Check if all coding exercises are completed
    if (totalCodingExercises > 0 && Object.keys(codingAnswers).length < totalCodingExercises) {
      alert(`Please complete all ${totalCodingExercises} coding exercises before submitting.`);
      return;
    }

    // Check if drag-drop puzzle is completed
    if (hasDragDropPuzzle) {
      const totalZones = hasDragDropPuzzle.zones.length;
      const filledZones = Object.keys(dragDropAnswer).length;
      if (filledZones < totalZones) {
        alert(`Please complete the drag-and-drop puzzle by placing all items in their correct zones.`);
        return;
      }
    }

    // Check if Learn to Read activities are completed
    if (hasLearnToRead) {
      const totalActivities = hasLearnToRead.activities.length;
      const completedActivities = Object.keys(interactiveWordAnswers).length;
      if (completedActivities < totalActivities) {
        alert(`Please complete all ${totalActivities} word activities before submitting.`);
        return;
      }
    }

    // Check if Spelling exercises are completed
    if (hasSpelling) {
      const totalSpelling = hasSpelling.length;
      const completedSpelling = Object.keys(spellingAnswers).length;
      if (completedSpelling < totalSpelling) {
        alert(`Please complete all ${totalSpelling} spelling exercises before submitting.`);
        return;
      }
    }

    setSubmitting(true);
    
    try {
      // Convert answers to arrays
      const answersArray = [];
      for (let i = 0; i < totalQuestions; i++) {
        answersArray[i] = answers[i] !== undefined ? answers[i] : -1;
      }

      const codingAnswersArray = [];
      for (let i = 0; i < totalCodingExercises; i++) {
        codingAnswersArray[i] = codingAnswers[i] || '';
      }

      // Prepare Learn to Read answers
      const learnToReadAnswersArray = [];
      if (hasLearnToRead) {
        for (let i = 0; i < hasLearnToRead.activities.length; i++) {
          learnToReadAnswersArray[i] = interactiveWordAnswers[i] || '';
        }
      }

      // Prepare Spelling answers
      const spellingAnswersArray = [];
      if (hasSpelling) {
        for (let i = 0; i < hasSpelling.length; i++) {
          spellingAnswersArray[i] = spellingAnswers[i] || '';
        }
      }

      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/student/assignments/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          student_assignment_id: assignmentId,
          answers: answersArray.length > 0 ? answersArray : null,
          coding_answers: codingAnswersArray.length > 0 ? codingAnswersArray : null,
          drag_drop_answer: hasDragDropPuzzle ? dragDropAnswer : null,
          interactive_word_answers: learnToReadAnswersArray.length > 0 ? learnToReadAnswersArray : null,
          spelling_answers: spellingAnswersArray.length > 0 ? spellingAnswersArray : null
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Assignment submitted successfully! Score: ${result.score}%`);
        navigate('/student/assignments');
      } else {
        alert('Failed to submit assignment. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting assignment:', error);
      alert('Error submitting assignment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
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
        <p style={{ color: '#94a3b8', fontSize: '16px' }}>Loading assignment...</p>
      </div>
    );
  }

  if (!assignment) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>❌</div>
        <h2 style={{ fontSize: '24px', marginBottom: '15px', color: '#ef4444' }}>
          Assignment Not Found
        </h2>
        <button
          onClick={() => navigate('/student/assignments')}
          style={{
            background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Back to Assignments
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '25px',
        padding: '20px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '12px',
        color: 'white'
      }}>
        <div>
          <h1 style={{ fontSize: '24px', margin: '0 0 5px 0', fontWeight: 'bold' }}>
            {assignment.assignment.title}
          </h1>
          <p style={{ margin: 0, opacity: 0.9 }}>
            {assignment.assignment.subject} • {assignment.assignment.grade_level}
            {assignment.assignment.coding_level && ` • Level ${assignment.assignment.coding_level}`}
          </p>
        </div>
        <button
          onClick={() => navigate('/student/assignments')}
          style={{
            backgroundColor: 'rgba(255,255,255,0.2)',
            color: 'white',
            padding: '8px 16px',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          ← Back
        </button>
      </div>

      {/* Assignment Status */}
      {assignment.completed && (
        <div style={{
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          padding: '15px 20px',
          borderRadius: '10px',
          marginBottom: '20px',
          color: 'white',
          textAlign: 'center'
        }}>
          ✅ Assignment Completed! Score: {assignment.score ? Math.round(assignment.score) : 0}%
        </div>
      )}

      {/* Questions Section */}
      {assignment.assignment.questions && assignment.assignment.questions.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ 
            fontSize: '20px', 
            marginBottom: '20px',
            color: '#e5e7eb'
          }}>
            📝 Questions ({assignment.assignment.questions.length})
          </h2>
          
          {assignment.assignment.questions.map((question, index) => (
            <div key={index} style={{
              background: '#1e40af',
              padding: '25px',
              borderRadius: '12px',
              marginBottom: '20px',
              color: '#f8fafc'
            }}>
              <div style={{ display: 'flex', alignItems: 'start', gap: '15px' }}>
                <div style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '50%',
                  backgroundColor: assignment.completed ? '#10b981' : 'rgba(248, 250, 252, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}>
                  {index + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{ fontSize: '18px', marginBottom: '15px', fontWeight: '600' }}>
                    {question.question}
                  </h3>
                  <div style={{ display: 'grid', gap: '10px' }}>
                    {question.options.map((option, optionIndex) => (
                      <label key={optionIndex} style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '12px',
                        backgroundColor: 'rgba(248, 250, 252, 0.1)',
                        borderRadius: '8px',
                        cursor: assignment.completed ? 'default' : 'pointer',
                        border: answers[index] === optionIndex ? '2px solid #f8fafc' : '2px solid transparent'
                      }}>
                        <input
                          type="radio"
                          name={`question-${index}`}
                          value={optionIndex}
                          checked={answers[index] === optionIndex}
                          onChange={() => !assignment.completed && handleAnswerSelect(index, optionIndex)}
                          disabled={assignment.completed}
                          style={{ marginRight: '12px' }}
                        />
                        {option}
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Coding Exercises Section */}
      {assignment.assignment.coding_exercises && assignment.assignment.coding_exercises.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ 
            fontSize: '20px', 
            marginBottom: '20px',
            color: '#e5e7eb'
          }}>
            💻 Coding Exercises ({assignment.assignment.coding_exercises.length})
          </h2>
          
          {assignment.assignment.coding_exercises.map((exercise, index) => (
            <div key={index} style={{
              background: '#1e40af',
              padding: '25px',
              borderRadius: '12px',
              marginBottom: '20px',
              color: '#f8fafc'
            }}>
              <div style={{ display: 'flex', alignItems: 'start', gap: '15px' }}>
                <div style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '50%',
                  backgroundColor: assignment.completed ? '#10b981' : 'rgba(248, 250, 252, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}>
                  {index + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{ fontSize: '18px', marginBottom: '10px', fontWeight: '600' }}>
                    {exercise.prompt}
                  </h3>
                  <div style={{
                    backgroundColor: 'rgba(0,0,0,0.2)',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    marginBottom: '15px',
                    display: 'inline-block'
                  }}>
                    Language: {exercise.language.toUpperCase()}
                  </div>
                  
                  {exercise.starter_code && (
                    <div style={{ marginBottom: '15px' }}>
                      <p style={{ fontSize: '14px', marginBottom: '8px', opacity: 0.9 }}>Starter Code:</p>
                      <pre style={{
                        backgroundColor: 'rgba(0,0,0,0.3)',
                        padding: '15px',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontFamily: 'Monaco, "Lucida Console", monospace',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap'
                      }}>
                        {exercise.starter_code}
                      </pre>
                    </div>
                  )}
                  
                  <div>
                    <p style={{ fontSize: '14px', marginBottom: '8px', opacity: 0.9 }}>Your Code:</p>
                    <textarea
                      value={codingAnswers[index] || exercise.starter_code || ''}
                      onChange={(e) => !assignment.completed && handleCodingAnswerChange(index, e.target.value)}
                      disabled={assignment.completed}
                      placeholder={`Write your ${exercise.language} code here...`}
                      style={{
                        width: '100%',
                        height: '150px',
                        backgroundColor: 'rgba(0,0,0,0.3)',
                        color: '#f8fafc',
                        border: '1px solid rgba(248, 250, 252, 0.2)',
                        borderRadius: '8px',
                        padding: '15px',
                        fontSize: '14px',
                        fontFamily: 'Monaco, "Lucida Console", monospace',
                        resize: 'vertical'
                      }}
                    />
                  </div>

                  {assignment.completed && exercise.correct_answer && (
                    <div style={{ marginTop: '15px' }}>
                      <p style={{ fontSize: '14px', marginBottom: '8px', color: '#10b981' }}>Correct Answer:</p>
                      <pre style={{
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        padding: '15px',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontFamily: 'Monaco, "Lucida Console", monospace',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap'
                      }}>
                        {exercise.correct_answer}
                      </pre>
                      {exercise.explanation && (
                        <p style={{ 
                          fontSize: '14px', 
                          marginTop: '10px', 
                          fontStyle: 'italic',
                          opacity: 0.9
                        }}>
                          💡 {exercise.explanation}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Drag and Drop Puzzle Section */}
      {assignment.assignment.drag_drop_puzzle && (
        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ 
            fontSize: '20px', 
            marginBottom: '20px',
            color: '#e5e7eb'
          }}>
            🧩 Critical Thinking Puzzle
          </h2>
          
          <div style={{
            background: '#1e40af',
            padding: '25px',
            borderRadius: '12px',
            color: '#f8fafc'
          }}>
            <p style={{ fontSize: '16px', marginBottom: '25px', fontWeight: '600' }}>
              {assignment.assignment.drag_drop_puzzle.prompt}
            </p>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr',
              gap: '30px',
              alignItems: 'start'
            }}>
              {/* Items to Drag (Left Side) */}
              <div>
                <h3 style={{ fontSize: '14px', marginBottom: '15px', opacity: 0.8, textTransform: 'uppercase' }}>
                  📦 Drag These Items:
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {assignment.assignment.drag_drop_puzzle.items.map((item) => {
                    const isPlaced = Object.values(dragDropAnswer).includes(item.id);
                    return (
                      <div
                        key={item.id}
                        draggable={!assignment.completed && !isPlaced}
                        onDragStart={(e) => !assignment.completed && !isPlaced && handleDragStart(e, item.id)}
                        style={{
                          backgroundColor: isPlaced ? 'rgba(107, 114, 128, 0.3)' : 'rgba(59, 130, 246, 0.3)',
                          border: '2px dashed ' + (isPlaced ? 'rgba(107, 114, 128, 0.5)' : 'rgba(96, 165, 250, 0.8)'),
                          padding: '15px 20px',
                          borderRadius: '10px',
                          cursor: !assignment.completed && !isPlaced ? 'grab' : 'not-allowed',
                          textAlign: 'center',
                          fontSize: '15px',
                          fontWeight: '500',
                          opacity: isPlaced ? 0.4 : 1,
                          transition: 'all 0.3s ease',
                          userSelect: 'none'
                        }}
                      >
                        {item.content}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Drop Zones (Right Side) */}
              <div>
                <h3 style={{ fontSize: '14px', marginBottom: '15px', opacity: 0.8, textTransform: 'uppercase' }}>
                  🎯 Drop Zones:
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {assignment.assignment.drag_drop_puzzle.zones.map((zone) => {
                    const placedItemId = dragDropAnswer[zone.id];
                    const placedItem = placedItemId 
                      ? assignment.assignment.drag_drop_puzzle.items.find(item => item.id === placedItemId)
                      : null;
                    
                    return (
                      <div
                        key={zone.id}
                        onDragOver={!assignment.completed ? handleDragOver : null}
                        onDrop={(e) => !assignment.completed && handleDrop(e, zone.id)}
                        style={{
                          border: '2px solid rgba(248, 250, 252, 0.3)',
                          backgroundColor: placedItem ? 'rgba(16, 185, 129, 0.2)' : 'rgba(0, 0, 0, 0.2)',
                          padding: '15px 20px',
                          borderRadius: '10px',
                          minHeight: '60px',
                          transition: 'all 0.3s ease',
                          position: 'relative'
                        }}
                      >
                        <div style={{ 
                          fontSize: '12px', 
                          marginBottom: placedItem ? '8px' : '0',
                          opacity: 0.7,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px'
                        }}>
                          {zone.label}
                        </div>
                        
                        {placedItem ? (
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between'
                          }}>
                            <span style={{ fontSize: '15px', fontWeight: '500' }}>
                              {placedItem.content}
                            </span>
                            {!assignment.completed && (
                              <button
                                onClick={() => handleRemoveFromZone(zone.id)}
                                style={{
                                  backgroundColor: 'rgba(239, 68, 68, 0.3)',
                                  border: 'none',
                                  color: 'white',
                                  padding: '4px 8px',
                                  borderRadius: '5px',
                                  cursor: 'pointer',
                                  fontSize: '12px'
                                }}
                              >
                                ✕
                              </button>
                            )}
                          </div>
                        ) : (
                          <div style={{ 
                            textAlign: 'center',
                            opacity: 0.5,
                            fontSize: '14px',
                            fontStyle: 'italic'
                          }}>
                            Drop item here
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {assignment.completed && assignment.assignment.drag_drop_puzzle.explanation && (
              <div style={{
                marginTop: '20px',
                padding: '15px',
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                borderRadius: '8px',
                border: '1px solid rgba(16, 185, 129, 0.3)'
              }}>
                <p style={{ fontSize: '14px', color: '#10b981', fontWeight: '600', marginBottom: '8px' }}>
                  ✅ Explanation:
                </p>
                <p style={{ fontSize: '14px', opacity: 0.9 }}>
                  {assignment.assignment.drag_drop_puzzle.explanation}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Learn to Read Section */}
      {assignment.assignment.learn_to_read_content && (
        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ 
            fontSize: '20px', 
            marginBottom: '20px',
            color: '#e5e7eb'
          }}>
            📚 Mini Book - Let's Read Together!
          </h2>
          
          <div style={{
            background: '#1e40af',
            padding: '30px',
            borderRadius: '12px',
            color: '#f8fafc'
          }}>
            {/* Story Section */}
            <div style={{ marginBottom: '30px' }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                marginBottom: '20px'
              }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600' }}>📖 Story</h3>
                <button
                  onClick={() => speakText(assignment.assignment.learn_to_read_content.story.join(' '))}
                  style={{
                    backgroundColor: isSpeaking ? 'rgba(251, 191, 36, 0.3)' : 'rgba(16, 185, 129, 0.3)',
                    border: isSpeaking ? '2px solid rgba(251, 191, 36, 0.5)' : '2px solid rgba(16, 185, 129, 0.5)',
                    color: 'white',
                    padding: '10px 20px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    animation: isSpeaking ? 'pulse 1.5s ease-in-out infinite' : 'none'
                  }}
                >
                  {isSpeaking ? '🔊 Reading...' : '🔊 Read Story Aloud'}
                </button>
              </div>
              
              {assignment.assignment.learn_to_read_content.story.map((sentence, index) => (
                <div key={index} style={{
                  backgroundColor: 'rgba(0,0,0,0.2)',
                  padding: '20px',
                  borderRadius: '10px',
                  marginBottom: '15px',
                  fontSize: '20px',
                  lineHeight: '1.8',
                  fontWeight: '500',
                  display: 'flex',
                  alignItems: 'start',
                  gap: '15px'
                }}>
                  <button
                    onClick={() => speakText(sentence)}
                    style={{
                      backgroundColor: 'rgba(59, 130, 246, 0.3)',
                      border: 'none',
                      color: 'white',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '18px',
                      flexShrink: 0
                    }}
                  >
                    🔊
                  </button>
                  <span style={{ flex: 1 }}>{sentence}</span>
                </div>
              ))}
            </div>

            {/* Interactive Activities */}
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px' }}>
                🎯 Word Activities
              </h3>
              
              {assignment.assignment.learn_to_read_content.activities.map((activity, activityIndex) => {
                const sentence = assignment.assignment.learn_to_read_content.story[activity.sentence_index];
                const words = sentence.split(' ');
                const selectedWord = interactiveWordAnswers[activityIndex];
                const isCorrect = assignment.completed && selectedWord?.toLowerCase() === activity.target_word.toLowerCase();
                const isWrong = assignment.completed && selectedWord && selectedWord?.toLowerCase() !== activity.target_word.toLowerCase();
                
                return (
                  <div key={activityIndex} style={{
                    backgroundColor: 'rgba(0,0,0,0.2)',
                    padding: '25px',
                    borderRadius: '10px',
                    marginBottom: '20px'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      marginBottom: '15px',
                      fontSize: '16px',
                      fontWeight: '600'
                    }}>
                      <span style={{
                        backgroundColor: selectedWord ? 'rgba(16, 185, 129, 0.3)' : 'rgba(59, 130, 246, 0.3)',
                        padding: '5px 12px',
                        borderRadius: '6px',
                        fontSize: '14px'
                      }}>
                        Activity {activityIndex + 1}
                      </span>
                      {activity.instruction}
                      <button
                        onClick={() => speakText(activity.instruction)}
                        style={{
                          backgroundColor: 'transparent',
                          border: 'none',
                          color: 'white',
                          cursor: 'pointer',
                          fontSize: '16px'
                        }}
                      >
                        🔊
                      </button>
                    </div>
                    
                    <div style={{ 
                      display: 'flex', 
                      flexWrap: 'wrap', 
                      gap: '10px',
                      fontSize: '18px'
                    }}>
                      {words.map((word, wordIndex) => {
                        const cleanWord = word.replace(/[.,!?;:]/g, '');
                        const isSelected = selectedWord === cleanWord;
                        const isTarget = cleanWord.toLowerCase() === activity.target_word.toLowerCase();
                        
                        return (
                          <button
                            key={wordIndex}
                            onClick={() => handleWordClick(activityIndex, cleanWord)}
                            disabled={assignment.completed}
                            style={{
                              backgroundColor: isSelected 
                                ? (isCorrect || (assignment.completed && isTarget)) 
                                  ? 'rgba(16, 185, 129, 0.4)' 
                                  : isWrong 
                                    ? 'rgba(239, 68, 68, 0.4)'
                                    : 'rgba(59, 130, 246, 0.4)'
                                : 'rgba(255,255,255,0.1)',
                              border: isSelected ? '2px solid rgba(255,255,255,0.8)' : '2px solid rgba(255,255,255,0.2)',
                              color: 'white',
                              padding: '10px 16px',
                              borderRadius: '8px',
                              cursor: assignment.completed ? 'not-allowed' : 'pointer',
                              fontSize: '18px',
                              fontWeight: isSelected ? '600' : '500',
                              transition: 'all 0.2s ease'
                            }}
                          >
                            {word}
                            {assignment.completed && isTarget && ' ✓'}
                          </button>
                        );
                      })}
                    </div>

                    {assignment.completed && (
                      <div style={{
                        marginTop: '15px',
                        padding: '12px',
                        backgroundColor: isCorrect ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                        borderRadius: '8px',
                        fontSize: '14px'
                      }}>
                        {isCorrect ? '✅ Correct!' : `❌ The correct word was: ${activity.target_word}`}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Spelling Section */}
      {assignment.assignment.spelling_exercises && assignment.assignment.spelling_exercises.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ 
            fontSize: '20px', 
            marginBottom: '20px',
            color: '#e5e7eb'
          }}>
            ✏️ Spelling Exercises
          </h2>
          
          {assignment.assignment.spelling_exercises.map((exercise, index) => (
            <div key={index} style={{
              background: '#1e40af',
              padding: '25px',
              borderRadius: '12px',
              marginBottom: '20px',
              color: '#f8fafc'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                <div style={{
                  backgroundColor: 'rgba(248, 250, 252, 0.2)',
                  padding: '5px 12px',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  Exercise {index + 1}
                </div>
                <span style={{
                  backgroundColor: exercise.exercise_type === 'typing_test' 
                    ? 'rgba(59, 130, 246, 0.3)' 
                    : exercise.exercise_type === 'fill_blank'
                      ? 'rgba(16, 185, 129, 0.3)'
                      : 'rgba(251, 191, 36, 0.3)',
                  padding: '4px 10px',
                  borderRadius: '5px',
                  fontSize: '12px',
                  textTransform: 'uppercase'
                }}>
                  {exercise.exercise_type === 'typing_test' ? '⌨️ Type' : exercise.exercise_type === 'fill_blank' ? '📝 Fill' : '✓ Choose'}
                </span>
              </div>

              {/* Example Sentence with Audio */}
              {exercise.example_sentence && (
                <div style={{
                  backgroundColor: 'rgba(0,0,0,0.2)',
                  padding: '15px',
                  borderRadius: '8px',
                  marginBottom: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}>
                  <button
                    onClick={() => speakText(exercise.example_sentence)}
                    style={{
                      backgroundColor: 'rgba(59, 130, 246, 0.3)',
                      border: 'none',
                      color: 'white',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '16px'
                    }}
                  >
                    🔊
                  </button>
                  <span style={{ fontSize: '15px', fontStyle: 'italic' }}>
                    {exercise.example_sentence}
                  </span>
                </div>
              )}

              {/* Typing Test */}
              {exercise.exercise_type === 'typing_test' && (
                <div>
                  <label style={{ display: 'block', marginBottom: '10px', fontSize: '15px' }}>
                    Type the word you hear:
                  </label>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <button
                      onClick={() => speakText(exercise.word)}
                      style={{
                        backgroundColor: 'rgba(16, 185, 129, 0.3)',
                        border: '2px solid rgba(16, 185, 129, 0.5)',
                        color: 'white',
                        padding: '10px 16px',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px'
                      }}
                    >
                      🔊 Hear Word
                    </button>
                    <input
                      type="text"
                      value={spellingAnswers[index] || ''}
                      onChange={(e) => handleSpellingAnswer(index, e.target.value)}
                      disabled={assignment.completed}
                      placeholder="Type your answer here..."
                      style={{
                        flex: 1,
                        backgroundColor: 'rgba(0,0,0,0.3)',
                        border: '1px solid rgba(248, 250, 252, 0.2)',
                        color: 'white',
                        padding: '12px',
                        borderRadius: '8px',
                        fontSize: '16px'
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Fill in the Blank */}
              {exercise.exercise_type === 'fill_blank' && (
                <div>
                  <label style={{ display: 'block', marginBottom: '10px', fontSize: '15px' }}>
                    Fill in the missing word:
                  </label>
                  <div style={{
                    backgroundColor: 'rgba(0,0,0,0.2)',
                    padding: '15px',
                    borderRadius: '8px',
                    marginBottom: '12px',
                    fontSize: '16px'
                  }}>
                    {exercise.fill_blank_sentence}
                  </div>
                  <input
                    type="text"
                    value={spellingAnswers[index] || ''}
                    onChange={(e) => handleSpellingAnswer(index, e.target.value)}
                    disabled={assignment.completed}
                    placeholder="Type your answer here..."
                    style={{
                      width: '100%',
                      backgroundColor: 'rgba(0,0,0,0.3)',
                      border: '1px solid rgba(248, 250, 252, 0.2)',
                      color: 'white',
                      padding: '12px',
                      borderRadius: '8px',
                      fontSize: '16px'
                    }}
                  />
                </div>
              )}

              {/* Multiple Choice */}
              {exercise.exercise_type === 'multiple_choice' && (
                <div>
                  <label style={{ display: 'block', marginBottom: '10px', fontSize: '15px' }}>
                    Choose the correct spelling:
                  </label>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                    {exercise.multiple_choice_options.map((option, optIndex) => {
                      const isSelected = spellingAnswers[index] === option;
                      const isCorrect = assignment.completed && option === exercise.correct_answer;
                      const isWrong = assignment.completed && isSelected && option !== exercise.correct_answer;
                      
                      return (
                        <button
                          key={optIndex}
                          onClick={() => handleSpellingAnswer(index, option)}
                          disabled={assignment.completed}
                          style={{
                            backgroundColor: isCorrect 
                              ? 'rgba(16, 185, 129, 0.3)' 
                              : isWrong 
                                ? 'rgba(239, 68, 68, 0.3)'
                                : isSelected 
                                  ? 'rgba(59, 130, 246, 0.4)'
                                  : 'rgba(255,255,255,0.1)',
                            border: isSelected ? '2px solid rgba(255,255,255,0.8)' : '2px solid rgba(255,255,255,0.2)',
                            color: 'white',
                            padding: '15px',
                            borderRadius: '8px',
                            cursor: assignment.completed ? 'not-allowed' : 'pointer',
                            fontSize: '16px',
                            fontWeight: isSelected ? '600' : '500',
                            textAlign: 'center',
                            transition: 'all 0.2s ease'
                          }}
                        >
                          {option}
                          {isCorrect && ' ✓'}
                          {isWrong && ' ✗'}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Show Correct Answer After Submission */}
              {assignment.completed && (
                <div style={{
                  marginTop: '15px',
                  padding: '12px',
                  backgroundColor: spellingAnswers[index]?.toLowerCase() === exercise.correct_answer.toLowerCase()
                    ? 'rgba(16, 185, 129, 0.2)'
                    : 'rgba(239, 68, 68, 0.2)',
                  borderRadius: '8px',
                  border: '1px solid ' + (spellingAnswers[index]?.toLowerCase() === exercise.correct_answer.toLowerCase()
                    ? 'rgba(16, 185, 129, 0.3)'
                    : 'rgba(239, 68, 68, 0.3)'),
                  fontSize: '14px'
                }}>
                  {spellingAnswers[index]?.toLowerCase() === exercise.correct_answer.toLowerCase() 
                    ? '✅ Correct!' 
                    : `❌ Correct spelling: ${exercise.correct_answer}`}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Submit Button */}
      {!assignment.completed && (
        <div style={{
          background: 'rgba(255,255,255,0.05)',
          padding: '20px',
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <p style={{ fontSize: '14px', marginBottom: '15px', opacity: 0.8 }}>
            Make sure you've answered all questions and completed all coding exercises.
          </p>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            style={{
              background: submitting 
                ? 'rgba(107, 114, 128, 0.5)' 
                : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              padding: '15px 30px',
              border: 'none',
              borderRadius: '10px',
              cursor: submitting ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            {submitting ? '⏳ Submitting...' : '🚀 Submit Assignment'}
          </button>
        </div>
      )}
    </div>
  );
};

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
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      color: 'white', 
      padding: '20px' 
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Modern Header */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '30px',
          background: 'rgba(255,255,255,0.05)',
          padding: '20px 25px',
          borderRadius: '16px',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <div>
            <h1 style={{ 
              fontSize: '32px', 
              margin: '0 0 5px 0',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
              fontWeight: 'bold'
            }}>
              🎓 Keystone Learning Portal
            </h1>
            <p style={{ margin: 0, opacity: 0.7, fontSize: '14px' }}>
              Welcome back, {user.first_name}! 👋
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              onClick={handleLogout}
              style={{ 
                background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                color: 'white', 
                padding: '10px 16px',
                border: 'none',
                borderRadius: '10px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
              onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            >
              🚪 Logout
            </button>
          </div>
        </div>

        {/* Modern Navigation */}
        <div style={{ marginBottom: '25px' }}>
          <div style={{ 
            display: 'flex', 
            gap: '8px', 
            flexWrap: 'wrap',
            background: 'rgba(255,255,255,0.05)',
            padding: '8px',
            borderRadius: '12px',
            backdropFilter: 'blur(10px)'
          }}>
            {[
              { path: '/student', icon: '🏠', label: 'Dashboard' },
              { path: '/student/assignments', icon: '📚', label: 'Assignments' },
              { path: '/student/grades', icon: '📊', label: 'Grades' }
            ].map(({ path, icon, label }) => (
              <button
                key={path}
                onClick={() => navigate(path)}
                style={{
                  background: location.pathname === path 
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                    : 'transparent',
                  color: 'white',
                  padding: '12px 20px',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: '600',
                  transition: 'all 0.2s ease',
                  opacity: location.pathname === path ? 1 : 0.7
                }}
                onMouseEnter={(e) => {
                  if (location.pathname !== path) {
                    e.target.style.background = 'rgba(255,255,255,0.1)';
                    e.target.style.opacity = '1';
                  }
                }}
                onMouseLeave={(e) => {
                  if (location.pathname !== path) {
                    e.target.style.background = 'transparent';
                    e.target.style.opacity = '0.7';
                  }
                }}
              >
                {icon} {label}
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div style={{ 
          background: 'rgba(255,255,255,0.03)', 
          padding: '30px', 
          borderRadius: '16px',
          minHeight: '500px',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.05)'
        }}>
          <Routes>
            <Route index element={<StudentHome user={user} navigate={navigate} />} />
            <Route path="assignments" element={<StudentAssignments user={user} />} />
            <Route path="assignment/:assignmentId" element={<StudentAssignmentView user={user} navigate={navigate} />} />
            <Route path="grades" element={<StudentGrades user={user} />} />
            <Route path="rewards" element={<StudentRewards user={user} />} />
            <Route path="*" element={<StudentHome user={user} navigate={navigate} />} />
          </Routes>
        </div>
      </div>

      {/* Add CSS for animations */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `
      }} />
    </div>
  );
};

// Student Rewards Store Component
const StudentRewards = ({ user }) => {
  const [rewards, setRewards] = useState([]);
  const [pointsData, setPointsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [redeeming, setRedeeming] = useState(null);

  useEffect(() => {
    fetchRewardsAndPoints();
  }, []);

  const fetchRewardsAndPoints = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Fetch rewards
      const rewardsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/rewards`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Fetch student points
      const pointsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/student/points`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (rewardsResponse.ok && pointsResponse.ok) {
        setRewards(await rewardsResponse.json());
        setPointsData(await pointsResponse.json());
      }
    } catch (error) {
      console.error('Error fetching rewards:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRedeem = async (rewardId, rewardTitle, pointsCost) => {
    if (!window.confirm(`Are you sure you want to redeem "${rewardTitle}" for ${pointsCost} points?`)) {
      return;
    }

    setRedeeming(rewardId);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/student/redeem?reward_id=${rewardId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(`🎉 ${result.message}\nRemaining Points: ${result.remaining_points}`);
        fetchRewardsAndPoints(); // Refresh data
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to redeem reward');
      }
    } catch (error) {
      console.error('Error redeeming reward:', error);
      alert('Error redeeming reward. Please try again.');
    } finally {
      setRedeeming(null);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '4px solid #e5e7eb',
          borderTop: '4px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 20px'
        }}></div>
        <p style={{ color: '#94a3b8' }}>Loading rewards...</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header with Points Display */}
      <div style={{
        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        padding: '40px',
        borderRadius: '20px',
        marginBottom: '30px',
        textAlign: 'center',
        color: 'white',
        boxShadow: '0 10px 30px rgba(245, 158, 11, 0.3)'
      }}>
        <div style={{ fontSize: '64px', marginBottom: '10px' }}>🏆</div>
        <h2 style={{ fontSize: '32px', margin: '0 0 10px 0', fontWeight: 'bold' }}>
          Rewards Store
        </h2>
        <div style={{
          fontSize: '48px',
          fontWeight: 'bold',
          marginTop: '20px',
          textShadow: '2px 2px 4px rgba(0,0,0,0.2)'
        }}>
          {pointsData?.total_points || 0} Points
        </div>
        <p style={{ fontSize: '16px', opacity: 0.9, marginTop: '10px' }}>
          💡 Earn 5 points for every assignment with a grade of 85% or higher!
        </p>
      </div>

      {/* Available Rewards */}
      <div style={{ marginBottom: '40px' }}>
        <h3 style={{ 
          fontSize: '24px', 
          marginBottom: '20px',
          color: '#e5e7eb',
          fontWeight: 'bold'
        }}>
          🎁 Available Rewards
        </h3>

        {rewards.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: '12px',
            color: '#94a3b8'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>🎪</div>
            <p style={{ fontSize: '18px' }}>No rewards available yet!</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>Check back later for awesome rewards!</p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '20px'
          }}>
            {rewards.map((reward) => {
              const canAfford = pointsData && pointsData.total_points >= reward.points_cost;
              const isRedeeming = redeeming === reward.id;

              return (
                <div key={reward.id} style={{
                  background: canAfford 
                    ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)'
                    : 'rgba(255,255,255,0.03)',
                  border: canAfford 
                    ? '2px solid rgba(16, 185, 129, 0.3)'
                    : '2px solid rgba(255,255,255,0.1)',
                  borderRadius: '16px',
                  padding: '25px',
                  transition: 'all 0.3s ease',
                  position: 'relative',
                  overflow: 'hidden'
                }}>
                  {/* Reward Icon based on title */}
                  <div style={{
                    fontSize: '48px',
                    marginBottom: '15px',
                    textAlign: 'center'
                  }}>
                    {reward.title.toLowerCase().includes('game') ? '🎮' :
                     reward.title.toLowerCase().includes('coke') ? '🥤' :
                     reward.title.toLowerCase().includes('tv') ? '📺' :
                     reward.title.toLowerCase().includes('day off') ? '🏖️' : '🎁'}
                  </div>

                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: 'bold',
                    color: '#e5e7eb',
                    marginBottom: '8px',
                    textAlign: 'center'
                  }}>
                    {reward.title}
                  </h4>

                  <p style={{
                    fontSize: '14px',
                    color: '#94a3b8',
                    marginBottom: '20px',
                    textAlign: 'center',
                    minHeight: '40px'
                  }}>
                    {reward.description}
                  </p>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '15px',
                    padding: '12px',
                    background: 'rgba(0,0,0,0.2)',
                    borderRadius: '8px'
                  }}>
                    <span style={{ color: '#94a3b8', fontSize: '14px' }}>Cost:</span>
                    <span style={{
                      fontSize: '20px',
                      fontWeight: 'bold',
                      color: canAfford ? '#10b981' : '#f59e0b'
                    }}>
                      {reward.points_cost} pts
                    </span>
                  </div>

                  <button
                    onClick={() => handleRedeem(reward.id, reward.title, reward.points_cost)}
                    disabled={!canAfford || isRedeeming}
                    style={{
                      width: '100%',
                      padding: '12px',
                      backgroundColor: canAfford ? '#10b981' : '#6b7280',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      cursor: canAfford && !isRedeeming ? 'pointer' : 'not-allowed',
                      opacity: !canAfford || isRedeeming ? 0.6 : 1,
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {isRedeeming ? '⏳ Redeeming...' : canAfford ? '🎉 Redeem Now' : '🔒 Need More Points'}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Redemption History */}
      {pointsData && pointsData.redemptions && pointsData.redemptions.length > 0 && (
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{ 
            fontSize: '24px', 
            marginBottom: '20px',
            color: '#e5e7eb',
            fontWeight: 'bold'
          }}>
            📜 Your Redemption History
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {pointsData.redemptions.slice(0, 10).map((redemption) => (
              <div key={redemption.id} style={{
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.2)',
                borderRadius: '12px',
                padding: '15px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ color: '#e5e7eb', fontSize: '16px', fontWeight: '500' }}>
                    {redemption.reward_title}
                  </div>
                  <div style={{ color: '#94a3b8', fontSize: '13px', marginTop: '4px' }}>
                    {new Date(redemption.redeemed_at).toLocaleDateString()} at {new Date(redemption.redeemed_at).toLocaleTimeString()}
                  </div>
                </div>
                <div style={{
                  color: '#10b981',
                  fontSize: '16px',
                  fontWeight: 'bold'
                }}>
                  -{redemption.points_spent} pts
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Points History */}
      {pointsData && pointsData.transactions && pointsData.transactions.length > 0 && (
        <div>
          <h3 style={{ 
            fontSize: '24px', 
            marginBottom: '20px',
            color: '#e5e7eb',
            fontWeight: 'bold'
          }}>
            💰 Points History
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {pointsData.transactions.slice(0, 15).map((transaction) => (
              <div key={transaction.id} style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                padding: '15px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ color: '#e5e7eb', fontSize: '14px' }}>
                    {transaction.transaction_type === 'earned' && '📚 '}
                    {transaction.transaction_type === 'redeemed' && '🎁 '}
                    {transaction.transaction_type === 'manual_add' && '➕ '}
                    {transaction.transaction_type === 'manual_subtract' && '➖ '}
                    {transaction.description}
                  </div>
                  <div style={{ color: '#94a3b8', fontSize: '12px', marginTop: '4px' }}>
                    {new Date(transaction.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div style={{
                  color: transaction.points > 0 ? '#10b981' : '#ef4444',
                  fontSize: '16px',
                  fontWeight: 'bold'
                }}>
                  {transaction.points > 0 ? '+' : ''}{transaction.points} pts
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
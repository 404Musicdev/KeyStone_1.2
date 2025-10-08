import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/auth/Login';
import TeacherDashboard from './components/teacher/TeacherDashboard';
import StudentDashboard from './components/student/StudentDashboard';
import { Toaster } from './components/ui/sonner';

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, isAuthenticated, loading } = useAuth();
  
  console.log('ProtectedRoute check:', { isAuthenticated, user, requiredRole, loading });
  
  if (loading) {
    return <div style={{color: 'white', padding: '20px'}}>Loading...</div>;
  }
  
  if (!isAuthenticated || !user) {
    console.log('Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  if (requiredRole && user.role !== requiredRole) {
    console.log(`Role mismatch: expected ${requiredRole}, got ${user.role}`);
    return <Navigate to="/login" replace />;
  }
  
  console.log('ProtectedRoute: Access granted');
  return children;
};

// Main App Component
const AppContent = () => {
  const { isAuthenticated, user } = useAuth();
  
  return (
    <div className="min-h-screen bg-slate-950">
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? (
              <Navigate to={user?.role === 'teacher' ? '/teacher' : '/student'} replace />
            ) : (
              <Login />
            )
          } 
        />
        <Route 
          path="/teacher/*" 
          element={
            <ProtectedRoute requiredRole="teacher">
              <TeacherDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/student/*" 
          element={<StudentDashboard />} 
        />
        <Route 
          path="/test" 
          element={
            <div style={{backgroundColor: 'green', color: 'white', padding: '50px', fontSize: '30px'}}>
              🟢 TEST ROUTE WORKS - If you see this, routing is OK
            </div>
          } 
        />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
      <Toaster position="top-right" />
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
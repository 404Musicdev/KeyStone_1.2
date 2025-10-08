import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/auth/Login';
import TeacherDashboard from './components/teacher/TeacherDashboard';
import StudentDashboard from './components/student/StudentDashboard';
import { Toaster } from './components/ui/sonner';

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/login" replace />;
  }
  
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
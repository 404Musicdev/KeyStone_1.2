import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('StudentDashboard Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 space-y-4">
          <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-lg">
            <h3 className="text-red-400 font-medium mb-2">Dashboard Error</h3>
            <p className="text-gray-300 text-sm">Something went wrong loading the student dashboard.</p>
            <p className="text-gray-400 text-xs mt-2">Error: {this.state.error?.message}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { 
  LogOut, 
  User, 
  FileText, 
  BarChart3, 
  MessageSquare,
  Home,
  Menu,
  X,
  GraduationCap 
} from 'lucide-react';

// Simple Student Overview Component
const SimpleStudentOverview = () => {
  const { user } = useAuth();
  
  // Debug logging
  React.useEffect(() => {
    console.log('SimpleStudentOverview mounted with user:', user);
  }, [user]);
  
  // Fallback if user data is not available
  if (!user) {
    return (
      <div className="space-y-6">
        <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-lg">
          <p className="text-red-400 font-medium">Loading user data...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="fade-in">
        <h1 className="text-3xl font-bold text-white mb-2">Welcome back, {user?.first_name || 'Student'}!</h1>
        <p className="text-gray-300">Here's your learning dashboard</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-gray-900 border-gray-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">My Assignments</p>
                <p className="text-2xl font-bold text-white mt-1">0</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Completed</p>
                <p className="text-2xl font-bold text-green-400 mt-1">0</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Average Grade</p>
                <p className="text-2xl font-bold text-purple-400 mt-1">--</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white">Student Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
              <p className="text-green-400 font-medium">✅ Dashboard loaded successfully!</p>
              <p className="text-gray-300 text-sm mt-1">You are logged in as: {user?.username}</p>
            </div>
            
            <div className="text-gray-300 space-y-2">
              <p><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>
              <p><strong>Username:</strong> @{user?.username}</p>
              <p><strong>Role:</strong> {user?.role}</p>
              
              {/* Emergency logout button */}
              <div className="mt-4 pt-4 border-t border-gray-700">
                <button 
                  onClick={() => {
                    localStorage.clear();
                    sessionStorage.clear();
                    window.location.href = '/';
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                >
                  Emergency Logout
                </button>
                <p className="text-gray-400 text-xs mt-1">Use this if you get stuck on this page</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Simple Sidebar Component
const SimpleSidebar = ({ isOpen, onToggle, onLogout }) => {
  const { user } = useAuth();

  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/student' },
    { icon: FileText, label: 'Assignments', path: '/student/assignments' },
    { icon: BarChart3, label: 'My Grades', path: '/student/grades' },
    { icon: MessageSquare, label: 'Messages', path: '/student/messages' },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" 
          onClick={onToggle}
        />
      )}
      
      {/* Mobile menu button */}
      <button
        onClick={onToggle}
        className="fixed top-4 left-4 z-50 lg:hidden p-2 bg-gray-800 text-white rounded-lg border border-gray-700 hover:bg-gray-700 transition-colors"
      >
        {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Sidebar */}
      <aside 
        className={`
          fixed top-0 left-0 z-40 w-64 h-full bg-gray-900 border-r border-gray-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Keystone Homeschool</h2>
                <p className="text-sm text-gray-400">Student Portal</p>
              </div>
            </div>
          </div>

          {/* User Info */}
          <div className="p-6 border-b border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-gray-400 text-sm truncate">@{user?.username}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              
              return (
                <button
                  key={item.path}
                  className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all duration-200 text-gray-300 hover:bg-gray-800 hover:text-white"
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-gray-700">
            <Button
              onClick={onLogout}
              variant="outline"
              className="w-full border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white hover:border-gray-500"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
};

const StudentDashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Debug logging
  React.useEffect(() => {
    console.log('StudentDashboard mounted successfully');
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex" data-testid="student-dashboard">
      <SimpleSidebar 
        isOpen={sidebarOpen} 
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onLogout={handleLogout}
      />
      
      <main className="flex-1 lg:ml-64 transition-all duration-300">
        <div className="p-6 min-h-screen bg-slate-900">
          <ErrorBoundary>
            <Routes>
              <Route index element={<SimpleStudentOverview />} />
              <Route path="*" element={<SimpleStudentOverview />} />
            </Routes>
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
};

export default StudentDashboard;
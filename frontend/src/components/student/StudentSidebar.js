import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';
import { 
  Home, 
  FileText, 
  BarChart3, 
  MessageSquare, 
  LogOut,
  Menu,
  X,
  GraduationCap,
  User
} from 'lucide-react';

const StudentSidebar = ({ isOpen, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/student' },
    { icon: FileText, label: 'Assignments', path: '/student/assignments' },
    { icon: BarChart3, label: 'My Grades', path: '/student/grades' },
    { icon: MessageSquare, label: 'Messages', path: '/student/messages' },
  ];

  const handleNavigation = (path) => {
    navigate(path);
    if (window.innerWidth < 1024) {
      onToggle();
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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
        className="fixed top-4 left-4 z-50 lg:hidden p-2 bg-slate-800 text-white rounded-lg border border-slate-700 hover:bg-slate-700 transition-colors"
        data-testid="mobile-menu-button"
      >
        {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Sidebar */}
      <aside 
        className={`
          fixed top-0 left-0 z-40 w-64 h-full bg-slate-800 border-r border-slate-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        data-testid="student-sidebar"
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-slate-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Keystone Homeschool</h2>
                <p className="text-sm text-slate-400">Student Portal</p>
              </div>
            </div>
          </div>

          {/* User Info */}
          <div className="p-6 border-b border-slate-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-slate-400 text-sm truncate">@{user?.username}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <button
                  key={item.path}
                  onClick={() => handleNavigation(item.path)}
                  className={`
                    w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all duration-200
                    ${isActive 
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25' 
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                    }
                  `}
                  data-testid={`sidebar-${item.label.toLowerCase().replace(' ', '-')}`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-slate-700">
            <Button
              onClick={handleLogout}
              variant="outline"
              className="w-full border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white hover:border-slate-500"
              data-testid="logout-button"
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

export default StudentSidebar;
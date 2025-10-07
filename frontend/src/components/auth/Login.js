import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Label } from '../ui/label';
import { toast } from 'sonner';
import { Eye, EyeOff, GraduationCap, Users } from 'lucide-react';

const Login = () => {
  const { login, register } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState('teacher-login');

  // Teacher Login Form
  const [teacherLogin, setTeacherLogin] = useState({
    email: '',
    password: ''
  });

  // Student Login Form
  const [studentLogin, setStudentLogin] = useState({
    username: '',
    password: ''
  });

  // Teacher Registration Form
  const [teacherRegister, setTeacherRegister] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'teacher'
  });

  const handleTeacherLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const result = await login(teacherLogin, 'teacher');
      if (result.success) {
        toast.success('Welcome back!');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Login failed. Please try again.');
    }
    
    setIsLoading(false);
  };

  const handleStudentLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const result = await login(studentLogin, 'student');
      if (result.success) {
        toast.success('Welcome back!');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Login failed. Please try again.');
    }
    
    setIsLoading(false);
  };

  const handleTeacherRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const result = await register(teacherRegister);
      if (result.success) {
        toast.success('Account created successfully!');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Registration failed. Please try again.');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center">
            <GraduationCap className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Keystone Homeschool</h1>
          <p className="text-slate-400">Empowering education, one student at a time</p>
        </div>

        {/* Main Card */}
        <Card className="bg-gray-900 border-gray-600 slide-up" data-testid="login-card">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center text-white">Welcome</CardTitle>
            <CardDescription className="text-center text-slate-300">
              Sign in to your account or create a new one
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid grid-cols-3 mb-6 bg-gray-800 border border-gray-600">
                <TabsTrigger 
                  value="teacher-login" 
                  className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-slate-300"
                  data-testid="teacher-login-tab"
                >
                  <Users className="w-4 h-4 mr-2" />
                  Teacher
                </TabsTrigger>
                <TabsTrigger 
                  value="student-login" 
                  className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-slate-300"
                  data-testid="student-login-tab"
                >
                  <GraduationCap className="w-4 h-4 mr-2" />
                  Student
                </TabsTrigger>
                <TabsTrigger 
                  value="teacher-register" 
                  className="data-[state=active]:bg-blue-600 data-[state=active]:text-white text-slate-300"
                  data-testid="teacher-register-tab"
                >
                  Sign Up
                </TabsTrigger>
              </TabsList>

              {/* Teacher Login */}
              <TabsContent value="teacher-login">
                <form onSubmit={handleTeacherLogin} className="space-y-4" data-testid="teacher-login-form">
                  <div className="space-y-2">
                    <Label htmlFor="teacher-email" className="text-slate-300">Email</Label>
                    <Input
                      id="teacher-email"
                      type="email"
                      placeholder="Enter your email"
                      value={teacherLogin.email}
                      onChange={(e) => setTeacherLogin({...teacherLogin, email: e.target.value})}
                      className="bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500"
                      required
                      data-testid="teacher-email-input"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="teacher-password" className="text-slate-300">Password</Label>
                    <div className="relative">
                      <Input
                        id="teacher-password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        value={teacherLogin.password}
                        onChange={(e) => setTeacherLogin({...teacherLogin, password: e.target.value})}
                        className="bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500 pr-10"
                        required
                        data-testid="teacher-password-input"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-white"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5"
                    disabled={isLoading}
                    data-testid="teacher-login-button"
                  >
                    {isLoading ? (
                      <div className="flex items-center">
                        <div className="loading-spinner w-4 h-4 mr-2"></div>
                        Signing in...
                      </div>
                    ) : (
                      'Sign in as Teacher'
                    )}
                  </Button>
                </form>
              </TabsContent>

              {/* Student Login */}
              <TabsContent value="student-login">
                <form onSubmit={handleStudentLogin} className="space-y-4" data-testid="student-login-form">
                  <div className="space-y-2">
                    <Label htmlFor="student-username" className="text-slate-300">Username</Label>
                    <Input
                      id="student-username"
                      type="text"
                      placeholder="Enter your username"
                      value={studentLogin.username}
                      onChange={(e) => setStudentLogin({...studentLogin, username: e.target.value})}
                      className="bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500"
                      required
                      data-testid="student-username-input"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="student-password" className="text-slate-300">Password</Label>
                    <div className="relative">
                      <Input
                        id="student-password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        value={studentLogin.password}
                        onChange={(e) => setStudentLogin({...studentLogin, password: e.target.value})}
                        className="bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500 pr-10"
                        required
                        data-testid="student-password-input"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-white"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5"
                    disabled={isLoading}
                    data-testid="student-login-button"
                  >
                    {isLoading ? (
                      <div className="flex items-center">
                        <div className="loading-spinner w-4 h-4 mr-2"></div>
                        Signing in...
                      </div>
                    ) : (
                      'Sign in as Student'
                    )}
                  </Button>
                </form>
              </TabsContent>

              {/* Teacher Registration */}
              <TabsContent value="teacher-register">
                <form onSubmit={handleTeacherRegister} className="space-y-4" data-testid="teacher-register-form">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first-name" className="text-slate-300">First Name</Label>
                      <Input
                        id="first-name"
                        type="text"
                        placeholder="First name"
                        value={teacherRegister.first_name}
                        onChange={(e) => setTeacherRegister({...teacherRegister, first_name: e.target.value})}
                        className="bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500"
                        required
                        data-testid="register-firstname-input"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="last-name" className="text-slate-300">Last Name</Label>
                      <Input
                        id="last-name"
                        type="text"
                        placeholder="Last name"
                        value={teacherRegister.last_name}
                        onChange={(e) => setTeacherRegister({...teacherRegister, last_name: e.target.value})}
                        className="bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500"
                        required
                        data-testid="register-lastname-input"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="register-email" className="text-slate-300">Email</Label>
                    <Input
                      id="register-email"
                      type="email"
                      placeholder="Enter your email"
                      value={teacherRegister.email}
                      onChange={(e) => setTeacherRegister({...teacherRegister, email: e.target.value})}
                      className="bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500"
                      required
                      data-testid="register-email-input"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="register-password" className="text-slate-300">Password</Label>
                    <div className="relative">
                      <Input
                        id="register-password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Create a password"
                        value={teacherRegister.password}
                        onChange={(e) => setTeacherRegister({...teacherRegister, password: e.target.value})}
                        className="bg-slate-800 border-slate-600 text-white placeholder-slate-400 focus:border-blue-500 pr-10"
                        required
                        data-testid="register-password-input"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-white"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5"
                    disabled={isLoading}
                    data-testid="teacher-register-button"
                  >
                    {isLoading ? (
                      <div className="flex items-center">
                        <div className="loading-spinner w-4 h-4 mr-2"></div>
                        Creating account...
                      </div>
                    ) : (
                      'Create Teacher Account'
                    )}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-6 fade-in">
          <p className="text-slate-400 text-sm">
            Secure • Modern • Educational
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
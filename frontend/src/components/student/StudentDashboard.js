import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import StudentSidebar from './StudentSidebar';
import StudentOverview from './StudentOverview';
import StudentAssignments from './StudentAssignments';
import StudentGrades from './StudentGrades';
import StudentMessages from './StudentMessages';
import AssignmentView from './AssignmentView';

const StudentDashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-black flex" data-testid="student-dashboard">
      <StudentSidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      <main className="flex-1 lg:ml-64 transition-all duration-300">
        <div className="p-6">
          <Routes>
            <Route index element={<StudentOverview />} />
            <Route path="assignments" element={<StudentAssignments />} />
            <Route path="assignments/:assignmentId" element={<AssignmentView />} />
            <Route path="grades" element={<StudentGrades />} />
            <Route path="messages" element={<StudentMessages />} />
          </Routes>
        </div>
      </main>
    </div>
  );
};

export default StudentDashboard;
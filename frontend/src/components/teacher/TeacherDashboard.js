import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './Sidebar';
import Overview from './Overview';
import StudentManagement from './StudentManagement';
import AssignmentGenerator from './AssignmentGenerator';
import LessonPlanGenerator from './LessonPlanGenerator';
import Gradebook from './Gradebook';
import Messaging from './Messaging';
import RewardsManagement from './RewardsManagement';
import SpellingWordLists from './SpellingWordLists';

const TeacherDashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-black flex" data-testid="teacher-dashboard">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      <main className="flex-1 lg:ml-64 transition-all duration-300">
        <div className="p-6">
          <Routes>
            <Route index element={<Overview />} />
            <Route path="students" element={<StudentManagement />} />
            <Route path="assignments" element={<AssignmentGenerator />} />
            <Route path="lesson-plans" element={<LessonPlanGenerator />} />
            <Route path="gradebook" element={<Gradebook />} />
            <Route path="rewards" element={<RewardsManagement />} />
            <Route path="spelling-words" element={<SpellingWordLists />} />
            <Route path="messages" element={<Messaging />} />
          </Routes>
        </div>
      </main>
    </div>
  );
};

export default TeacherDashboard;
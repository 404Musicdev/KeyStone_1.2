import React from 'react';

const StudentDashboard = () => {
  console.log('StudentDashboard component is rendering!');
  
  const handleEmergencyReset = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/';
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: 'red', 
      color: 'white', 
      padding: '40px',
      fontSize: '24px'
    }}>
      <h1>🚨 BASIC TEST - CAN YOU SEE THIS? 🚨</h1>
      <p>If you can see this red screen, the component is working!</p>
      <button 
        onClick={handleEmergencyReset}
        style={{ 
          backgroundColor: 'yellow', 
          color: 'black', 
          padding: '20px',
          border: 'none',
          fontSize: '20px',
          cursor: 'pointer'
        }}
      >
        EMERGENCY RESET
      </button>
    </div>
  );
};

export default StudentDashboard;
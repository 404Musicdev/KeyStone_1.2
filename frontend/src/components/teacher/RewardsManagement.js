import React, { useState, useEffect } from 'react';

const RewardsManagement = () => {
  const [rewards, setRewards] = useState([]);
  const [students, setStudents] = useState([]);
  const [studentPoints, setStudentPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('rewards'); // 'rewards' or 'students'
  
  // Form states
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingReward, setEditingReward] = useState(null);
  const [newReward, setNewReward] = useState({ title: '', description: '', points_cost: '' });
  
  // Points adjustment
  const [adjustingStudent, setAdjustingStudent] = useState(null);
  const [pointsAdjustment, setPointsAdjustment] = useState({ points: '', description: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Fetch rewards
      const rewardsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/rewards`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Fetch student points
      const pointsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/teacher/student-points`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (rewardsResponse.ok && pointsResponse.ok) {
        setRewards(await rewardsResponse.json());
        setStudentPoints(await pointsResponse.json());
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const initializeDefaultRewards = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/teacher/initialize-rewards`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        alert('Default rewards initialized successfully!');
        fetchData();
      }
    } catch (error) {
      console.error('Error initializing rewards:', error);
    }
  };

  const handleAddReward = async () => {
    if (!newReward.title || !newReward.description || !newReward.points_cost) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/rewards`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: newReward.title,
          description: newReward.description,
          points_cost: parseInt(newReward.points_cost)
        })
      });

      if (response.ok) {
        alert('Reward added successfully!');
        setNewReward({ title: '', description: '', points_cost: '' });
        setShowAddForm(false);
        fetchData();
      }
    } catch (error) {
      console.error('Error adding reward:', error);
      alert('Error adding reward');
    }
  };

  const handleUpdateReward = async () => {
    if (!editingReward.title || !editingReward.description || !editingReward.points_cost) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/rewards/${editingReward.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: editingReward.title,
          description: editingReward.description,
          points_cost: parseInt(editingReward.points_cost)
        })
      });

      if (response.ok) {
        alert('Reward updated successfully!');
        setEditingReward(null);
        fetchData();
      }
    } catch (error) {
      console.error('Error updating reward:', error);
      alert('Error updating reward');
    }
  };

  const handleDeleteReward = async (rewardId, rewardTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${rewardTitle}"?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/rewards/${rewardId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Reward deleted successfully!');
        fetchData();
      }
    } catch (error) {
      console.error('Error deleting reward:', error);
      alert('Error deleting reward');
    }
  };

  const handleAdjustPoints = async () => {
    if (!pointsAdjustment.points || !pointsAdjustment.description) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/teacher/points`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          student_id: adjustingStudent,
          points: parseInt(pointsAdjustment.points),
          description: pointsAdjustment.description
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Points adjusted! New total: ${result.new_total}`);
        setAdjustingStudent(null);
        setPointsAdjustment({ points: '', description: '' });
        fetchData();
      }
    } catch (error) {
      console.error('Error adjusting points:', error);
      alert('Error adjusting points');
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
        <p style={{ color: '#94a3b8' }}>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{
        fontSize: '32px',
        fontWeight: 'bold',
        marginBottom: '30px',
        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        color: 'transparent'
      }}>
        🏆 Rewards Management
      </h1>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '30px',
        borderBottom: '2px solid rgba(255,255,255,0.1)',
        paddingBottom: '10px'
      }}>
        <button
          onClick={() => setActiveTab('rewards')}
          style={{
            padding: '12px 24px',
            backgroundColor: activeTab === 'rewards' ? '#f59e0b' : 'transparent',
            color: 'white',
            border: 'none',
            borderRadius: '8px 8px 0 0',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            transition: 'all 0.3s ease'
          }}
        >
          🎁 Manage Rewards
        </button>
        <button
          onClick={() => setActiveTab('students')}
          style={{
            padding: '12px 24px',
            backgroundColor: activeTab === 'students' ? '#f59e0b' : 'transparent',
            color: 'white',
            border: 'none',
            borderRadius: '8px 8px 0 0',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            transition: 'all 0.3s ease'
          }}
        >
          👥 Student Points
        </button>
      </div>

      {activeTab === 'rewards' && (
        <div>
          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', marginBottom: '30px' }}>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              style={{
                padding: '12px 24px',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 'bold'
              }}
            >
              ➕ Add New Reward
            </button>
            
            {rewards.length === 0 && (
              <button
                onClick={initializeDefaultRewards}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
              >
                🎯 Initialize Default Rewards
              </button>
            )}
          </div>

          {/* Add/Edit Form */}
          {(showAddForm || editingReward) && (
            <div style={{
              background: 'rgba(255,255,255,0.05)',
              padding: '25px',
              borderRadius: '12px',
              marginBottom: '30px',
              border: '1px solid rgba(255,255,255,0.1)'
            }}>
              <h3 style={{
                fontSize: '20px',
                marginBottom: '20px',
                color: '#e5e7eb'
              }}>
                {editingReward ? 'Edit Reward' : 'Add New Reward'}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                <input
                  type="text"
                  placeholder="Reward Title"
                  value={editingReward ? editingReward.title : newReward.title}
                  onChange={(e) => editingReward 
                    ? setEditingReward({ ...editingReward, title: e.target.value })
                    : setNewReward({ ...newReward, title: e.target.value })
                  }
                  style={{
                    padding: '12px',
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '14px'
                  }}
                />

                <textarea
                  placeholder="Description"
                  value={editingReward ? editingReward.description : newReward.description}
                  onChange={(e) => editingReward
                    ? setEditingReward({ ...editingReward, description: e.target.value })
                    : setNewReward({ ...newReward, description: e.target.value })
                  }
                  rows={3}
                  style={{
                    padding: '12px',
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '14px',
                    resize: 'vertical'
                  }}
                />

                <input
                  type="number"
                  placeholder="Points Cost"
                  value={editingReward ? editingReward.points_cost : newReward.points_cost}
                  onChange={(e) => editingReward
                    ? setEditingReward({ ...editingReward, points_cost: e.target.value })
                    : setNewReward({ ...newReward, points_cost: e.target.value })
                  }
                  style={{
                    padding: '12px',
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '14px'
                  }}
                />

                <div style={{ display: 'flex', gap: '12px' }}>
                  <button
                    onClick={editingReward ? handleUpdateReward : handleAddReward}
                    style={{
                      padding: '12px 24px',
                      backgroundColor: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: 'bold'
                    }}
                  >
                    {editingReward ? '💾 Save Changes' : '➕ Add Reward'}
                  </button>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingReward(null);
                      setNewReward({ title: '', description: '', points_cost: '' });
                    }}
                    style={{
                      padding: '12px 24px',
                      backgroundColor: '#6b7280',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: 'bold'
                    }}
                  >
                    ❌ Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Rewards List */}
          {rewards.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '60px 20px',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '12px',
              color: '#94a3b8'
            }}>
              <div style={{ fontSize: '64px', marginBottom: '15px' }}>🎪</div>
              <p style={{ fontSize: '18px' }}>No rewards created yet!</p>
              <p style={{ fontSize: '14px', marginTop: '8px' }}>Click "Initialize Default Rewards" to get started</p>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '20px'
            }}>
              {rewards.map((reward) => (
                <div key={reward.id} style={{
                  background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%)',
                  border: '2px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '16px',
                  padding: '25px'
                }}>
                  <div style={{
                    fontSize: '48px',
                    textAlign: 'center',
                    marginBottom: '15px'
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
                    marginBottom: '15px',
                    textAlign: 'center',
                    minHeight: '40px'
                  }}>
                    {reward.description}
                  </p>

                  <div style={{
                    textAlign: 'center',
                    fontSize: '24px',
                    fontWeight: 'bold',
                    color: '#f59e0b',
                    marginBottom: '20px'
                  }}>
                    {reward.points_cost} Points
                  </div>

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={() => setEditingReward(reward)}
                      style={{
                        flex: 1,
                        padding: '10px',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}
                    >
                      ✏️ Edit
                    </button>
                    <button
                      onClick={() => handleDeleteReward(reward.id, reward.title)}
                      style={{
                        flex: 1,
                        padding: '10px',
                        backgroundColor: '#ef4444',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'students' && (
        <div>
          <h2 style={{
            fontSize: '24px',
            marginBottom: '20px',
            color: '#e5e7eb'
          }}>
            Student Points Overview
          </h2>

          {studentPoints.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '60px 20px',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '12px',
              color: '#94a3b8'
            }}>
              <div style={{ fontSize: '64px', marginBottom: '15px' }}>👥</div>
              <p style={{ fontSize: '18px' }}>No students found</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {studentPoints.map((studentData) => (
                <div key={studentData.student_id} style={{
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px',
                  padding: '20px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '15px'
                  }}>
                    <div>
                      <h4 style={{ fontSize: '18px', color: '#e5e7eb', marginBottom: '5px' }}>
                        {studentData.student_name}
                      </h4>
                      <p style={{ fontSize: '14px', color: '#94a3b8' }}>
                        @{studentData.username}
                      </p>
                    </div>

                    <div style={{
                      fontSize: '32px',
                      fontWeight: 'bold',
                      color: '#f59e0b'
                    }}>
                      {studentData.total_points} pts
                    </div>
                  </div>

                  {/* Points Adjustment Form */}
                  {adjustingStudent === studentData.student_id ? (
                    <div style={{
                      background: 'rgba(0,0,0,0.2)',
                      padding: '15px',
                      borderRadius: '8px',
                      marginTop: '15px'
                    }}>
                      <h5 style={{ fontSize: '16px', color: '#e5e7eb', marginBottom: '10px' }}>
                        Adjust Points
                      </h5>
                      <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                        <input
                          type="number"
                          placeholder="Points (use - for subtract)"
                          value={pointsAdjustment.points}
                          onChange={(e) => setPointsAdjustment({ ...pointsAdjustment, points: e.target.value })}
                          style={{
                            flex: 1,
                            padding: '10px',
                            backgroundColor: 'rgba(0,0,0,0.3)',
                            border: '1px solid rgba(255,255,255,0.2)',
                            borderRadius: '6px',
                            color: 'white',
                            fontSize: '14px'
                          }}
                        />
                        <input
                          type="text"
                          placeholder="Reason"
                          value={pointsAdjustment.description}
                          onChange={(e) => setPointsAdjustment({ ...pointsAdjustment, description: e.target.value })}
                          style={{
                            flex: 2,
                            padding: '10px',
                            backgroundColor: 'rgba(0,0,0,0.3)',
                            border: '1px solid rgba(255,255,255,0.2)',
                            borderRadius: '6px',
                            color: 'white',
                            fontSize: '14px'
                          }}
                        />
                      </div>
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                          onClick={handleAdjustPoints}
                          style={{
                            padding: '10px 20px',
                            backgroundColor: '#10b981',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: 'bold'
                          }}
                        >
                          ✅ Confirm
                        </button>
                        <button
                          onClick={() => {
                            setAdjustingStudent(null);
                            setPointsAdjustment({ points: '', description: '' });
                          }}
                          style={{
                            padding: '10px 20px',
                            backgroundColor: '#6b7280',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: 'bold'
                          }}
                        >
                          ❌ Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button
                        onClick={() => setAdjustingStudent(studentData.student_id)}
                        style={{
                          padding: '10px 20px',
                          backgroundColor: '#3b82f6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: 'bold'
                        }}
                      >
                        ➕➖ Adjust Points
                      </button>
                    </div>
                  )}

                  {/* Recent Transactions */}
                  {studentData.transactions && studentData.transactions.length > 0 && (
                    <details style={{ marginTop: '15px' }}>
                      <summary style={{
                        cursor: 'pointer',
                        color: '#94a3b8',
                        fontSize: '14px',
                        padding: '10px',
                        background: 'rgba(0,0,0,0.2)',
                        borderRadius: '6px'
                      }}>
                        📊 View Transaction History ({studentData.transactions.length})
                      </summary>
                      <div style={{
                        marginTop: '10px',
                        maxHeight: '200px',
                        overflowY: 'auto',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px'
                      }}>
                        {studentData.transactions.slice(0, 10).map((transaction) => (
                          <div key={transaction.id} style={{
                            padding: '10px',
                            background: 'rgba(0,0,0,0.2)',
                            borderRadius: '6px',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                          }}>
                            <div style={{ fontSize: '13px', color: '#e5e7eb' }}>
                              {transaction.description}
                            </div>
                            <div style={{
                              fontSize: '14px',
                              fontWeight: 'bold',
                              color: transaction.points > 0 ? '#10b981' : '#ef4444'
                            }}>
                              {transaction.points > 0 ? '+' : ''}{transaction.points}
                            </div>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RewardsManagement;

import React, { useState, useEffect } from 'react';

const SpellingWordLists = () => {
  const [wordLists, setWordLists] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingList, setEditingList] = useState(null);
  
  const [formData, setFormData] = useState({
    student_id: '',
    name: '',
    words: ['', '', '', '', '', '', '', '', '', '']
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const [wordListsRes, studentsRes] = await Promise.all([
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/spelling-word-lists`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/students`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);
      
      if (wordListsRes.ok && studentsRes.ok) {
        setWordLists(await wordListsRes.json());
        setStudents(await studentsRes.json());
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWordChange = (index, value) => {
    const newWords = [...formData.words];
    newWords[index] = value;
    setFormData({ ...formData, words: newWords });
  };

  const handleCreateWordList = async () => {
    if (!formData.student_id || !formData.name) {
      alert('Please select a student and enter a name');
      return;
    }

    const emptyWords = formData.words.filter(w => w.trim() === '');
    if (emptyWords.length > 0) {
      alert('Please fill in all 10 words');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/spelling-word-lists`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('Word list created successfully!');
        setShowCreateForm(false);
        setFormData({ student_id: '', name: '', words: ['', '', '', '', '', '', '', '', '', ''] });
        fetchData();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to create word list');
      }
    } catch (error) {
      console.error('Error creating word list:', error);
      alert('Error creating word list');
    }
  };

  const handleUpdateWordList = async () => {
    if (!formData.name) {
      alert('Please enter a name');
      return;
    }

    const emptyWords = formData.words.filter(w => w.trim() === '');
    if (emptyWords.length > 0) {
      alert('Please fill in all 10 words');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/spelling-word-lists/${editingList.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('Word list updated successfully!');
        setEditingList(null);
        setFormData({ student_id: '', name: '', words: ['', '', '', '', '', '', '', '', '', ''] });
        fetchData();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to update word list');
      }
    } catch (error) {
      console.error('Error updating word list:', error);
      alert('Error updating word list');
    }
  };

  const handleDeleteWordList = async (listId, listName) => {
    if (!window.confirm(`Are you sure you want to delete "${listName}"?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/spelling-word-lists/${listId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Word list deleted successfully!');
        fetchData();
      }
    } catch (error) {
      console.error('Error deleting word list:', error);
      alert('Error deleting word list');
    }
  };

  const startEdit = (list) => {
    setEditingList(list);
    setFormData({
      student_id: list.student_id,
      name: list.name,
      words: list.words
    });
    setShowCreateForm(false);
  };

  const cancelForm = () => {
    setShowCreateForm(false);
    setEditingList(null);
    setFormData({ student_id: '', name: '', words: ['', '', '', '', '', '', '', '', '', ''] });
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 'bold',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          color: 'transparent'
        }}>
          ✏️ Spelling Word Lists
        </h1>

        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
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
          ➕ Create New Word List
        </button>
      </div>

      {/* Create/Edit Form */}
      {(showCreateForm || editingList) && (
        <div style={{
          background: 'rgba(255,255,255,0.05)',
          padding: '30px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ fontSize: '20px', marginBottom: '20px', color: '#e5e7eb' }}>
            {editingList ? 'Edit Word List' : 'Create New Word List'}
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: '#94a3b8', fontSize: '14px' }}>
                Student *
              </label>
              <select
                value={formData.student_id}
                onChange={(e) => setFormData({ ...formData, student_id: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px',
                  backgroundColor: 'rgba(0,0,0,0.3)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px',
                  color: 'white',
                  fontSize: '14px'
                }}
              >
                <option value="">Select a student</option>
                {students.map(student => (
                  <option key={student.id} value={student.id}>
                    {student.first_name} {student.last_name} (@{student.username})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: '#94a3b8', fontSize: '14px' }}>
                Word List Name *
              </label>
              <input
                type="text"
                placeholder="e.g., Week 1 Words"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px',
                  backgroundColor: 'rgba(0,0,0,0.3)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px',
                  color: 'white',
                  fontSize: '14px'
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: '#94a3b8', fontSize: '14px' }}>
                10 Spelling Words *
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                {formData.words.map((word, index) => (
                  <input
                    key={index}
                    type="text"
                    placeholder={`Word ${index + 1}`}
                    value={word}
                    onChange={(e) => handleWordChange(index, e.target.value)}
                    style={{
                      padding: '12px',
                      backgroundColor: 'rgba(0,0,0,0.3)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                      color: 'white',
                      fontSize: '14px'
                    }}
                  />
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={editingList ? handleUpdateWordList : handleCreateWordList}
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
                {editingList ? '💾 Save Changes' : '➕ Create Word List'}
              </button>
              <button
                onClick={cancelForm}
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

      {/* Word Lists Display */}
      {wordLists.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          background: 'rgba(255,255,255,0.03)',
          borderRadius: '12px',
          color: '#94a3b8'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '15px' }}>📝</div>
          <p style={{ fontSize: '18px' }}>No word lists created yet!</p>
          <p style={{ fontSize: '14px', marginTop: '8px' }}>Click "Create New Word List" to get started</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {wordLists.map((list) => {
            const student = students.find(s => s.id === list.student_id);
            return (
              <div key={list.id} style={{
                background: list.active 
                  ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)'
                  : 'rgba(255,255,255,0.03)',
                border: list.active 
                  ? '2px solid rgba(16, 185, 129, 0.3)'
                  : '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                padding: '25px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
                  <div>
                    <h3 style={{ fontSize: '20px', color: '#e5e7eb', marginBottom: '8px', fontWeight: 'bold' }}>
                      {list.name}
                      {list.active && (
                        <span style={{
                          marginLeft: '12px',
                          padding: '4px 12px',
                          backgroundColor: 'rgba(16, 185, 129, 0.2)',
                          border: '1px solid rgba(16, 185, 129, 0.3)',
                          borderRadius: '6px',
                          fontSize: '12px',
                          fontWeight: 'normal'
                        }}>
                          ✓ Active
                        </span>
                      )}
                    </h3>
                    <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                      Student: {student ? `${student.first_name} ${student.last_name} (@${student.username})` : 'Unknown'}
                    </p>
                    <p style={{ color: '#94a3b8', fontSize: '12px', marginTop: '4px' }}>
                      Created: {new Date(list.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={() => startEdit(list)}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}
                    >
                      ✏️ Edit
                    </button>
                    <button
                      onClick={() => handleDeleteWordList(list.id, list.name)}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#ef4444',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>

                <div>
                  <h4 style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '12px', textTransform: 'uppercase' }}>
                    Words:
                  </h4>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(5, 1fr)',
                    gap: '10px'
                  }}>
                    {list.words.map((word, index) => (
                      <div key={index} style={{
                        padding: '10px',
                        backgroundColor: 'rgba(0,0,0,0.2)',
                        borderRadius: '8px',
                        textAlign: 'center',
                        fontSize: '14px',
                        color: '#e5e7eb',
                        fontWeight: '500'
                      }}>
                        {index + 1}. {word}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SpellingWordLists;

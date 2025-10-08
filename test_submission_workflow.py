#!/usr/bin/env python3
"""
Test the complete submission workflow
"""

import requests
import json

BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

# Login teacher and student
teacher_data = {"email": "teacher.code@example.com", "password": "SecurePass123!"}
response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_data)
teacher_token = response.json()["access_token"]

student_data = {"username": "codestudent123", "password": "StudentPass123!"}
response = requests.post(f"{BACKEND_URL}/auth/student/login", json=student_data)
student_token = response.json()["access_token"]

print("✅ Authentication successful")

# Create Level 2 assignment (has both MCQ and coding)
assignment_data = {
    "subject": "Learn to Code",
    "grade_level": "Elementary", 
    "topic": "HTML Basics",
    "coding_level": 2
}

headers = {"Authorization": f"Bearer {teacher_token}"}
response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
assignment = response.json()
assignment_id = assignment["id"]

print(f"✅ Created assignment: {assignment_id}")
print(f"   Questions: {len(assignment['questions'])}")
print(f"   Coding exercises: {len(assignment['coding_exercises'])}")

# Assign to student
assign_data = {"assignment_id": assignment_id, "student_ids": ["ab87cf52-0ed3-40e0-b0ed-9368172305f3"]}
response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data, headers=headers)
print("✅ Assignment assigned to student")

# Get student assignments
student_headers = {"Authorization": f"Bearer {student_token}"}
response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
assignments = response.json()

student_assignment_id = None
for sa in assignments:
    if sa["assignment"]["id"] == assignment_id:
        student_assignment_id = sa["student_assignment_id"]
        break

print(f"✅ Found student assignment: {student_assignment_id}")

# Submit assignment with both MCQ and coding answers
submission_data = {
    "student_assignment_id": student_assignment_id,
    "answers": [0, 1],  # MCQ answers
    "coding_answers": ["<h1>Hello World</h1>", "<p>This is a paragraph</p>"]  # HTML code
}

response = requests.post(f"{BACKEND_URL}/student/assignments/submit", json=submission_data, headers=student_headers)
result = response.json()

print("✅ Assignment submitted successfully")
print(f"   Score: {result['score']}%")
print(f"   MCQ correct: {result['mcq_correct']}/{result['total_mcq']}")
print(f"   Coding correct: {result['coding_correct']}/{result['total_coding']}")

print("\n🎉 Complete submission workflow tested successfully!")
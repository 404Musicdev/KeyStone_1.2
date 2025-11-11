#!/usr/bin/env python3
"""
Debug Assignment Scoring Test
"""

import requests
import json

BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

def debug_assignment_scoring():
    # Login as teacher
    teacher_credentials = {
        "email": "testteacher@example.com",
        "password": "TestPass123!"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_credentials)
    if response.status_code != 200:
        print("Failed to login as teacher")
        return
        
    teacher_data = response.json()
    teacher_token = teacher_data["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Create a simple Math assignment
    assignment_data = {
        "subject": "Math",
        "grade_level": "5th Grade",
        "topic": "Basic Addition"
    }
    
    response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=teacher_headers)
    if response.status_code != 200:
        print("Failed to create assignment")
        return
        
    assignment = response.json()
    print(f"Created assignment: {assignment['id']}")
    print(f"Number of questions: {len(assignment['questions'])}")
    
    # Print all questions and their correct answers
    for i, question in enumerate(assignment['questions']):
        print(f"\nQuestion {i+1}: {question['question']}")
        print(f"Options: {question['options']}")
        print(f"Correct answer index: {question['correct_answer']}")
        
    # Find teststudent
    response = requests.get(f"{BACKEND_URL}/students", headers=teacher_headers)
    students = response.json()
    teststudent_id = None
    for student in students:
        if student["username"] == "teststudent":
            teststudent_id = student["id"]
            break
            
    if not teststudent_id:
        print("teststudent not found")
        return
        
    # Assign to teststudent
    assign_data = {
        "assignment_id": assignment["id"],
        "student_ids": [teststudent_id]
    }
    
    response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data, headers=teacher_headers)
    if response.status_code != 200:
        print("Failed to assign")
        return
        
    # Login as student
    student_credentials = {
        "username": "teststudent",
        "password": "testpass"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/student/login", json=student_credentials)
    if response.status_code != 200:
        print("Failed to login as student")
        return
        
    student_data = response.json()
    student_token = student_data["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Get student assignments
    response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
    assignments = response.json()
    
    student_assignment_id = None
    for sa in assignments:
        if sa["assignment"]["id"] == assignment["id"] and not sa["completed"]:
            student_assignment_id = sa["student_assignment_id"]
            break
            
    if not student_assignment_id:
        print("Student assignment not found")
        return
        
    # Test 1: Submit all correct answers
    correct_answers = [q["correct_answer"] for q in assignment["questions"]]
    print(f"\nSubmitting all correct answers: {correct_answers}")
    
    submission_data = {
        "student_assignment_id": student_assignment_id,
        "answers": correct_answers
    }
    
    response = requests.post(f"{BACKEND_URL}/student/assignments/submit", json=submission_data, headers=student_headers)
    if response.status_code == 200:
        result = response.json()
        print(f"Score with all correct answers: {result.get('score', 0)}%")
        print(f"MCQ correct: {result.get('mcq_correct', 0)}/{result.get('total_mcq', 0)}")
        print(f"Total questions: {result.get('total_questions', 0)}")
    else:
        print(f"Submission failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    debug_assignment_scoring()
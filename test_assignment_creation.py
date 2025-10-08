#!/usr/bin/env python3
"""
Test script to create a specific Learn to Code assignment for student testing
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

def log_test(test_name, success, details=""):
    """Log test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

def create_learn_to_code_assignment():
    """
    Create a test "Learn to Code" assignment for the student to test assignment clicking functionality
    Following the exact requirements from the review request
    """
    print("\n=== Creating Learn to Code Assignment for Student Testing ===")
    
    # Step 1: Login as teacher (testteacher@example.com / TestPass123!)
    teacher_credentials = {
        "email": "testteacher@example.com",
        "password": "TestPass123!"
    }
    
    teacher_token = None
    teacher_id = None
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_credentials)
        if response.status_code == 200:
            data = response.json()
            teacher_token = data["access_token"]
            teacher_id = data["user"]["id"]
            log_test("Teacher Login (testteacher@example.com)", True, f"Teacher ID: {teacher_id}")
        else:
            log_test("Teacher Login (testteacher@example.com)", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        log_test("Teacher Login (testteacher@example.com)", False, f"Exception: {str(e)}")
        return None
        
    # Step 2: Generate a Learn to Code assignment with specific parameters
    assignment_data = {
        "subject": "Learn to Code",
        "grade_level": "5th Grade",
        "topic": "Introduction to Programming",
        "coding_level": 1  # Programming concepts
    }
    
    assignment_id = None
    assignment_details = None
    
    try:
        headers = {"Authorization": f"Bearer {teacher_token}"}
        response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
        
        if response.status_code == 200:
            assignment_details = response.json()
            assignment_id = assignment_details["id"]
            
            log_test("Learn to Code Assignment Generation", True, f"Assignment ID: {assignment_id}")
            
            # Verify assignment structure
            if assignment_details.get("subject") == "Learn to Code":
                log_test("Assignment Subject Verification", True, "Subject correctly set to 'Learn to Code'")
            else:
                log_test("Assignment Subject Verification", False, f"Expected 'Learn to Code', got '{assignment_details.get('subject')}'")
                
            if assignment_details.get("coding_level") == 1:
                log_test("Assignment Coding Level Verification", True, "Coding level correctly set to 1")
            else:
                log_test("Assignment Coding Level Verification", False, f"Expected 1, got {assignment_details.get('coding_level')}")
                
            if assignment_details.get("grade_level") == "5th Grade":
                log_test("Assignment Grade Level Verification", True, "Grade level correctly set to '5th Grade'")
            else:
                log_test("Assignment Grade Level Verification", False, f"Expected '5th Grade', got '{assignment_details.get('grade_level')}'")
                
            if assignment_details.get("topic") == "Introduction to Programming":
                log_test("Assignment Topic Verification", True, "Topic correctly set to 'Introduction to Programming'")
            else:
                log_test("Assignment Topic Verification", False, f"Expected 'Introduction to Programming', got '{assignment_details.get('topic')}'")
                
            # Verify it has MCQ questions (Level 1 should be MCQ only)
            questions = assignment_details.get("questions", [])
            if len(questions) > 0:
                log_test("Assignment MCQ Questions", True, f"Generated {len(questions)} MCQ questions")
            else:
                log_test("Assignment MCQ Questions", False, "No MCQ questions found")
                
            # Verify no coding exercises for Level 1
            coding_exercises = assignment_details.get("coding_exercises", [])
            if len(coding_exercises) == 0:
                log_test("Assignment No Coding Exercises", True, "Level 1 correctly has no coding exercises")
            else:
                log_test("Assignment No Coding Exercises", False, f"Level 1 should have no coding exercises, found {len(coding_exercises)}")
                
        else:
            log_test("Learn to Code Assignment Generation", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Learn to Code Assignment Generation", False, f"Exception: {str(e)}")
        return None
        
    # Step 3: Find the student "teststudent" in the database
    teststudent_id = None
    
    try:
        headers = {"Authorization": f"Bearer {teacher_token}"}
        response = requests.get(f"{BACKEND_URL}/students", headers=headers)
        
        if response.status_code == 200:
            students = response.json()
            for student in students:
                if student["username"] == "teststudent":
                    teststudent_id = student["id"]
                    log_test("Find Student 'teststudent'", True, f"Student ID: {teststudent_id}")
                    break
                    
            if not teststudent_id:
                log_test("Find Student 'teststudent'", False, "Student 'teststudent' not found in database")
                return None
                
        else:
            log_test("Find Student 'teststudent'", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Find Student 'teststudent'", False, f"Exception: {str(e)}")
        return None
        
    # Step 4: Assign the assignment to student "teststudent"
    student_assignment_id = None
    
    try:
        assign_data = {
            "assignment_id": assignment_id,
            "student_ids": [teststudent_id]
        }
        
        headers = {"Authorization": f"Bearer {teacher_token}"}
        response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data, headers=headers)
        
        if response.status_code == 200:
            log_test("Assign Assignment to teststudent", True, "Assignment successfully assigned")
            
            # Verify student_assignment record exists
            # Login as teststudent to check assignments
            student_credentials = {
                "username": "teststudent",
                "password": "testpass"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/student/login", json=student_credentials)
            if response.status_code == 200:
                student_data = response.json()
                student_token = student_data["access_token"]
                
                # Get student assignments
                student_headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
                
                if response.status_code == 200:
                    assignments = response.json()
                    
                    # Find our assignment
                    found_assignment = None
                    for assignment in assignments:
                        if assignment["assignment"]["id"] == assignment_id:
                            found_assignment = assignment
                            student_assignment_id = assignment["student_assignment_id"]
                            break
                            
                    if found_assignment:
                        log_test("Verify Student Assignment Record", True, f"Student assignment ID: {student_assignment_id}")
                        
                        # Verify assignment appears in student's list
                        assignment_in_list = found_assignment["assignment"]
                        if (assignment_in_list.get("subject") == "Learn to Code" and 
                            assignment_in_list.get("coding_level") == 1 and
                            assignment_in_list.get("topic") == "Introduction to Programming"):
                            log_test("Assignment Visible to Student", True, "Assignment correctly appears in student's assignments list")
                        else:
                            log_test("Assignment Visible to Student", False, "Assignment data mismatch in student's list")
                            
                    else:
                        log_test("Verify Student Assignment Record", False, "Assignment not found in student's assignments list")
                        
                else:
                    log_test("Get Student Assignments", False, f"Status: {response.status_code}, Response: {response.text}")
                    
            else:
                log_test("Student Login for Verification", False, f"Status: {response.status_code}, Response: {response.text}")
                
        else:
            log_test("Assign Assignment to teststudent", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Assign Assignment to teststudent", False, f"Exception: {str(e)}")
        return None
        
    # Return assignment details for the user
    result = {
        "assignment_id": assignment_id,
        "student_assignment_id": student_assignment_id,
        "assignment_details": assignment_details,
        "student_id": teststudent_id,
        "teacher_id": teacher_id
    }
    
    print(f"\n📋 ASSIGNMENT CREATED SUCCESSFULLY:")
    print(f"   Assignment ID: {assignment_id}")
    print(f"   Student Assignment ID: {student_assignment_id}")
    print(f"   Subject: {assignment_details.get('subject')}")
    print(f"   Grade Level: {assignment_details.get('grade_level')}")
    print(f"   Topic: {assignment_details.get('topic')}")
    print(f"   Coding Level: {assignment_details.get('coding_level')}")
    print(f"   Number of Questions: {len(assignment_details.get('questions', []))}")
    print(f"   Assigned to Student: teststudent (ID: {teststudent_id})")
    
    # Show sample questions
    questions = assignment_details.get('questions', [])
    if questions:
        print(f"\n📝 SAMPLE QUESTIONS:")
        for i, question in enumerate(questions[:3]):  # Show first 3 questions
            print(f"   Question {i+1}: {question.get('question', 'N/A')}")
            options = question.get('options', [])
            for j, option in enumerate(options):
                print(f"      {chr(65+j)}. {option}")
            print(f"      Correct Answer: {chr(65 + question.get('correct_answer', 0))}")
            print()
    
    return result

if __name__ == "__main__":
    print("🚀 Creating Learn to Code Assignment for Student Testing")
    print(f"Backend URL: {BACKEND_URL}")
    
    result = create_learn_to_code_assignment()
    
    if result:
        print("\n✅ SUCCESS: Learn to Code assignment created and assigned to teststudent")
        print("The student can now log in and see this assignment in their assignments list.")
    else:
        print("\n❌ FAILED: Could not create or assign the Learn to Code assignment")
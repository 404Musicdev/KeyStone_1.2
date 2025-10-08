#!/usr/bin/env python3
"""
Backend Test Suite for Learn to Code Functionality
Tests the new "Learn to Code" subject with 4 coding levels
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://homeschool-ai.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.teacher_token = None
        self.student_token = None
        self.teacher_id = None
        self.student_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def setup_authentication(self):
        """Setup teacher and student accounts for testing"""
        print("\n=== Setting up Authentication ===")
        
        # Register teacher
        teacher_data = {
            "email": "teacher.code@example.com",
            "password": "SecurePass123!",
            "first_name": "Code",
            "last_name": "Teacher",
            "role": "teacher"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/teacher/register", json=teacher_data)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data["access_token"]
                self.teacher_id = data["user"]["id"]
                self.log_test("Teacher Registration", True, f"Teacher ID: {self.teacher_id}")
            elif response.status_code == 400 and "already registered" in response.text:
                # Try login instead
                login_data = {"email": teacher_data["email"], "password": teacher_data["password"]}
                response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.teacher_token = data["access_token"]
                    self.teacher_id = data["user"]["id"]
                    self.log_test("Teacher Login", True, f"Teacher ID: {self.teacher_id}")
                else:
                    self.log_test("Teacher Authentication", False, f"Login failed: {response.text}")
                    return False
            else:
                self.log_test("Teacher Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Teacher Authentication", False, f"Exception: {str(e)}")
            return False
            
        # Create student
        student_data = {
            "first_name": "Code",
            "last_name": "Student",
            "username": "codestudent123",
            "password": "StudentPass123!"
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{BACKEND_URL}/students", json=student_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.student_id = data["id"]
                self.log_test("Student Creation", True, f"Student ID: {self.student_id}")
            elif response.status_code == 400 and "already exists" in response.text:
                # Get existing student
                response = requests.get(f"{BACKEND_URL}/students", headers=headers)
                if response.status_code == 200:
                    students = response.json()
                    for student in students:
                        if student["username"] == student_data["username"]:
                            self.student_id = student["id"]
                            self.log_test("Student Found", True, f"Student ID: {self.student_id}")
                            break
            else:
                self.log_test("Student Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Student Creation", False, f"Exception: {str(e)}")
            return False
            
        # Login student
        try:
            login_data = {"username": student_data["username"], "password": student_data["password"]}
            response = requests.post(f"{BACKEND_URL}/auth/student/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.log_test("Student Login", True, "Student authenticated successfully")
            else:
                self.log_test("Student Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Student Login", False, f"Exception: {str(e)}")
            return False
            
        return True
        
    def test_learn_to_code_level_1(self):
        """Test Learn to Code Level 1 - Programming Concepts (MCQ only)"""
        print("\n=== Testing Learn to Code Level 1 ===")
        
        assignment_data = {
            "subject": "Learn to Code",
            "grade_level": "Elementary",
            "topic": "Introduction to Programming",
            "coding_level": 1
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify assignment structure
                if data.get("subject") == "Learn to Code":
                    self.log_test("Level 1 Subject", True, "Subject correctly set to 'Learn to Code'")
                else:
                    self.log_test("Level 1 Subject", False, f"Expected 'Learn to Code', got '{data.get('subject')}'")
                    
                if data.get("coding_level") == 1:
                    self.log_test("Level 1 Coding Level", True, "Coding level correctly set to 1")
                else:
                    self.log_test("Level 1 Coding Level", False, f"Expected 1, got {data.get('coding_level')}")
                    
                # Verify questions exist
                questions = data.get("questions", [])
                if len(questions) >= 4:
                    self.log_test("Level 1 Questions Count", True, f"Generated {len(questions)} questions")
                else:
                    self.log_test("Level 1 Questions Count", False, f"Expected at least 4 questions, got {len(questions)}")
                    
                # Verify no coding exercises for Level 1
                coding_exercises = data.get("coding_exercises", [])
                if len(coding_exercises) == 0:
                    self.log_test("Level 1 No Coding Exercises", True, "Level 1 correctly has no coding exercises")
                else:
                    self.log_test("Level 1 No Coding Exercises", False, f"Level 1 should have no coding exercises, found {len(coding_exercises)}")
                    
                # Verify question structure
                if questions:
                    first_question = questions[0]
                    if all(key in first_question for key in ["question", "options", "correct_answer"]):
                        self.log_test("Level 1 Question Structure", True, "Questions have correct structure")
                    else:
                        self.log_test("Level 1 Question Structure", False, "Questions missing required fields")
                        
                return data.get("id")
            else:
                self.log_test("Level 1 Assignment Generation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Level 1 Assignment Generation", False, f"Exception: {str(e)}")
            return None
            
    def test_learn_to_code_level_2(self):
        """Test Learn to Code Level 2 - HTML Fundamentals (code + MCQ)"""
        print("\n=== Testing Learn to Code Level 2 ===")
        
        assignment_data = {
            "subject": "Learn to Code",
            "grade_level": "Elementary",
            "topic": "HTML Basics",
            "coding_level": 2
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify coding level
                if data.get("coding_level") == 2:
                    self.log_test("Level 2 Coding Level", True, "Coding level correctly set to 2")
                else:
                    self.log_test("Level 2 Coding Level", False, f"Expected 2, got {data.get('coding_level')}")
                    
                # Verify both questions and coding exercises exist
                questions = data.get("questions", [])
                coding_exercises = data.get("coding_exercises", [])
                
                if len(questions) >= 2:
                    self.log_test("Level 2 MCQ Questions", True, f"Generated {len(questions)} MCQ questions")
                else:
                    self.log_test("Level 2 MCQ Questions", False, f"Expected at least 2 MCQ questions, got {len(questions)}")
                    
                if len(coding_exercises) >= 1:
                    self.log_test("Level 2 Coding Exercises", True, f"Generated {len(coding_exercises)} coding exercises")
                else:
                    self.log_test("Level 2 Coding Exercises", False, f"Expected at least 1 coding exercise, got {len(coding_exercises)}")
                    
                # Verify HTML coding exercise structure
                if coding_exercises:
                    first_exercise = coding_exercises[0]
                    if first_exercise.get("language") == "html":
                        self.log_test("Level 2 HTML Language", True, "Coding exercise language is HTML")
                    else:
                        self.log_test("Level 2 HTML Language", False, f"Expected 'html', got '{first_exercise.get('language')}'")
                        
                    required_fields = ["prompt", "language", "starter_code", "correct_answer"]
                    if all(field in first_exercise for field in required_fields):
                        self.log_test("Level 2 Exercise Structure", True, "Coding exercise has all required fields")
                    else:
                        missing = [f for f in required_fields if f not in first_exercise]
                        self.log_test("Level 2 Exercise Structure", False, f"Missing fields: {missing}")
                        
                return data.get("id")
            else:
                self.log_test("Level 2 Assignment Generation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Level 2 Assignment Generation", False, f"Exception: {str(e)}")
            return None
            
    def test_learn_to_code_level_3(self):
        """Test Learn to Code Level 3 - JavaScript Basics (code + MCQ)"""
        print("\n=== Testing Learn to Code Level 3 ===")
        
        assignment_data = {
            "subject": "Learn to Code",
            "grade_level": "Middle School",
            "topic": "JavaScript Fundamentals",
            "coding_level": 3
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify coding level
                if data.get("coding_level") == 3:
                    self.log_test("Level 3 Coding Level", True, "Coding level correctly set to 3")
                else:
                    self.log_test("Level 3 Coding Level", False, f"Expected 3, got {data.get('coding_level')}")
                    
                # Verify JavaScript coding exercises
                coding_exercises = data.get("coding_exercises", [])
                if coding_exercises:
                    first_exercise = coding_exercises[0]
                    if first_exercise.get("language") == "javascript":
                        self.log_test("Level 3 JavaScript Language", True, "Coding exercise language is JavaScript")
                    else:
                        self.log_test("Level 3 JavaScript Language", False, f"Expected 'javascript', got '{first_exercise.get('language')}'")
                else:
                    self.log_test("Level 3 Coding Exercises", False, "No coding exercises found for Level 3")
                    
                return data.get("id")
            else:
                self.log_test("Level 3 Assignment Generation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Level 3 Assignment Generation", False, f"Exception: {str(e)}")
            return None
            
    def test_learn_to_code_level_4(self):
        """Test Learn to Code Level 4 - Python Backend (code + MCQ)"""
        print("\n=== Testing Learn to Code Level 4 ===")
        
        assignment_data = {
            "subject": "Learn to Code",
            "grade_level": "High School",
            "topic": "Python Backend Development",
            "coding_level": 4
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify coding level
                if data.get("coding_level") == 4:
                    self.log_test("Level 4 Coding Level", True, "Coding level correctly set to 4")
                else:
                    self.log_test("Level 4 Coding Level", False, f"Expected 4, got {data.get('coding_level')}")
                    
                # Verify Python coding exercises
                coding_exercises = data.get("coding_exercises", [])
                if coding_exercises:
                    first_exercise = coding_exercises[0]
                    if first_exercise.get("language") == "python":
                        self.log_test("Level 4 Python Language", True, "Coding exercise language is Python")
                    else:
                        self.log_test("Level 4 Python Language", False, f"Expected 'python', got '{first_exercise.get('language')}'")
                else:
                    self.log_test("Level 4 Coding Exercises", False, "No coding exercises found for Level 4")
                    
                return data.get("id")
            else:
                self.log_test("Level 4 Assignment Generation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Level 4 Assignment Generation", False, f"Exception: {str(e)}")
            return None
            
    def test_assignment_submission(self, assignment_id):
        """Test assignment submission with both MCQ and coding answers"""
        print("\n=== Testing Assignment Submission ===")
        
        if not assignment_id:
            self.log_test("Assignment Submission Setup", False, "No assignment ID provided")
            return
            
        try:
            # First assign the assignment to the student
            assign_data = {
                "assignment_id": assignment_id,
                "student_ids": [self.student_id]
            }
            
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data, headers=headers)
            
            if response.status_code != 200:
                self.log_test("Assignment Assignment", False, f"Failed to assign: {response.text}")
                return
                
            self.log_test("Assignment Assignment", True, "Assignment successfully assigned to student")
            
            # Get student assignments to find the student_assignment_id
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
            
            if response.status_code != 200:
                self.log_test("Get Student Assignments", False, f"Failed to get assignments: {response.text}")
                return
                
            assignments = response.json()
            student_assignment_id = None
            assignment_details = None
            
            for assignment in assignments:
                if assignment["assignment"]["id"] == assignment_id:
                    student_assignment_id = assignment["student_assignment_id"]
                    assignment_details = assignment["assignment"]
                    break
                    
            if not student_assignment_id:
                self.log_test("Find Student Assignment", False, "Could not find student assignment")
                return
                
            self.log_test("Find Student Assignment", True, f"Found student assignment: {student_assignment_id}")
            
            # Prepare submission data
            mcq_answers = [0] * len(assignment_details.get("questions", []))  # Answer all as option 0
            coding_answers = []
            
            # Add coding answers if there are coding exercises
            coding_exercises = assignment_details.get("coding_exercises", [])
            for exercise in coding_exercises:
                # Use a simple test answer
                if exercise.get("language") == "html":
                    coding_answers.append("<h1>Test</h1>")
                elif exercise.get("language") == "javascript":
                    coding_answers.append("console.log('test');")
                elif exercise.get("language") == "python":
                    coding_answers.append("print('test')")
                    
            submission_data = {
                "student_assignment_id": student_assignment_id,
                "answers": mcq_answers if mcq_answers else None,
                "coding_answers": coding_answers if coding_answers else None
            }
            
            # Submit the assignment
            response = requests.post(f"{BACKEND_URL}/student/assignments/submit", json=submission_data, headers=student_headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Assignment Submission", True, f"Score: {data.get('score', 0)}%")
                
                # Verify submission response structure
                expected_fields = ["message", "score", "mcq_correct", "total_mcq", "total_questions"]
                if all(field in data for field in expected_fields):
                    self.log_test("Submission Response Structure", True, "All expected fields present")
                else:
                    missing = [f for f in expected_fields if f not in data]
                    self.log_test("Submission Response Structure", False, f"Missing fields: {missing}")
                    
                # Verify coding answers handling
                if coding_answers and "coding_correct" in data and "total_coding" in data:
                    self.log_test("Coding Answers Handling", True, f"Coding correct: {data['coding_correct']}/{data['total_coding']}")
                elif not coding_answers:
                    self.log_test("Coding Answers Handling", True, "No coding exercises to handle")
                else:
                    self.log_test("Coding Answers Handling", False, "Coding answers not properly handled in response")
                    
            else:
                self.log_test("Assignment Submission", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Assignment Submission", False, f"Exception: {str(e)}")
            
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n=== Testing Edge Cases ===")
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        # Test missing coding_level for Learn to Code
        assignment_data = {
            "subject": "Learn to Code",
            "grade_level": "Elementary",
            "topic": "Programming Basics"
            # Missing coding_level
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Should still work, might default to basic questions
                self.log_test("Missing Coding Level", True, "Assignment generated without coding_level")
            else:
                self.log_test("Missing Coding Level", False, f"Failed: {response.text}")
        except Exception as e:
            self.log_test("Missing Coding Level", False, f"Exception: {str(e)}")
            
        # Test invalid coding level
        assignment_data = {
            "subject": "Learn to Code",
            "grade_level": "Elementary",
            "topic": "Programming Basics",
            "coding_level": 99  # Invalid level
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Invalid Coding Level", True, "Assignment generated with invalid coding_level (fallback worked)")
            else:
                self.log_test("Invalid Coding Level", False, f"Failed: {response.text}")
        except Exception as e:
            self.log_test("Invalid Coding Level", False, f"Exception: {str(e)}")
            
        # Test other subjects still work normally
        assignment_data = {
            "subject": "Math",
            "grade_level": "Elementary",
            "topic": "Addition and Subtraction"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("subject") == "Math" and not data.get("coding_exercises"):
                    self.log_test("Other Subjects Normal", True, "Math subject works normally without coding features")
                else:
                    self.log_test("Other Subjects Normal", False, "Math subject has unexpected coding features")
            else:
                self.log_test("Other Subjects Normal", False, f"Failed: {response.text}")
        except Exception as e:
            self.log_test("Other Subjects Normal", False, f"Exception: {str(e)}")
            
    def create_test_accounts_for_student_login(self):
        """Create specific test accounts to resolve student login black screen issue"""
        print("\n=== Creating Test Accounts for Student Login Fix ===")
        
        # 1. Create Teacher Account
        teacher_data = {
            "email": "testteacher@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "Teacher",
            "role": "teacher"
        }
        
        teacher_token = None
        try:
            response = requests.post(f"{BACKEND_URL}/auth/teacher/register", json=teacher_data)
            if response.status_code == 200:
                data = response.json()
                teacher_token = data["access_token"]
                teacher_id = data["user"]["id"]
                self.log_test("Test Teacher Account Creation", True, f"Teacher ID: {teacher_id}")
            elif response.status_code == 400 and "already registered" in response.text:
                # Try login instead
                login_data = {"email": teacher_data["email"], "password": teacher_data["password"]}
                response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    teacher_token = data["access_token"]
                    teacher_id = data["user"]["id"]
                    self.log_test("Test Teacher Account Login", True, f"Teacher ID: {teacher_id}")
                else:
                    self.log_test("Test Teacher Account", False, f"Login failed: {response.text}")
                    return False
            else:
                self.log_test("Test Teacher Account Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Test Teacher Account", False, f"Exception: {str(e)}")
            return False
            
        # 2. Create Student Accounts via Teacher
        students_data = [
            {
                "first_name": "John",
                "last_name": "Student", 
                "username": "johnstudent",
                "password": "student123"
            },
            {
                "first_name": "Jane",
                "last_name": "Student",
                "username": "janestudent", 
                "password": "student123"
            },
            {
                "first_name": "Test",
                "last_name": "Student",
                "username": "teststudent",
                "password": "testpass"
            }
        ]
        
        headers = {"Authorization": f"Bearer {teacher_token}"}
        created_students = []
        
        for student_data in students_data:
            try:
                response = requests.post(f"{BACKEND_URL}/students", json=student_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    created_students.append({
                        "id": data["id"],
                        "username": student_data["username"],
                        "password": student_data["password"]
                    })
                    self.log_test(f"Student Creation - {student_data['username']}", True, f"Student ID: {data['id']}")
                elif response.status_code == 400 and "already exists" in response.text:
                    # Student already exists, get their ID
                    response = requests.get(f"{BACKEND_URL}/students", headers=headers)
                    if response.status_code == 200:
                        students = response.json()
                        for student in students:
                            if student["username"] == student_data["username"]:
                                created_students.append({
                                    "id": student["id"],
                                    "username": student_data["username"],
                                    "password": student_data["password"]
                                })
                                self.log_test(f"Student Found - {student_data['username']}", True, f"Student ID: {student['id']}")
                                break
                else:
                    self.log_test(f"Student Creation - {student_data['username']}", False, f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test(f"Student Creation - {student_data['username']}", False, f"Exception: {str(e)}")
                
        # 3. Verify Student Login for each created student
        for student in created_students:
            try:
                login_data = {
                    "username": student["username"],
                    "password": student["password"]
                }
                response = requests.post(f"{BACKEND_URL}/auth/student/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Student Login - {student['username']}", True, f"Login successful, token received")
                    
                    # Verify student data is returned correctly
                    user_data = data.get("user", {})
                    if user_data.get("username") == student["username"]:
                        self.log_test(f"Student Data Verification - {student['username']}", True, "Student data returned correctly")
                    else:
                        self.log_test(f"Student Data Verification - {student['username']}", False, "Student data mismatch")
                        
                else:
                    self.log_test(f"Student Login - {student['username']}", False, f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test(f"Student Login - {student['username']}", False, f"Exception: {str(e)}")
                
        return len(created_students) > 0
        
    def test_student_authentication_workflow(self):
        """Test complete student authentication workflow to prevent black screen"""
        print("\n=== Testing Student Authentication Workflow ===")
        
        # Test with the created test student
        test_credentials = {
            "username": "johnstudent",
            "password": "student123"
        }
        
        try:
            # 1. Test student login
            response = requests.post(f"{BACKEND_URL}/auth/student/login", json=test_credentials)
            if response.status_code == 200:
                data = response.json()
                student_token = data["access_token"]
                student_data = data["user"]
                self.log_test("Student Authentication Workflow - Login", True, f"Student: {student_data.get('first_name')} {student_data.get('last_name')}")
                
                # 2. Test accessing student assignments (this is what causes black screen if auth fails)
                headers = {"Authorization": f"Bearer {student_token}"}
                response = requests.get(f"{BACKEND_URL}/student/assignments", headers=headers)
                if response.status_code == 200:
                    assignments = response.json()
                    self.log_test("Student Authentication Workflow - Assignments Access", True, f"Retrieved {len(assignments)} assignments")
                else:
                    self.log_test("Student Authentication Workflow - Assignments Access", False, f"Status: {response.status_code}, Response: {response.text}")
                    
                # 3. Test token validation by making another authenticated request
                response = requests.get(f"{BACKEND_URL}/health", headers=headers)
                if response.status_code == 200:
                    self.log_test("Student Authentication Workflow - Token Validation", True, "Token remains valid for subsequent requests")
                else:
                    self.log_test("Student Authentication Workflow - Token Validation", False, f"Token validation failed: {response.text}")
                    
            else:
                self.log_test("Student Authentication Workflow - Login", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Student Authentication Workflow", False, f"Exception: {str(e)}")

    def test_learn_to_code_assignment_for_student_clicking(self):
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
                self.log_test("Teacher Login (testteacher@example.com)", True, f"Teacher ID: {teacher_id}")
            else:
                self.log_test("Teacher Login (testteacher@example.com)", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test("Teacher Login (testteacher@example.com)", False, f"Exception: {str(e)}")
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
                
                self.log_test("Learn to Code Assignment Generation", True, f"Assignment ID: {assignment_id}")
                
                # Verify assignment structure
                if assignment_details.get("subject") == "Learn to Code":
                    self.log_test("Assignment Subject Verification", True, "Subject correctly set to 'Learn to Code'")
                else:
                    self.log_test("Assignment Subject Verification", False, f"Expected 'Learn to Code', got '{assignment_details.get('subject')}'")
                    
                if assignment_details.get("coding_level") == 1:
                    self.log_test("Assignment Coding Level Verification", True, "Coding level correctly set to 1")
                else:
                    self.log_test("Assignment Coding Level Verification", False, f"Expected 1, got {assignment_details.get('coding_level')}")
                    
                if assignment_details.get("grade_level") == "5th Grade":
                    self.log_test("Assignment Grade Level Verification", True, "Grade level correctly set to '5th Grade'")
                else:
                    self.log_test("Assignment Grade Level Verification", False, f"Expected '5th Grade', got '{assignment_details.get('grade_level')}'")
                    
                if assignment_details.get("topic") == "Introduction to Programming":
                    self.log_test("Assignment Topic Verification", True, "Topic correctly set to 'Introduction to Programming'")
                else:
                    self.log_test("Assignment Topic Verification", False, f"Expected 'Introduction to Programming', got '{assignment_details.get('topic')}'")
                    
                # Verify it has MCQ questions (Level 1 should be MCQ only)
                questions = assignment_details.get("questions", [])
                if len(questions) > 0:
                    self.log_test("Assignment MCQ Questions", True, f"Generated {len(questions)} MCQ questions")
                else:
                    self.log_test("Assignment MCQ Questions", False, "No MCQ questions found")
                    
                # Verify no coding exercises for Level 1
                coding_exercises = assignment_details.get("coding_exercises", [])
                if len(coding_exercises) == 0:
                    self.log_test("Assignment No Coding Exercises", True, "Level 1 correctly has no coding exercises")
                else:
                    self.log_test("Assignment No Coding Exercises", False, f"Level 1 should have no coding exercises, found {len(coding_exercises)}")
                    
            else:
                self.log_test("Learn to Code Assignment Generation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Learn to Code Assignment Generation", False, f"Exception: {str(e)}")
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
                        self.log_test("Find Student 'teststudent'", True, f"Student ID: {teststudent_id}")
                        break
                        
                if not teststudent_id:
                    self.log_test("Find Student 'teststudent'", False, "Student 'teststudent' not found in database")
                    return None
                    
            else:
                self.log_test("Find Student 'teststudent'", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Find Student 'teststudent'", False, f"Exception: {str(e)}")
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
                self.log_test("Assign Assignment to teststudent", True, "Assignment successfully assigned")
                
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
                            self.log_test("Verify Student Assignment Record", True, f"Student assignment ID: {student_assignment_id}")
                            
                            # Verify assignment appears in student's list
                            assignment_in_list = found_assignment["assignment"]
                            if (assignment_in_list.get("subject") == "Learn to Code" and 
                                assignment_in_list.get("coding_level") == 1 and
                                assignment_in_list.get("topic") == "Introduction to Programming"):
                                self.log_test("Assignment Visible to Student", True, "Assignment correctly appears in student's assignments list")
                            else:
                                self.log_test("Assignment Visible to Student", False, "Assignment data mismatch in student's list")
                                
                        else:
                            self.log_test("Verify Student Assignment Record", False, "Assignment not found in student's assignments list")
                            
                    else:
                        self.log_test("Get Student Assignments", False, f"Status: {response.status_code}, Response: {response.text}")
                        
                else:
                    self.log_test("Student Login for Verification", False, f"Status: {response.status_code}, Response: {response.text}")
                    
            else:
                self.log_test("Assign Assignment to teststudent", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Assign Assignment to teststudent", False, f"Exception: {str(e)}")
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
        
        return result

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Backend Tests - Focus on Learn to Code Assignment for Student Testing")
        print(f"Backend URL: {BACKEND_URL}")
        
        # PRIORITY: Create the specific Learn to Code assignment for student testing
        assignment_result = self.test_learn_to_code_assignment_for_student_clicking()
        
        # PRIORITY: Create test accounts to fix student login black screen
        if not self.create_test_accounts_for_student_login():
            print("❌ Failed to create test accounts. This may cause continued login issues.")
        
        # Test student authentication workflow
        self.test_student_authentication_workflow()
        
        # Setup original authentication for other tests
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with Learn to Code tests.")
            self.print_summary()
            return
            
        # Test each coding level
        level_1_id = self.test_learn_to_code_level_1()
        level_2_id = self.test_learn_to_code_level_2()
        level_3_id = self.test_learn_to_code_level_3()
        level_4_id = self.test_learn_to_code_level_4()
        
        # Test submission with Level 2 (has both MCQ and coding)
        if level_2_id:
            self.test_assignment_submission(level_2_id)
            
        # Test edge cases
        self.test_edge_cases()
        
        # Summary
        self.print_summary()
        
        return assignment_result
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()
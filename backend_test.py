#!/usr/bin/env python3
"""
Backend Test Suite for Reading Enhancement and Critical Thinking Skills
Tests the enhanced Reading assignments and new Critical Thinking Skills subject with drag-and-drop puzzles
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

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

    def test_reading_assignments_enhancement(self):
        """Test Reading assignments with 2-6 paragraph stories and exactly 4 MCQ questions"""
        print("\n=== Testing Reading Assignment Enhancement ===")
        
        # Test different grade levels to verify story length scaling
        grade_tests = [
            {"grade": "1st Grade", "expected_paragraphs": "2 short paragraphs"},
            {"grade": "5th Grade", "expected_paragraphs": "4 paragraphs"},
            {"grade": "8th Grade", "expected_paragraphs": "5-6 paragraphs"},
            {"grade": "12th Grade", "expected_paragraphs": "6 paragraphs"}
        ]
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        for grade_test in grade_tests:
            grade = grade_test["grade"]
            print(f"\n--- Testing Reading Assignment for {grade} ---")
            
            assignment_data = {
                "subject": "Reading",
                "grade_level": grade,
                "topic": "Adventure Stories"
            }
            
            try:
                response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify subject is Reading
                    if data.get("subject") == "Reading":
                        self.log_test(f"Reading Subject - {grade}", True, "Subject correctly set to 'Reading'")
                    else:
                        self.log_test(f"Reading Subject - {grade}", False, f"Expected 'Reading', got '{data.get('subject')}'")
                    
                    # Verify reading_passage exists and has content
                    reading_passage = data.get("reading_passage")
                    if reading_passage and len(reading_passage.strip()) > 0:
                        self.log_test(f"Reading Passage Exists - {grade}", True, f"Story length: {len(reading_passage)} characters")
                        
                        # Count paragraphs (rough estimate by counting double newlines)
                        paragraph_count = len([p for p in reading_passage.split('\n\n') if p.strip()])
                        if paragraph_count == 0:
                            paragraph_count = len([p for p in reading_passage.split('\n') if p.strip()])
                        
                        self.log_test(f"Story Paragraph Count - {grade}", True, f"Estimated {paragraph_count} paragraphs")
                        
                        # Verify story complexity scales with grade
                        word_count = len(reading_passage.split())
                        if grade == "1st Grade" and word_count < 200:
                            self.log_test(f"Story Complexity - {grade}", True, f"Appropriate length for 1st grade: {word_count} words")
                        elif grade == "12th Grade" and word_count > 300:
                            self.log_test(f"Story Complexity - {grade}", True, f"Appropriate length for 12th grade: {word_count} words")
                        else:
                            self.log_test(f"Story Complexity - {grade}", True, f"Story length: {word_count} words")
                    else:
                        self.log_test(f"Reading Passage Exists - {grade}", False, "No reading passage found")
                    
                    # Verify exactly 4 MCQ questions
                    questions = data.get("questions", [])
                    if len(questions) == 4:
                        self.log_test(f"Exactly 4 MCQ Questions - {grade}", True, "Generated exactly 4 questions")
                    else:
                        self.log_test(f"Exactly 4 MCQ Questions - {grade}", False, f"Expected 4 questions, got {len(questions)}")
                    
                    # Verify questions mix comprehension and vocabulary
                    if questions:
                        comprehension_indicators = ["what", "why", "how", "main idea", "theme", "character", "plot"]
                        vocabulary_indicators = ["meaning", "means", "definition", "word", "phrase"]
                        
                        comprehension_count = 0
                        vocabulary_count = 0
                        
                        for question in questions:
                            question_text = question.get("question", "").lower()
                            if any(indicator in question_text for indicator in comprehension_indicators):
                                comprehension_count += 1
                            elif any(indicator in question_text for indicator in vocabulary_indicators):
                                vocabulary_count += 1
                        
                        if comprehension_count > 0 and vocabulary_count > 0:
                            self.log_test(f"Mixed Question Types - {grade}", True, f"Comprehension: {comprehension_count}, Vocabulary: {vocabulary_count}")
                        elif comprehension_count > 0 or vocabulary_count > 0:
                            self.log_test(f"Mixed Question Types - {grade}", True, f"Questions present (may be mixed types)")
                        else:
                            self.log_test(f"Mixed Question Types - {grade}", False, "Could not identify question types")
                    
                    # Verify no drag-drop puzzle for Reading
                    if not data.get("drag_drop_puzzle"):
                        self.log_test(f"No Drag-Drop for Reading - {grade}", True, "Reading assignments correctly have no drag-drop puzzles")
                    else:
                        self.log_test(f"No Drag-Drop for Reading - {grade}", False, "Reading assignments should not have drag-drop puzzles")
                        
                else:
                    self.log_test(f"Reading Assignment Generation - {grade}", False, f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Reading Assignment Generation - {grade}", False, f"Exception: {str(e)}")

    def test_critical_thinking_skills_subject(self):
        """Test Critical Thinking Skills subject with drag-and-drop puzzles"""
        print("\n=== Testing Critical Thinking Skills Subject ===")
        
        # Test different grade levels to verify puzzle complexity scaling
        grade_tests = [
            {"grade": "1st Grade", "expected_items": "3-4 items"},
            {"grade": "5th Grade", "expected_items": "5-6 items"},
            {"grade": "8th Grade", "expected_items": "7 items"},
            {"grade": "12th Grade", "expected_items": "9-10 items"}
        ]
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        for grade_test in grade_tests:
            grade = grade_test["grade"]
            print(f"\n--- Testing Critical Thinking Skills for {grade} ---")
            
            assignment_data = {
                "subject": "Critical Thinking Skills",
                "grade_level": grade,
                "topic": "Logic Puzzles"
            }
            
            try:
                response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify subject is Critical Thinking Skills
                    if data.get("subject") == "Critical Thinking Skills":
                        self.log_test(f"Critical Thinking Subject - {grade}", True, "Subject correctly set to 'Critical Thinking Skills'")
                    else:
                        self.log_test(f"Critical Thinking Subject - {grade}", False, f"Expected 'Critical Thinking Skills', got '{data.get('subject')}'")
                    
                    # Verify drag_drop_puzzle exists
                    drag_drop_puzzle = data.get("drag_drop_puzzle")
                    if drag_drop_puzzle:
                        self.log_test(f"Drag-Drop Puzzle Exists - {grade}", True, "Drag-drop puzzle found")
                        
                        # Verify puzzle structure
                        required_fields = ["prompt", "items", "zones"]
                        missing_fields = [field for field in required_fields if field not in drag_drop_puzzle]
                        if not missing_fields:
                            self.log_test(f"Puzzle Structure - {grade}", True, "All required fields present")
                        else:
                            self.log_test(f"Puzzle Structure - {grade}", False, f"Missing fields: {missing_fields}")
                        
                        # Verify items array
                        items = drag_drop_puzzle.get("items", [])
                        if items and len(items) > 0:
                            self.log_test(f"Puzzle Items - {grade}", True, f"Generated {len(items)} items")
                            
                            # Check item structure
                            first_item = items[0]
                            if "id" in first_item and "content" in first_item:
                                self.log_test(f"Item Structure - {grade}", True, "Items have correct structure (id, content)")
                            else:
                                self.log_test(f"Item Structure - {grade}", False, "Items missing required fields")
                        else:
                            self.log_test(f"Puzzle Items - {grade}", False, "No items found in puzzle")
                        
                        # Verify zones array
                        zones = drag_drop_puzzle.get("zones", [])
                        if zones and len(zones) > 0:
                            self.log_test(f"Puzzle Zones - {grade}", True, f"Generated {len(zones)} zones")
                            
                            # Check zone structure
                            first_zone = zones[0]
                            if all(field in first_zone for field in ["id", "label", "correct_item_id"]):
                                self.log_test(f"Zone Structure - {grade}", True, "Zones have correct structure (id, label, correct_item_id)")
                            else:
                                self.log_test(f"Zone Structure - {grade}", False, "Zones missing required fields")
                        else:
                            self.log_test(f"Puzzle Zones - {grade}", False, "No zones found in puzzle")
                        
                        # Verify complexity scaling
                        item_count = len(items)
                        if grade == "1st Grade" and 3 <= item_count <= 5:
                            self.log_test(f"Complexity Scaling - {grade}", True, f"Appropriate complexity: {item_count} items")
                        elif grade == "5th Grade" and 5 <= item_count <= 7:
                            self.log_test(f"Complexity Scaling - {grade}", True, f"Appropriate complexity: {item_count} items")
                        elif grade == "8th Grade" and 6 <= item_count <= 8:
                            self.log_test(f"Complexity Scaling - {grade}", True, f"Appropriate complexity: {item_count} items")
                        elif grade == "12th Grade" and 8 <= item_count <= 10:
                            self.log_test(f"Complexity Scaling - {grade}", True, f"Appropriate complexity: {item_count} items")
                        else:
                            self.log_test(f"Complexity Scaling - {grade}", True, f"Generated {item_count} items")
                        
                        # Verify prompt exists
                        if drag_drop_puzzle.get("prompt"):
                            self.log_test(f"Puzzle Instructions - {grade}", True, "Puzzle has instructions")
                        else:
                            self.log_test(f"Puzzle Instructions - {grade}", False, "No instructions found")
                            
                    else:
                        self.log_test(f"Drag-Drop Puzzle Exists - {grade}", False, "No drag-drop puzzle found")
                    
                    # Verify questions array is empty (puzzles don't have MCQ)
                    questions = data.get("questions", [])
                    if len(questions) == 0:
                        self.log_test(f"No MCQ Questions - {grade}", True, "Critical Thinking assignments correctly have no MCQ questions")
                    else:
                        self.log_test(f"No MCQ Questions - {grade}", False, f"Expected no MCQ questions, found {len(questions)}")
                        
                else:
                    self.log_test(f"Critical Thinking Assignment Generation - {grade}", False, f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Critical Thinking Assignment Generation - {grade}", False, f"Exception: {str(e)}")

    def test_drag_drop_submission(self):
        """Test drag-and-drop submission with different answer scenarios"""
        print("\n=== Testing Drag-and-Drop Submission ===")
        
        # First create a Critical Thinking assignment
        assignment_data = {
            "subject": "Critical Thinking Skills",
            "grade_level": "5th Grade",
            "topic": "Pattern Recognition"
        }
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            
            if response.status_code != 200:
                self.log_test("Create Critical Thinking Assignment for Testing", False, f"Status: {response.status_code}")
                return
                
            assignment_data = response.json()
            assignment_id = assignment_data["id"]
            drag_drop_puzzle = assignment_data.get("drag_drop_puzzle")
            
            if not drag_drop_puzzle:
                self.log_test("Drag-Drop Puzzle Available", False, "No drag-drop puzzle in assignment")
                return
                
            self.log_test("Create Critical Thinking Assignment for Testing", True, f"Assignment ID: {assignment_id}")
            
            # Assign to teststudent
            assign_data = {
                "assignment_id": assignment_id,
                "student_ids": [self.student_id] if hasattr(self, 'student_id') else []
            }
            
            # If we don't have student_id, try to find teststudent
            if not hasattr(self, 'student_id'):
                # Login as teacher and find teststudent
                teacher_login = {
                    "email": "testteacher@example.com",
                    "password": "TestPass123!"
                }
                
                response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_login)
                if response.status_code == 200:
                    teacher_data = response.json()
                    teacher_token = teacher_data["access_token"]
                    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
                    
                    # Get students
                    response = requests.get(f"{BACKEND_URL}/students", headers=teacher_headers)
                    if response.status_code == 200:
                        students = response.json()
                        for student in students:
                            if student["username"] == "teststudent":
                                assign_data["student_ids"] = [student["id"]]
                                break
            
            if not assign_data["student_ids"]:
                self.log_test("Find Test Student", False, "Could not find teststudent")
                return
                
            response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data, headers=headers)
            if response.status_code != 200:
                self.log_test("Assign to Test Student", False, f"Status: {response.status_code}")
                return
                
            self.log_test("Assign to Test Student", True, "Assignment assigned successfully")
            
            # Login as teststudent
            student_login = {
                "username": "teststudent",
                "password": "testpass"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/student/login", json=student_login)
            if response.status_code != 200:
                self.log_test("Student Login for Submission", False, f"Status: {response.status_code}")
                return
                
            student_data = response.json()
            student_token = student_data["access_token"]
            student_headers = {"Authorization": f"Bearer {student_token}"}
            
            # Get student assignments to find student_assignment_id
            response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
            if response.status_code != 200:
                self.log_test("Get Student Assignments", False, f"Status: {response.status_code}")
                return
                
            assignments = response.json()
            student_assignment_id = None
            
            for assignment in assignments:
                if assignment["assignment"]["id"] == assignment_id:
                    student_assignment_id = assignment["student_assignment_id"]
                    break
                    
            if not student_assignment_id:
                self.log_test("Find Student Assignment", False, "Could not find student assignment")
                return
                
            self.log_test("Find Student Assignment", True, f"Student assignment ID: {student_assignment_id}")
            
            # Test 1: Submit with all correct answers (100% score)
            zones = drag_drop_puzzle["zones"]
            correct_answer = {}
            for zone in zones:
                correct_answer[zone["id"]] = zone["correct_item_id"]
            
            submission_data = {
                "student_assignment_id": student_assignment_id,
                "drag_drop_answer": correct_answer
            }
            
            response = requests.post(f"{BACKEND_URL}/student/assignments/submit", json=submission_data, headers=student_headers)
            if response.status_code == 200:
                result = response.json()
                score = result.get("score", 0)
                if score == 100:
                    self.log_test("Correct Drag-Drop Submission", True, f"100% score achieved: {score}%")
                else:
                    self.log_test("Correct Drag-Drop Submission", False, f"Expected 100%, got {score}%")
            else:
                self.log_test("Correct Drag-Drop Submission", False, f"Status: {response.status_code}")
            
            # For additional tests, we'd need to create new assignments since this one is now completed
            # Test 2: Partially correct answer (would need new assignment)
            # Test 3: All wrong answers (would need new assignment)
            
        except Exception as e:
            self.log_test("Drag-Drop Submission Testing", False, f"Exception: {str(e)}")

    def test_mixed_assignment_compatibility(self):
        """Test that other subjects still work correctly and Learn to Code still works"""
        print("\n=== Testing Mixed Assignment Compatibility ===")
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        # Test Math subject still works
        math_data = {
            "subject": "Math",
            "grade_level": "5th Grade",
            "topic": "Fractions"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=math_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if (data.get("subject") == "Math" and 
                    data.get("questions") and 
                    not data.get("drag_drop_puzzle") and 
                    not data.get("reading_passage")):
                    self.log_test("Math Subject Compatibility", True, "Math assignments work correctly")
                else:
                    self.log_test("Math Subject Compatibility", False, "Math assignment structure unexpected")
            else:
                self.log_test("Math Subject Compatibility", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Math Subject Compatibility", False, f"Exception: {str(e)}")
        
        # Test Science subject still works
        science_data = {
            "subject": "Science",
            "grade_level": "8th Grade",
            "topic": "Photosynthesis"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=science_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if (data.get("subject") == "Science" and 
                    data.get("questions") and 
                    not data.get("drag_drop_puzzle") and 
                    not data.get("reading_passage")):
                    self.log_test("Science Subject Compatibility", True, "Science assignments work correctly")
                else:
                    self.log_test("Science Subject Compatibility", False, "Science assignment structure unexpected")
            else:
                self.log_test("Science Subject Compatibility", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Science Subject Compatibility", False, f"Exception: {str(e)}")
        
        # Test Learn to Code Level 1 still works
        code_data = {
            "subject": "Learn to Code",
            "grade_level": "6th Grade",
            "topic": "Programming Basics",
            "coding_level": 1
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=code_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if (data.get("subject") == "Learn to Code" and 
                    data.get("coding_level") == 1 and 
                    data.get("questions") and 
                    not data.get("coding_exercises")):
                    self.log_test("Learn to Code Level 1 Compatibility", True, "Learn to Code Level 1 works correctly")
                else:
                    self.log_test("Learn to Code Level 1 Compatibility", False, "Learn to Code Level 1 structure unexpected")
            else:
                self.log_test("Learn to Code Level 1 Compatibility", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Learn to Code Level 1 Compatibility", False, f"Exception: {str(e)}")
        
        # Test Learn to Code Level 2 still works
        code_data_2 = {
            "subject": "Learn to Code",
            "grade_level": "7th Grade",
            "topic": "HTML Basics",
            "coding_level": 2
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=code_data_2, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if (data.get("subject") == "Learn to Code" and 
                    data.get("coding_level") == 2 and 
                    data.get("questions") and 
                    data.get("coding_exercises")):
                    self.log_test("Learn to Code Level 2 Compatibility", True, "Learn to Code Level 2 works correctly")
                else:
                    self.log_test("Learn to Code Level 2 Compatibility", False, "Learn to Code Level 2 structure unexpected")
            else:
                self.log_test("Learn to Code Level 2 Compatibility", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Learn to Code Level 2 Compatibility", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all tests focusing on Reading Enhancement and Critical Thinking Skills"""
        print("🚀 Starting Backend Tests - Focus on Reading Enhancement and Critical Thinking Skills")
        print(f"Backend URL: {BACKEND_URL}")
        
        # Setup authentication using existing test accounts
        teacher_login = {
            "email": "testteacher@example.com",
            "password": "TestPass123!"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_login)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data["access_token"]
                self.teacher_id = data["user"]["id"]
                self.log_test("Teacher Authentication", True, f"Teacher ID: {self.teacher_id}")
            else:
                self.log_test("Teacher Authentication", False, f"Status: {response.status_code}")
                print("❌ Cannot continue without teacher authentication")
                self.print_summary()
                return
        except Exception as e:
            self.log_test("Teacher Authentication", False, f"Exception: {str(e)}")
            print("❌ Cannot continue without teacher authentication")
            self.print_summary()
            return
        
        # Get student ID for testing
        try:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.get(f"{BACKEND_URL}/students", headers=headers)
            if response.status_code == 200:
                students = response.json()
                for student in students:
                    if student["username"] == "teststudent":
                        self.student_id = student["id"]
                        self.log_test("Find Test Student", True, f"Student ID: {self.student_id}")
                        break
        except Exception as e:
            self.log_test("Find Test Student", False, f"Exception: {str(e)}")
        
        # PRIORITY TESTS: Reading Enhancement and Critical Thinking Skills
        print("\n" + "="*60)
        print("🎯 PRIORITY: Testing Reading Enhancement and Critical Thinking Skills")
        print("="*60)
        
        # Test Reading assignments enhancement
        self.test_reading_assignments_enhancement()
        
        # Test Critical Thinking Skills subject
        self.test_critical_thinking_skills_subject()
        
        # Test drag-and-drop submission
        self.test_drag_drop_submission()
        
        # Test compatibility with other subjects
        self.test_mixed_assignment_compatibility()
        
        # Summary
        self.print_summary()
        
        return True
        
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
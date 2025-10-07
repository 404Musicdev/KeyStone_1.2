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
            
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Learn to Code Backend Tests")
        print(f"Backend URL: {BACKEND_URL}")
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
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
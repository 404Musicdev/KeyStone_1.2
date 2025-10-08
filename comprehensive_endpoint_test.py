#!/usr/bin/env python3
"""
Comprehensive Test for GET /api/student/assignments/{student_assignment_id} Endpoint
Tests all 4 Learn to Code levels and various assignment types
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

class ComprehensiveEndpointTester:
    def __init__(self):
        self.test_results = []
        self.student_token = None
        self.teacher_token = None
        self.created_assignments = []
        
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
        """Setup authentication tokens"""
        print("\n=== Setting up Authentication ===")
        
        # Login as teststudent
        student_credentials = {
            "username": "teststudent",
            "password": "testpass"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/student/login", json=student_credentials)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user"]["id"]
                self.log_test("Student Authentication", True, f"Student ID: {self.student_id}")
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
            
        # Login as teacher
        teacher_credentials = {
            "email": "testteacher@example.com",
            "password": "TestPass123!"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_credentials)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data["access_token"]
                self.teacher_id = data["user"]["id"]
                self.log_test("Teacher Authentication", True, f"Teacher ID: {self.teacher_id}")
            else:
                self.log_test("Teacher Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Teacher Authentication", False, f"Exception: {str(e)}")
            return False
            
        return True
        
    def create_and_assign_assignment(self, subject, grade_level, topic, coding_level=None, youtube_url=None):
        """Create and assign an assignment to the test student"""
        assignment_data = {
            "subject": subject,
            "grade_level": grade_level,
            "topic": topic
        }
        
        if coding_level:
            assignment_data["coding_level"] = coding_level
        if youtube_url:
            assignment_data["youtube_url"] = youtube_url
            
        try:
            # Create assignment
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
            
            if response.status_code != 200:
                return None, None
                
            assignment = response.json()
            assignment_id = assignment["id"]
            
            # Assign to student
            assign_data = {
                "assignment_id": assignment_id,
                "student_ids": [self.student_id]
            }
            
            response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data, headers=headers)
            
            if response.status_code != 200:
                return assignment_id, None
                
            # Get student assignment ID
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
            
            if response.status_code == 200:
                assignments = response.json()
                for sa in assignments:
                    if sa["assignment"]["id"] == assignment_id:
                        return assignment_id, sa["student_assignment_id"]
                        
            return assignment_id, None
            
        except Exception as e:
            print(f"Error creating assignment: {e}")
            return None, None
            
    def test_learn_to_code_level(self, level):
        """Test a specific Learn to Code level"""
        print(f"\n=== Testing Learn to Code Level {level} ===")
        
        topics = {
            1: "Programming Concepts",
            2: "HTML Fundamentals", 
            3: "JavaScript Basics",
            4: "Python Backend"
        }
        
        assignment_id, student_assignment_id = self.create_and_assign_assignment(
            "Learn to Code",
            "Elementary",
            topics[level],
            coding_level=level
        )
        
        if not student_assignment_id:
            self.log_test(f"Level {level} Assignment Creation", False, "Failed to create or assign assignment")
            return
            
        self.log_test(f"Level {level} Assignment Creation", True, f"Student assignment ID: {student_assignment_id}")
        self.created_assignments.append(student_assignment_id)
        
        # Test endpoint with this assignment
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{student_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                assignment = data.get("assignment", {})
                
                # Verify coding level
                if assignment.get("coding_level") == level:
                    self.log_test(f"Level {level} Coding Level Verification", True, f"Correct coding level: {level}")
                else:
                    self.log_test(f"Level {level} Coding Level Verification", False, f"Expected {level}, got {assignment.get('coding_level')}")
                    
                # Verify coding exercises based on level
                coding_exercises = assignment.get("coding_exercises", [])
                if level == 1:
                    if len(coding_exercises) == 0:
                        self.log_test(f"Level {level} Coding Exercises", True, "Level 1 correctly has no coding exercises")
                    else:
                        self.log_test(f"Level {level} Coding Exercises", False, f"Level 1 should have no coding exercises, found {len(coding_exercises)}")
                else:
                    if len(coding_exercises) > 0:
                        self.log_test(f"Level {level} Coding Exercises", True, f"Level {level} has {len(coding_exercises)} coding exercises")
                        
                        # Verify language for higher levels
                        expected_languages = {2: "html", 3: "javascript", 4: "python"}
                        if level in expected_languages:
                            first_exercise = coding_exercises[0]
                            expected_lang = expected_languages[level]
                            if first_exercise.get("language") == expected_lang:
                                self.log_test(f"Level {level} Language Verification", True, f"Correct language: {expected_lang}")
                            else:
                                self.log_test(f"Level {level} Language Verification", False, f"Expected {expected_lang}, got {first_exercise.get('language')}")
                    else:
                        self.log_test(f"Level {level} Coding Exercises", False, f"Level {level} should have coding exercises")
                        
                # Verify questions exist
                questions = assignment.get("questions", [])
                if len(questions) > 0:
                    self.log_test(f"Level {level} MCQ Questions", True, f"Has {len(questions)} MCQ questions")
                else:
                    self.log_test(f"Level {level} MCQ Questions", False, "No MCQ questions found")
                    
            else:
                self.log_test(f"Level {level} Endpoint Test", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test(f"Level {level} Endpoint Test", False, f"Exception: {str(e)}")
            
    def test_assignment_with_youtube_url(self):
        """Test assignment with YouTube URL"""
        print("\n=== Testing Assignment with YouTube URL ===")
        
        youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assignment_id, student_assignment_id = self.create_and_assign_assignment(
            "Science",
            "Middle School",
            "Solar System",
            youtube_url=youtube_url
        )
        
        if not student_assignment_id:
            self.log_test("YouTube Assignment Creation", False, "Failed to create assignment with YouTube URL")
            return
            
        self.log_test("YouTube Assignment Creation", True, f"Created assignment with YouTube URL")
        self.created_assignments.append(student_assignment_id)
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{student_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                assignment = data.get("assignment", {})
                
                if assignment.get("youtube_url") == youtube_url:
                    self.log_test("YouTube URL Retrieval", True, f"YouTube URL correctly retrieved: {youtube_url}")
                else:
                    self.log_test("YouTube URL Retrieval", False, f"Expected {youtube_url}, got {assignment.get('youtube_url')}")
            else:
                self.log_test("YouTube Assignment Endpoint Test", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("YouTube Assignment Endpoint Test", False, f"Exception: {str(e)}")
            
    def test_assignment_submission_and_retrieval(self):
        """Test submitting an assignment and then retrieving it to verify completed fields"""
        print("\n=== Testing Assignment Submission and Retrieval ===")
        
        # Use Level 2 assignment (has both MCQ and coding)
        assignment_id, student_assignment_id = self.create_and_assign_assignment(
            "Learn to Code",
            "Elementary", 
            "HTML Basics",
            coding_level=2
        )
        
        if not student_assignment_id:
            self.log_test("Submission Test Assignment Creation", False, "Failed to create assignment for submission test")
            return
            
        self.created_assignments.append(student_assignment_id)
        
        try:
            # First get the assignment to see its structure
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{student_assignment_id}", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Pre-submission Assignment Retrieval", False, f"Status: {response.status_code}")
                return
                
            data = response.json()
            assignment = data.get("assignment", {})
            
            # Prepare submission
            questions = assignment.get("questions", [])
            coding_exercises = assignment.get("coding_exercises", [])
            
            submission_data = {
                "student_assignment_id": student_assignment_id,
                "answers": [0] * len(questions),  # Answer all as option 0
                "coding_answers": ["<h1>Test HTML</h1>"] * len(coding_exercises)
            }
            
            # Submit assignment
            response = requests.post(f"{BACKEND_URL}/student/assignments/submit", json=submission_data, headers=headers)
            
            if response.status_code == 200:
                self.log_test("Assignment Submission", True, "Assignment submitted successfully")
                
                # Now retrieve the completed assignment
                response = requests.get(f"{BACKEND_URL}/student/assignments/{student_assignment_id}", headers=headers)
                
                if response.status_code == 200:
                    completed_data = response.json()
                    
                    # Verify completed status
                    if completed_data.get("completed") == True:
                        self.log_test("Completed Status", True, "Assignment marked as completed")
                    else:
                        self.log_test("Completed Status", False, "Assignment not marked as completed")
                        
                    # Verify score exists
                    if "score" in completed_data and completed_data.get("score") is not None:
                        self.log_test("Score Field", True, f"Score: {completed_data.get('score')}")
                    else:
                        self.log_test("Score Field", False, "Score field missing or null")
                        
                    # Verify submitted_at exists
                    if "submitted_at" in completed_data and completed_data.get("submitted_at") is not None:
                        self.log_test("Submitted At Field", True, f"Submitted at: {completed_data.get('submitted_at')}")
                    else:
                        self.log_test("Submitted At Field", False, "submitted_at field missing or null")
                        
                    # Verify answers are stored
                    if completed_data.get("answers") == submission_data["answers"]:
                        self.log_test("Stored Answers", True, "MCQ answers correctly stored")
                    else:
                        self.log_test("Stored Answers", False, "MCQ answers not correctly stored")
                        
                    # Verify coding answers are stored
                    if completed_data.get("coding_answers") == submission_data["coding_answers"]:
                        self.log_test("Stored Coding Answers", True, "Coding answers correctly stored")
                    else:
                        self.log_test("Stored Coding Answers", False, "Coding answers not correctly stored")
                        
                else:
                    self.log_test("Post-submission Assignment Retrieval", False, f"Status: {response.status_code}")
            else:
                self.log_test("Assignment Submission", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Submission and Retrieval Test", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run comprehensive endpoint tests"""
        print("🚀 Starting Comprehensive Student Assignment Endpoint Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing endpoint: GET /api/student/assignments/{{student_assignment_id}}")
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            self.print_summary()
            return
            
        # Test all 4 Learn to Code levels
        for level in [1, 2, 3, 4]:
            self.test_learn_to_code_level(level)
            
        # Test assignment with YouTube URL
        self.test_assignment_with_youtube_url()
        
        # Test assignment submission and retrieval
        self.test_assignment_submission_and_retrieval()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE ENDPOINT TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests run")
        
        if self.created_assignments:
            print(f"\nCreated {len(self.created_assignments)} test assignments:")
            for i, sa_id in enumerate(self.created_assignments, 1):
                print(f"  {i}. {sa_id}")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")

if __name__ == "__main__":
    tester = ComprehensiveEndpointTester()
    tester.run_all_tests()
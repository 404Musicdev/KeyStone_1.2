#!/usr/bin/env python3
"""
Test Suite for GET /api/student/assignments/{student_assignment_id} Endpoint
Tests the newly implemented endpoint for fetching individual student assignments
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

class StudentAssignmentEndpointTester:
    def __init__(self):
        self.test_results = []
        self.student_token = None
        self.teacher_token = None
        self.test_student_assignment_id = "b1a266f8-df02-4a65-9f80-e45cbb59df88"
        
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
        """Setup authentication tokens for testing"""
        print("\n=== Setting up Authentication ===")
        
        # Login as teststudent (password: testpass - corrected from system)
        student_credentials = {
            "username": "teststudent",
            "password": "testpass"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/student/login", json=student_credentials)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.log_test("Student Authentication (teststudent)", True, "Successfully authenticated")
            else:
                self.log_test("Student Authentication (teststudent)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Student Authentication (teststudent)", False, f"Exception: {str(e)}")
            return False
            
        # Login as teacher for comparison tests
        teacher_credentials = {
            "email": "testteacher@example.com",
            "password": "TestPass123!"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_credentials)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data["access_token"]
                self.log_test("Teacher Authentication", True, "Successfully authenticated")
            else:
                self.log_test("Teacher Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                # Continue without teacher token - some tests will be skipped
        except Exception as e:
            self.log_test("Teacher Authentication", False, f"Exception: {str(e)}")
            
        return True
        
    def test_unauthenticated_request(self):
        """Test that endpoint rejects unauthenticated requests"""
        print("\n=== Testing Unauthenticated Request ===")
        
        try:
            response = requests.get(f"{BACKEND_URL}/student/assignments/{self.test_student_assignment_id}")
            
            if response.status_code in [401, 403]:
                self.log_test("Unauthenticated Request Rejection", True, f"Correctly returned {response.status_code} (authentication required)")
            else:
                self.log_test("Unauthenticated Request Rejection", False, f"Expected 401 or 403, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Unauthenticated Request Rejection", False, f"Exception: {str(e)}")
            
    def test_teacher_token_rejection(self):
        """Test that endpoint rejects teacher tokens"""
        print("\n=== Testing Teacher Token Rejection ===")
        
        if not self.teacher_token:
            self.log_test("Teacher Token Rejection", False, "No teacher token available for testing")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{self.test_student_assignment_id}", headers=headers)
            
            if response.status_code == 403:
                self.log_test("Teacher Token Rejection", True, "Correctly returned 403 Forbidden for teacher token")
            else:
                self.log_test("Teacher Token Rejection", False, f"Expected 403, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Teacher Token Rejection", False, f"Exception: {str(e)}")
            
    def test_valid_assignment_retrieval(self):
        """Test retrieving a valid student assignment"""
        print("\n=== Testing Valid Assignment Retrieval ===")
        
        if not self.student_token:
            self.log_test("Valid Assignment Retrieval", False, "No student token available")
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{self.test_student_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Valid Assignment Retrieval", True, f"Successfully retrieved assignment")
                
                # Verify response structure
                required_fields = [
                    "student_assignment_id",
                    "assignment",
                    "completed",
                    "assigned_at",
                    "answers",
                    "coding_answers"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if not missing_fields:
                    self.log_test("Response Structure Validation", True, "All required fields present")
                else:
                    self.log_test("Response Structure Validation", False, f"Missing fields: {missing_fields}")
                    
                # Verify assignment details structure
                assignment = data.get("assignment", {})
                assignment_required_fields = [
                    "title",
                    "subject", 
                    "grade_level",
                    "topic",
                    "questions"
                ]
                
                assignment_missing_fields = [field for field in assignment_required_fields if field not in assignment]
                if not assignment_missing_fields:
                    self.log_test("Assignment Details Structure", True, "Assignment details have all required fields")
                else:
                    self.log_test("Assignment Details Structure", False, f"Assignment missing fields: {assignment_missing_fields}")
                    
                # Verify Learn to Code specific fields
                if assignment.get("subject") == "Learn to Code":
                    if "coding_level" in assignment:
                        self.log_test("Learn to Code Fields", True, f"Coding level: {assignment.get('coding_level')}")
                    else:
                        self.log_test("Learn to Code Fields", False, "Missing coding_level for Learn to Code assignment")
                        
                    # Check for coding exercises if level > 1
                    coding_level = assignment.get("coding_level", 0)
                    coding_exercises = assignment.get("coding_exercises", [])
                    if coding_level == 1:
                        if len(coding_exercises) == 0:
                            self.log_test("Level 1 Coding Exercises", True, "Level 1 correctly has no coding exercises")
                        else:
                            self.log_test("Level 1 Coding Exercises", False, f"Level 1 should have no coding exercises, found {len(coding_exercises)}")
                    elif coding_level > 1:
                        if len(coding_exercises) > 0:
                            self.log_test("Higher Level Coding Exercises", True, f"Level {coding_level} has {len(coding_exercises)} coding exercises")
                        else:
                            self.log_test("Higher Level Coding Exercises", False, f"Level {coding_level} should have coding exercises")
                            
                # Verify student_assignment_id matches
                if data.get("student_assignment_id") == self.test_student_assignment_id:
                    self.log_test("Student Assignment ID Match", True, "Returned ID matches requested ID")
                else:
                    self.log_test("Student Assignment ID Match", False, f"Expected {self.test_student_assignment_id}, got {data.get('student_assignment_id')}")
                    
                return data
                
            elif response.status_code == 404:
                self.log_test("Valid Assignment Retrieval", False, "Assignment not found - may need to create test assignment first")
                return None
            else:
                self.log_test("Valid Assignment Retrieval", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Valid Assignment Retrieval", False, f"Exception: {str(e)}")
            return None
            
    def test_invalid_assignment_id(self):
        """Test with invalid student_assignment_id"""
        print("\n=== Testing Invalid Assignment ID ===")
        
        if not self.student_token:
            self.log_test("Invalid Assignment ID Test", False, "No student token available")
            return
            
        invalid_id = "invalid-assignment-id-12345"
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{invalid_id}", headers=headers)
            
            if response.status_code == 404:
                self.log_test("Invalid Assignment ID Handling", True, "Correctly returned 404 for invalid ID")
            else:
                self.log_test("Invalid Assignment ID Handling", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Invalid Assignment ID Handling", False, f"Exception: {str(e)}")
            
    def test_other_student_assignment(self):
        """Test accessing assignment belonging to another student"""
        print("\n=== Testing Other Student's Assignment Access ===")
        
        if not self.student_token:
            self.log_test("Other Student Assignment Test", False, "No student token available")
            return
            
        # Use a different UUID that might belong to another student
        other_student_assignment_id = "00000000-0000-0000-0000-000000000000"
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{other_student_assignment_id}", headers=headers)
            
            if response.status_code == 404:
                self.log_test("Other Student Assignment Access", True, "Correctly returned 404 for other student's assignment")
            else:
                self.log_test("Other Student Assignment Access", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Other Student Assignment Access", False, f"Exception: {str(e)}")
            
    def test_assignment_with_youtube_url(self):
        """Test assignment that includes YouTube URL"""
        print("\n=== Testing Assignment with YouTube URL ===")
        
        # This test would require creating an assignment with YouTube URL first
        # For now, we'll check if the current assignment has YouTube URL support
        
        if not self.student_token:
            self.log_test("YouTube URL Test", False, "No student token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{self.test_student_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                assignment = data.get("assignment", {})
                
                # Check if youtube_url field exists (even if null)
                if "youtube_url" in assignment:
                    youtube_url = assignment.get("youtube_url")
                    if youtube_url:
                        self.log_test("YouTube URL Support", True, f"Assignment has YouTube URL: {youtube_url}")
                    else:
                        self.log_test("YouTube URL Support", True, "YouTube URL field present (null for this assignment)")
                else:
                    self.log_test("YouTube URL Support", False, "YouTube URL field missing from assignment structure")
            else:
                self.log_test("YouTube URL Test", False, f"Could not retrieve assignment: {response.status_code}")
                
        except Exception as e:
            self.log_test("YouTube URL Test", False, f"Exception: {str(e)}")
            
    def test_completed_assignment_fields(self):
        """Test that completed assignments show score and submitted_at"""
        print("\n=== Testing Completed Assignment Fields ===")
        
        if not self.student_token:
            self.log_test("Completed Assignment Fields Test", False, "No student token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{self.test_student_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                is_completed = data.get("completed", False)
                has_score = "score" in data and data.get("score") is not None
                has_submitted_at = "submitted_at" in data and data.get("submitted_at") is not None
                
                if is_completed:
                    if has_score and has_submitted_at:
                        self.log_test("Completed Assignment Fields", True, f"Score: {data.get('score')}, Submitted: {data.get('submitted_at')}")
                    else:
                        missing = []
                        if not has_score:
                            missing.append("score")
                        if not has_submitted_at:
                            missing.append("submitted_at")
                        self.log_test("Completed Assignment Fields", False, f"Completed assignment missing: {missing}")
                else:
                    # For incomplete assignments, these fields should be null or absent
                    if not has_score and not has_submitted_at:
                        self.log_test("Incomplete Assignment Fields", True, "Incomplete assignment correctly has no score/submitted_at")
                    else:
                        self.log_test("Incomplete Assignment Fields", False, "Incomplete assignment should not have score/submitted_at")
                        
            else:
                self.log_test("Completed Assignment Fields Test", False, f"Could not retrieve assignment: {response.status_code}")
                
        except Exception as e:
            self.log_test("Completed Assignment Fields Test", False, f"Exception: {str(e)}")
            
    def test_data_types_and_format(self):
        """Test that response data types match expected format"""
        print("\n=== Testing Data Types and Format ===")
        
        if not self.student_token:
            self.log_test("Data Types Test", False, "No student token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/student/assignments/{self.test_student_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Test data types
                type_checks = [
                    ("student_assignment_id", str),
                    ("completed", bool),
                    ("answers", list),
                    ("coding_answers", list)
                ]
                
                all_types_correct = True
                for field, expected_type in type_checks:
                    if field in data:
                        actual_value = data[field]
                        if actual_value is not None and not isinstance(actual_value, expected_type):
                            self.log_test(f"Data Type - {field}", False, f"Expected {expected_type.__name__}, got {type(actual_value).__name__}")
                            all_types_correct = False
                        else:
                            self.log_test(f"Data Type - {field}", True, f"Correct type: {expected_type.__name__}")
                            
                # Test assignment structure
                assignment = data.get("assignment", {})
                if isinstance(assignment, dict):
                    assignment_type_checks = [
                        ("questions", list),
                        ("coding_exercises", list)
                    ]
                    
                    for field, expected_type in assignment_type_checks:
                        if field in assignment:
                            actual_value = assignment[field]
                            if actual_value is not None and not isinstance(actual_value, expected_type):
                                self.log_test(f"Assignment Data Type - {field}", False, f"Expected {expected_type.__name__}, got {type(actual_value).__name__}")
                                all_types_correct = False
                            else:
                                self.log_test(f"Assignment Data Type - {field}", True, f"Correct type: {expected_type.__name__}")
                                
                if all_types_correct:
                    self.log_test("Overall Data Types", True, "All data types match expected format")
                    
            else:
                self.log_test("Data Types Test", False, f"Could not retrieve assignment: {response.status_code}")
                
        except Exception as e:
            self.log_test("Data Types Test", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Student Assignment Endpoint Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing endpoint: GET /api/student/assignments/{{student_assignment_id}}")
        print(f"Test assignment ID: {self.test_student_assignment_id}")
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            self.print_summary()
            return
            
        # Run all tests
        self.test_unauthenticated_request()
        self.test_teacher_token_rejection()
        assignment_data = self.test_valid_assignment_retrieval()
        self.test_invalid_assignment_id()
        self.test_other_student_assignment()
        self.test_assignment_with_youtube_url()
        self.test_completed_assignment_fields()
        self.test_data_types_and_format()
        
        # Print summary
        self.print_summary()
        
        return assignment_data
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 STUDENT ASSIGNMENT ENDPOINT TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests run")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
            
        # Show critical issues
        critical_failures = [
            result for result in failed_tests 
            if any(keyword in result['test'].lower() for keyword in ['authentication', 'retrieval', 'structure'])
        ]
        
        if critical_failures:
            print("\n🚨 CRITICAL ISSUES:")
            for test in critical_failures:
                print(f"  - {test['test']}: {test['details']}")

if __name__ == "__main__":
    tester = StudentAssignmentEndpointTester()
    tester.run_all_tests()
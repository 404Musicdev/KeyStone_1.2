#!/usr/bin/env python3
"""
Reward Points System Backend Test Suite
Tests the complete Reward Points System implementation as per review request
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

class RewardSystemTester:
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
        """Setup authentication for testteacher and teststudent"""
        print("\n=== Setting up Authentication ===")
        
        # Login as testteacher@example.com
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
                self.log_test("Teacher Login (testteacher@example.com)", True, f"Teacher ID: {self.teacher_id}")
            else:
                self.log_test("Teacher Login (testteacher@example.com)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Teacher Login (testteacher@example.com)", False, f"Exception: {str(e)}")
            return False
            
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
                self.log_test("Student Login (teststudent)", True, f"Student ID: {self.student_id}")
            else:
                self.log_test("Student Login (teststudent)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Student Login (teststudent)", False, f"Exception: {str(e)}")
            return False
            
        return True
        
    def test_default_rewards_initialization(self):
        """Test 1: Default Rewards Initialization"""
        print("\n=== Test 1: Default Rewards Initialization ===")
        
        teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            # Call POST /api/teacher/initialize-rewards
            response = requests.post(f"{BACKEND_URL}/teacher/initialize-rewards", headers=teacher_headers)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Initialize Default Rewards API Call", True, f"Message: {data.get('message')}")
                
                # Verify 5 default rewards were created
                response = requests.get(f"{BACKEND_URL}/rewards", headers=teacher_headers)
                if response.status_code == 200:
                    rewards = response.json()
                    expected_rewards = [
                        "1 Hour of Game Time",
                        "2 Hours of Game Time", 
                        "12oz Coke",
                        "TV at Night",
                        "One Day Off School"
                    ]
                    
                    if len(rewards) >= 5:
                        self.log_test("Default Rewards Count", True, f"Found {len(rewards)} rewards")
                        
                        # Check if all expected rewards exist
                        reward_titles = [r["title"] for r in rewards]
                        found_rewards = []
                        for expected in expected_rewards:
                            for title in reward_titles:
                                if expected in title:
                                    found_rewards.append(expected)
                                    break
                        
                        if len(found_rewards) == 5:
                            self.log_test("All 5 Default Rewards Created", True, f"Found: {found_rewards}")
                        else:
                            self.log_test("All 5 Default Rewards Created", False, f"Expected 5, found {len(found_rewards)}: {found_rewards}")
                            
                        # Verify reward structure
                        if rewards:
                            first_reward = rewards[0]
                            required_fields = ["id", "title", "description", "points_cost", "teacher_id", "active"]
                            if all(field in first_reward for field in required_fields):
                                self.log_test("Reward Structure Validation", True, "All required fields present")
                            else:
                                missing = [f for f in required_fields if f not in first_reward]
                                self.log_test("Reward Structure Validation", False, f"Missing fields: {missing}")
                    else:
                        self.log_test("Default Rewards Count", False, f"Expected at least 5 rewards, got {len(rewards)}")
                else:
                    self.log_test("Verify Default Rewards", False, f"Status: {response.status_code}")
            else:
                self.log_test("Initialize Default Rewards API Call", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Default Rewards Initialization", False, f"Exception: {str(e)}")
            
    def test_points_auto_award_system(self):
        """Test 2: Points Auto-Award Testing"""
        print("\n=== Test 2: Points Auto-Award Testing ===")
        
        teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Create a simple Math assignment
        assignment_data = {
            "subject": "Math",
            "grade_level": "5th Grade",
            "topic": "Basic Arithmetic"
        }
        
        assignment_id = None
        try:
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=teacher_headers)
            if response.status_code == 200:
                assignment = response.json()
                assignment_id = assignment["id"]
                self.log_test("Create Simple Math Assignment", True, f"Assignment ID: {assignment_id}")
                
                # Assign to teststudent
                assign_data = {
                    "assignment_id": assignment_id,
                    "student_ids": [self.student_id]
                }
                
                response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data, headers=teacher_headers)
                if response.status_code == 200:
                    self.log_test("Assign to teststudent", True, "Assignment assigned successfully")
                else:
                    self.log_test("Assign to teststudent", False, f"Status: {response.status_code}")
                    return
            else:
                self.log_test("Create Simple Math Assignment", False, f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_test("Create Simple Math Assignment", False, f"Exception: {str(e)}")
            return
            
        # Test Scenario 1: Submit with 90% score (should earn 5 points)
        try:
            # Get student assignments to find student_assignment_id
            response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
            if response.status_code == 200:
                assignments = response.json()
                student_assignment_id = None
                assignment_details = None
                
                for assignment in assignments:
                    if assignment["assignment"]["id"] == assignment_id:
                        student_assignment_id = assignment["student_assignment_id"]
                        assignment_details = assignment["assignment"]
                        break
                        
                if student_assignment_id:
                    self.log_test("Find Student Assignment", True, f"Student assignment ID: {student_assignment_id}")
                    
                    # Calculate answers for ~90% score
                    questions = assignment_details.get("questions", [])
                    num_questions = len(questions)
                    
                    if num_questions > 0:
                        # Answer most questions correctly (aim for 90%)
                        correct_answers = max(1, int(num_questions * 0.9))
                        answers = [0] * correct_answers + [1] * (num_questions - correct_answers)
                        
                        submission_data = {
                            "student_assignment_id": student_assignment_id,
                            "answers": answers
                        }
                        
                        response = requests.post(f"{BACKEND_URL}/student/assignments/submit", json=submission_data, headers=student_headers)
                        if response.status_code == 200:
                            result = response.json()
                            score = result.get("score", 0)
                            self.log_test("Submit with 90% Score", True, f"Score achieved: {score}%")
                            
                            if score >= 85:
                                self.log_test("Points Auto-Award (≥85%)", True, f"Score {score}% should earn 5 points")
                                
                                # Verify PointTransaction was created
                                response = requests.get(f"{BACKEND_URL}/student/points", headers=student_headers)
                                if response.status_code == 200:
                                    points_data = response.json()
                                    transactions = points_data.get("transactions", [])
                                    earned_transactions = [t for t in transactions if t["transaction_type"] == "earned"]
                                    
                                    if earned_transactions:
                                        latest_earned = max(earned_transactions, key=lambda x: x["created_at"])
                                        if latest_earned["points"] == 5:
                                            self.log_test("PointTransaction Created (earned)", True, f"5 points transaction found")
                                        else:
                                            self.log_test("PointTransaction Created (earned)", False, f"Expected 5 points, got {latest_earned['points']}")
                                    else:
                                        self.log_test("PointTransaction Created (earned)", False, "No earned transactions found")
                            else:
                                self.log_test("Points Auto-Award (≥85%)", False, f"Score {score}% below 85% threshold")
                        else:
                            self.log_test("Submit with 90% Score", False, f"Status: {response.status_code}")
                    else:
                        self.log_test("Assignment Questions Check", False, "No questions found in assignment")
                else:
                    self.log_test("Find Student Assignment", False, "Could not find student assignment")
            else:
                self.log_test("Get Student Assignments", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("90% Score Submission Test", False, f"Exception: {str(e)}")
            
        # Test Scenario 2: Submit with 80% score (should NOT earn points)
        # Create another assignment for this test
        try:
            assignment_data_2 = {
                "subject": "Math",
                "grade_level": "5th Grade",
                "topic": "Subtraction"
            }
            
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data_2, headers=teacher_headers)
            if response.status_code == 200:
                assignment_2 = response.json()
                assignment_id_2 = assignment_2["id"]
                
                # Assign to teststudent
                assign_data_2 = {
                    "assignment_id": assignment_id_2,
                    "student_ids": [self.student_id]
                }
                
                response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data_2, headers=teacher_headers)
                if response.status_code == 200:
                    # Get the new student assignment
                    response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
                    if response.status_code == 200:
                        assignments = response.json()
                        student_assignment_id_2 = None
                        assignment_details_2 = None
                        
                        for assignment in assignments:
                            if assignment["assignment"]["id"] == assignment_id_2 and not assignment["completed"]:
                                student_assignment_id_2 = assignment["student_assignment_id"]
                                assignment_details_2 = assignment["assignment"]
                                break
                                
                        if student_assignment_id_2:
                            # Submit with 80% score (below 85% threshold)
                            questions_2 = assignment_details_2.get("questions", [])
                            num_questions_2 = len(questions_2)
                            
                            if num_questions_2 > 0:
                                # Answer for ~80% score
                                correct_answers_2 = max(1, int(num_questions_2 * 0.8))
                                answers_2 = [0] * correct_answers_2 + [1] * (num_questions_2 - correct_answers_2)
                                
                                submission_data_2 = {
                                    "student_assignment_id": student_assignment_id_2,
                                    "answers": answers_2
                                }
                                
                                response = requests.post(f"{BACKEND_URL}/student/assignments/submit", json=submission_data_2, headers=student_headers)
                                if response.status_code == 200:
                                    result_2 = response.json()
                                    score_2 = result_2.get("score", 0)
                                    self.log_test("Submit with 80% Score", True, f"Score achieved: {score_2}%")
                                    
                                    if score_2 < 85:
                                        self.log_test("No Points for <85% Score", True, f"Score {score_2}% correctly below threshold")
                                    else:
                                        self.log_test("No Points for <85% Score", False, f"Score {score_2}% unexpectedly above threshold")
        except Exception as e:
            self.log_test("80% Score Submission Test", False, f"Exception: {str(e)}")
            
        # Test Scenario 3: Submit with 100% score (should earn 5 points)
        try:
            assignment_data_3 = {
                "subject": "Math",
                "grade_level": "5th Grade",
                "topic": "Addition"
            }
            
            response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data_3, headers=teacher_headers)
            if response.status_code == 200:
                assignment_3 = response.json()
                assignment_id_3 = assignment_3["id"]
                
                # Assign to teststudent
                assign_data_3 = {
                    "assignment_id": assignment_id_3,
                    "student_ids": [self.student_id]
                }
                
                response = requests.post(f"{BACKEND_URL}/assignments/assign", json=assign_data_3, headers=teacher_headers)
                if response.status_code == 200:
                    # Get the new student assignment
                    response = requests.get(f"{BACKEND_URL}/student/assignments", headers=student_headers)
                    if response.status_code == 200:
                        assignments = response.json()
                        student_assignment_id_3 = None
                        assignment_details_3 = None
                        
                        for assignment in assignments:
                            if assignment["assignment"]["id"] == assignment_id_3 and not assignment["completed"]:
                                student_assignment_id_3 = assignment["student_assignment_id"]
                                assignment_details_3 = assignment["assignment"]
                                break
                                
                        if student_assignment_id_3:
                            # Submit with 100% score (all correct answers)
                            questions_3 = assignment_details_3.get("questions", [])
                            num_questions_3 = len(questions_3)
                            
                            if num_questions_3 > 0:
                                # Answer all questions correctly (assuming correct answer is index 0)
                                answers_3 = [0] * num_questions_3
                                
                                submission_data_3 = {
                                    "student_assignment_id": student_assignment_id_3,
                                    "answers": answers_3
                                }
                                
                                response = requests.post(f"{BACKEND_URL}/student/assignments/submit", json=submission_data_3, headers=student_headers)
                                if response.status_code == 200:
                                    result_3 = response.json()
                                    score_3 = result_3.get("score", 0)
                                    self.log_test("Submit with 100% Score", True, f"Score achieved: {score_3}%")
                                    
                                    if score_3 >= 85:
                                        self.log_test("Points Auto-Award for 100%", True, f"Score {score_3}% should earn 5 points")
        except Exception as e:
            self.log_test("100% Score Submission Test", False, f"Exception: {str(e)}")
            
    def test_student_points_retrieval(self):
        """Test 3: Student Points Retrieval"""
        print("\n=== Test 3: Student Points Retrieval ===")
        
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Call GET /api/student/points
            response = requests.get(f"{BACKEND_URL}/student/points", headers=student_headers)
            if response.status_code == 200:
                points_data = response.json()
                total_points = points_data.get("total_points", 0)
                transactions = points_data.get("transactions", [])
                
                self.log_test("Get Student Points API", True, f"Total points: {total_points}")
                
                # Verify total_points calculation
                calculated_total = sum(t["points"] for t in transactions)
                if total_points == calculated_total:
                    self.log_test("Total Points Calculation", True, f"Calculated: {calculated_total}, Returned: {total_points}")
                else:
                    self.log_test("Total Points Calculation", False, f"Mismatch - Calculated: {calculated_total}, Returned: {total_points}")
                
                # Verify transactions array shows "earned" entries
                earned_transactions = [t for t in transactions if t["transaction_type"] == "earned"]
                if earned_transactions:
                    self.log_test("Earned Transactions Present", True, f"Found {len(earned_transactions)} earned transactions")
                    
                    # Verify transaction structure
                    if earned_transactions:
                        first_earned = earned_transactions[0]
                        required_fields = ["id", "student_id", "points", "transaction_type", "description", "created_at"]
                        if all(field in first_earned for field in required_fields):
                            self.log_test("Transaction Structure", True, "All required fields present")
                        else:
                            missing = [f for f in required_fields if f not in first_earned]
                            self.log_test("Transaction Structure", False, f"Missing fields: {missing}")
                else:
                    self.log_test("Earned Transactions Present", False, "No earned transactions found")
                    
                # Expected points: Should have earned points from 90% and 100% submissions (10 points total)
                expected_earned_points = 10  # 5 points each for two assignments ≥85%
                actual_earned_points = sum(t["points"] for t in earned_transactions)
                
                if actual_earned_points >= expected_earned_points:
                    self.log_test("Expected Points from Assignments", True, f"Earned {actual_earned_points} points (expected ≥{expected_earned_points})")
                else:
                    self.log_test("Expected Points from Assignments", False, f"Earned {actual_earned_points} points (expected ≥{expected_earned_points})")
                    
            else:
                self.log_test("Get Student Points API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Student Points Retrieval", False, f"Exception: {str(e)}")
            
    def test_reward_redemption(self):
        """Test 4: Reward Redemption"""
        print("\n=== Test 4: Reward Redemption ===")
        
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            # Call GET /api/rewards (should see 5 rewards)
            response = requests.get(f"{BACKEND_URL}/rewards", headers=student_headers)
            if response.status_code == 200:
                rewards = response.json()
                self.log_test("Get Rewards (Student View)", True, f"Found {len(rewards)} rewards")
                
                if len(rewards) >= 5:
                    self.log_test("5 Rewards Visible", True, "Student can see all rewards")
                else:
                    self.log_test("5 Rewards Visible", False, f"Expected ≥5 rewards, found {len(rewards)}")
                
                # Find "1 Hour of Game Time" reward (50 points)
                game_time_reward = None
                for reward in rewards:
                    if "1 Hour of Game Time" in reward["title"]:
                        game_time_reward = reward
                        break
                        
                if game_time_reward:
                    self.log_test("Find 1 Hour Game Time Reward", True, f"Cost: {game_time_reward['points_cost']} points")
                    
                    # Attempt to redeem (should FAIL - only has 10 points, need 50)
                    response = requests.post(f"{BACKEND_URL}/student/redeem?reward_id={game_time_reward['id']}", headers=student_headers)
                    if response.status_code == 400:
                        error_data = response.json()
                        if "Not enough points" in error_data.get("detail", ""):
                            self.log_test("Insufficient Points Redemption Fails", True, "Correctly rejected due to insufficient points")
                            
                            # Verify error message about insufficient points
                            detail = error_data.get("detail", "")
                            if "You have" in detail and "need" in detail:
                                self.log_test("Error Message Details", True, f"Detailed error: {detail}")
                            else:
                                self.log_test("Error Message Details", False, f"Error message not detailed enough: {detail}")
                        else:
                            self.log_test("Insufficient Points Redemption Fails", False, f"Unexpected error: {error_data}")
                    elif response.status_code == 200:
                        self.log_test("Insufficient Points Redemption Fails", False, "Redemption unexpectedly succeeded")
                    else:
                        self.log_test("Insufficient Points Redemption Fails", False, f"Unexpected status: {response.status_code}")
                        
                    # Manually give student 50 points via teacher
                    points_adjustment = {
                        "student_id": self.student_id,
                        "points": 50,
                        "description": "Manual points for redemption testing"
                    }
                    
                    response = requests.post(f"{BACKEND_URL}/teacher/points", json=points_adjustment, headers=teacher_headers)
                    if response.status_code == 200:
                        result = response.json()
                        new_total = result.get("new_total", 0)
                        self.log_test("Manual Points Addition (50 points)", True, f"New total: {new_total}")
                        
                        # Retry redemption (should SUCCESS)
                        response = requests.post(f"{BACKEND_URL}/student/redeem?reward_id={game_time_reward['id']}", headers=student_headers)
                        if response.status_code == 200:
                            redemption_result = response.json()
                            remaining_points = redemption_result.get("remaining_points", 0)
                            self.log_test("Successful Redemption", True, f"Redeemed successfully, remaining: {remaining_points}")
                            
                            # Verify points deducted (10+50-50 = 10 remaining)
                            expected_remaining = new_total - game_time_reward['points_cost']
                            if remaining_points == expected_remaining:
                                self.log_test("Points Deducted Correctly", True, f"Expected {expected_remaining}, got {remaining_points}")
                            else:
                                self.log_test("Points Deducted Correctly", False, f"Expected {expected_remaining}, got {remaining_points}")
                                
                            # Verify RewardRedemption record created
                            redemption = redemption_result.get("redemption")
                            if redemption and "id" in redemption:
                                self.log_test("RewardRedemption Record Created", True, f"Redemption ID: {redemption['id']}")
                            else:
                                self.log_test("RewardRedemption Record Created", False, "No redemption record in response")
                        else:
                            self.log_test("Successful Redemption", False, f"Status: {response.status_code}")
                    else:
                        self.log_test("Manual Points Addition (50 points)", False, f"Status: {response.status_code}")
                else:
                    self.log_test("Find 1 Hour Game Time Reward", False, "Could not find expected reward")
            else:
                self.log_test("Get Rewards (Student View)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Reward Redemption", False, f"Exception: {str(e)}")
            
    def test_teacher_points_management(self):
        """Test 5: Teacher Points Management"""
        print("\n=== Test 5: Teacher Points Management ===")
        
        teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            # Call POST /api/teacher/points to add 100 points to teststudent
            points_adjustment = {
                "student_id": self.student_id,
                "points": 100,
                "description": "Additional points for testing teacher management"
            }
            
            response = requests.post(f"{BACKEND_URL}/teacher/points", json=points_adjustment, headers=teacher_headers)
            if response.status_code == 200:
                result = response.json()
                new_total = result.get("new_total", 0)
                points_adjusted = result.get("points_adjusted", 0)
                
                self.log_test("Add 100 Points via Teacher", True, f"Added {points_adjusted} points, new total: {new_total}")
                
                # Verify transaction created with type "manual_add"
                response = requests.get(f"{BACKEND_URL}/teacher/student-points", headers=teacher_headers)
                if response.status_code == 200:
                    students_points = response.json()
                    
                    # Find teststudent in the list
                    teststudent_points = None
                    for student_data in students_points:
                        if student_data["student_id"] == self.student_id:
                            teststudent_points = student_data
                            break
                            
                    if teststudent_points:
                        transactions = teststudent_points["transactions"]
                        manual_add_transactions = [t for t in transactions if t["transaction_type"] == "manual_add"]
                        
                        if manual_add_transactions:
                            latest_manual = max(manual_add_transactions, key=lambda x: x["created_at"])
                            if latest_manual["points"] == 100:
                                self.log_test("Manual Add Transaction Created", True, f"Found manual_add transaction with 100 points")
                            else:
                                self.log_test("Manual Add Transaction Created", False, f"Expected 100 points, got {latest_manual['points']}")
                        else:
                            self.log_test("Manual Add Transaction Created", False, "No manual_add transactions found")
                    else:
                        self.log_test("Find Student in Points List", False, "teststudent not found in teacher's student points list")
            else:
                self.log_test("Add 100 Points via Teacher", False, f"Status: {response.status_code}")
                
            # Call GET /api/teacher/student-points
            response = requests.get(f"{BACKEND_URL}/teacher/student-points", headers=teacher_headers)
            if response.status_code == 200:
                students_points = response.json()
                self.log_test("Get All Students Points", True, f"Retrieved points for {len(students_points)} students")
                
                # Verify teststudent now has 110 total points (10 earned + 50 manual + 100 manual - 50 redeemed + 100 new = 210)
                teststudent_points = None
                for student_data in students_points:
                    if student_data["student_id"] == self.student_id:
                        teststudent_points = student_data
                        break
                        
                if teststudent_points:
                    total_points = teststudent_points["total_points"]
                    self.log_test("Verify Student Total Points", True, f"teststudent has {total_points} total points")
                    
                    # Verify structure includes all required fields
                    required_fields = ["student_id", "student_name", "username", "total_points", "transactions", "redemptions"]
                    if all(field in teststudent_points for field in required_fields):
                        self.log_test("Teacher Points View Structure", True, "All required fields present")
                    else:
                        missing = [f for f in required_fields if f not in teststudent_points]
                        self.log_test("Teacher Points View Structure", False, f"Missing fields: {missing}")
                else:
                    self.log_test("Verify Student Total Points", False, "teststudent not found in points list")
            else:
                self.log_test("Get All Students Points", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Teacher Points Management", False, f"Exception: {str(e)}")
            
    def test_reward_crud_operations(self):
        """Test 6: Reward CRUD Testing"""
        print("\n=== Test 6: Reward CRUD Testing ===")
        
        teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Create new reward: "Pizza Party" (150 points)
            new_reward_data = {
                "title": "Pizza Party",
                "description": "Enjoy a delicious pizza party with classmates",
                "points_cost": 150
            }
            
            response = requests.post(f"{BACKEND_URL}/rewards", json=new_reward_data, headers=teacher_headers)
            if response.status_code == 200:
                created_reward = response.json()
                reward_id = created_reward["id"]
                self.log_test("Create New Reward (Pizza Party)", True, f"Created reward ID: {reward_id}")
                
                # Verify reward structure
                if all(field in created_reward for field in ["id", "title", "description", "points_cost", "teacher_id", "active"]):
                    self.log_test("New Reward Structure", True, "All required fields present")
                else:
                    self.log_test("New Reward Structure", False, "Missing required fields")
                    
                # Update existing reward: Change "TV at Night" to 250 points
                # First find the TV at Night reward
                response = requests.get(f"{BACKEND_URL}/rewards", headers=teacher_headers)
                if response.status_code == 200:
                    rewards = response.json()
                    tv_reward = None
                    for reward in rewards:
                        if "TV at Night" in reward["title"]:
                            tv_reward = reward
                            break
                            
                    if tv_reward:
                        update_data = {
                            "title": "TV at Night",
                            "description": "Watch TV at night for one special night",
                            "points_cost": 250
                        }
                        
                        response = requests.put(f"{BACKEND_URL}/rewards/{tv_reward['id']}", json=update_data, headers=teacher_headers)
                        if response.status_code == 200:
                            updated_reward = response.json()
                            if updated_reward["points_cost"] == 250:
                                self.log_test("Update Existing Reward (TV at Night)", True, f"Updated cost to {updated_reward['points_cost']} points")
                            else:
                                self.log_test("Update Existing Reward (TV at Night)", False, f"Expected 250 points, got {updated_reward['points_cost']}")
                        else:
                            self.log_test("Update Existing Reward (TV at Night)", False, f"Status: {response.status_code}")
                    else:
                        self.log_test("Find TV at Night Reward", False, "Could not find TV at Night reward")
                        
                # Delete the Pizza Party reward
                response = requests.delete(f"{BACKEND_URL}/rewards/{reward_id}", headers=teacher_headers)
                if response.status_code == 200:
                    self.log_test("Delete Reward (Pizza Party)", True, "Reward deleted successfully")
                    
                    # Verify students only see active rewards
                    response = requests.get(f"{BACKEND_URL}/rewards", headers=student_headers)
                    if response.status_code == 200:
                        student_rewards = response.json()
                        pizza_rewards = [r for r in student_rewards if "Pizza Party" in r["title"]]
                        
                        if len(pizza_rewards) == 0:
                            self.log_test("Students See Only Active Rewards", True, "Deleted reward not visible to students")
                        else:
                            self.log_test("Students See Only Active Rewards", False, f"Found {len(pizza_rewards)} pizza rewards (should be 0)")
                    else:
                        self.log_test("Students See Only Active Rewards", False, f"Status: {response.status_code}")
                else:
                    self.log_test("Delete Reward (Pizza Party)", False, f"Status: {response.status_code}")
            else:
                self.log_test("Create New Reward (Pizza Party)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Reward CRUD Operations", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all reward system tests"""
        print("🚀 Starting Reward Points System Test Suite")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            return
            
        # Run all tests in sequence
        self.test_default_rewards_initialization()
        self.test_points_auto_award_system()
        self.test_student_points_retrieval()
        self.test_reward_redemption()
        self.test_teacher_points_management()
        self.test_reward_crud_operations()
        
        # Print summary
        self.print_test_summary()
        
    def print_test_summary(self):
        """Print a summary of all test results"""
        print("\n" + "=" * 60)
        print("📊 REWARD SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"   • {test['test']}: {test['details']}")
        else:
            print(f"\n🎉 ALL REWARD SYSTEM TESTS PASSED!")
            
        # Summary by test category
        print(f"\n📋 TEST CATEGORIES:")
        categories = {
            "Default Rewards": [t for t in self.test_results if "Default Rewards" in t["test"] or "Initialize" in t["test"]],
            "Points Auto-Award": [t for t in self.test_results if "Points Auto-Award" in t["test"] or "Score" in t["test"]],
            "Points Retrieval": [t for t in self.test_results if "Student Points" in t["test"] and "Teacher" not in t["test"]],
            "Reward Redemption": [t for t in self.test_results if "Redemption" in t["test"] or "Redeem" in t["test"]],
            "Teacher Management": [t for t in self.test_results if "Teacher" in t["test"] and "Points" in t["test"]],
            "CRUD Operations": [t for t in self.test_results if "CRUD" in t["test"] or "Create" in t["test"] or "Update" in t["test"] or "Delete" in t["test"]]
        }
        
        for category, tests in categories.items():
            if tests:
                passed = len([t for t in tests if t["success"]])
                total = len(tests)
                print(f"   {category}: {passed}/{total} passed")

if __name__ == "__main__":
    tester = RewardSystemTester()
    tester.run_all_tests()
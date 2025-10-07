#!/usr/bin/env python3
"""
Quick test of all Learn to Code levels
"""

import requests
import json

BACKEND_URL = "https://homeschool-ai.preview.emergentagent.com/api"

# Login teacher
teacher_data = {"email": "teacher.code@example.com", "password": "SecurePass123!"}
response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_data)
if response.status_code == 200:
    teacher_token = response.json()["access_token"]
    print("✅ Teacher authenticated")
else:
    print(f"❌ Teacher login failed")
    exit(1)

headers = {"Authorization": f"Bearer {teacher_token}"}

# Test all 4 levels
levels = [
    {"level": 1, "topic": "Programming Concepts", "expected_coding": 0},
    {"level": 2, "topic": "HTML Basics", "expected_coding": 1},
    {"level": 3, "topic": "JavaScript Fundamentals", "expected_coding": 1},
    {"level": 4, "topic": "Python Backend", "expected_coding": 1}
]

for level_info in levels:
    assignment_data = {
        "subject": "Learn to Code",
        "grade_level": "Elementary",
        "topic": level_info["topic"],
        "coding_level": level_info["level"]
    }
    
    response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        questions = len(data.get("questions", []))
        coding_exercises = len(data.get("coding_exercises", []))
        
        print(f"✅ Level {level_info['level']}: {questions} questions, {coding_exercises} coding exercises")
        
        # Check if it meets expectations
        if level_info["expected_coding"] == 0 and coding_exercises == 0:
            print(f"   ✅ Correctly has no coding exercises")
        elif level_info["expected_coding"] > 0 and coding_exercises > 0:
            print(f"   ✅ Correctly has coding exercises")
            if data.get("coding_exercises"):
                lang = data["coding_exercises"][0].get("language", "unknown")
                print(f"   ✅ Language: {lang}")
        else:
            print(f"   ❌ Expected {level_info['expected_coding']} coding exercises, got {coding_exercises}")
    else:
        print(f"❌ Level {level_info['level']} failed: {response.status_code}")

print("\n🎉 All levels tested!")
#!/usr/bin/env python3
"""
Debug Level 4 specifically to see what's happening
"""

import requests
import json

BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

# Use existing teacher credentials
teacher_data = {
    "email": "teacher.code@example.com",
    "password": "SecurePass123!"
}

# Login teacher
response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_data)
if response.status_code == 200:
    data = response.json()
    teacher_token = data["access_token"]
    print("✅ Teacher authenticated")
else:
    print(f"❌ Teacher login failed: {response.text}")
    exit(1)

# Test Level 4 assignment generation
assignment_data = {
    "subject": "Learn to Code",
    "grade_level": "High School",
    "topic": "Python Backend Development",
    "coding_level": 4
}

headers = {"Authorization": f"Bearer {teacher_token}"}
response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nAssignment Details:")
    print(f"Subject: {data.get('subject')}")
    print(f"Coding Level: {data.get('coding_level')}")
    print(f"Questions: {len(data.get('questions', []))}")
    print(f"Coding Exercises: {len(data.get('coding_exercises', []))}")
    
    if data.get('coding_exercises'):
        print(f"\nFirst Coding Exercise:")
        exercise = data['coding_exercises'][0]
        print(f"Language: {exercise.get('language')}")
        print(f"Prompt: {exercise.get('prompt')[:100]}...")
    else:
        print("\n❌ No coding exercises found!")
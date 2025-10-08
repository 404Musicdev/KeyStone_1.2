#!/usr/bin/env python3
"""
Test edge cases for Learn to Code functionality
"""

import requests

BACKEND_URL = "https://keystoneedu.preview.emergentagent.com/api"

# Login teacher
teacher_data = {"email": "teacher.code@example.com", "password": "SecurePass123!"}
response = requests.post(f"{BACKEND_URL}/auth/teacher/login", json=teacher_data)
teacher_token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {teacher_token}"}

print("✅ Teacher authenticated")

# Test 1: Learn to Code without coding_level
print("\n=== Test 1: Missing coding_level ===")
assignment_data = {
    "subject": "Learn to Code",
    "grade_level": "Elementary",
    "topic": "Programming Basics"
}

response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Generated assignment without coding_level")
    print(f"   Questions: {len(data.get('questions', []))}")
    print(f"   Coding exercises: {len(data.get('coding_exercises', []))}")
else:
    print(f"❌ Failed: {response.status_code}")

# Test 2: Invalid coding level
print("\n=== Test 2: Invalid coding_level ===")
assignment_data = {
    "subject": "Learn to Code",
    "grade_level": "Elementary", 
    "topic": "Programming Basics",
    "coding_level": 99
}

response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Handled invalid coding_level gracefully")
    print(f"   Questions: {len(data.get('questions', []))}")
    print(f"   Coding exercises: {len(data.get('coding_exercises', []))}")
else:
    print(f"❌ Failed: {response.status_code}")

# Test 3: Other subjects still work
print("\n=== Test 3: Other subjects work normally ===")
assignment_data = {
    "subject": "Math",
    "grade_level": "Elementary",
    "topic": "Addition and Subtraction"
}

response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Math subject works normally")
    print(f"   Subject: {data.get('subject')}")
    print(f"   Questions: {len(data.get('questions', []))}")
    print(f"   Coding exercises: {len(data.get('coding_exercises', []))}")
    if data.get('coding_exercises'):
        print("   ❌ Math should not have coding exercises!")
    else:
        print("   ✅ Math correctly has no coding exercises")
else:
    print(f"❌ Failed: {response.status_code}")

# Test 4: Science subject
print("\n=== Test 4: Science subject ===")
assignment_data = {
    "subject": "Science",
    "grade_level": "Middle School",
    "topic": "Solar System"
}

response = requests.post(f"{BACKEND_URL}/assignments/generate", json=assignment_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Science subject works normally")
    print(f"   Subject: {data.get('subject')}")
    print(f"   Questions: {len(data.get('questions', []))}")
    print(f"   Coding exercises: {len(data.get('coding_exercises', []))}")
else:
    print(f"❌ Failed: {response.status_code}")

print("\n🎉 All edge cases tested!")
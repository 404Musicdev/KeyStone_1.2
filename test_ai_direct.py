#!/usr/bin/env python3
"""
Test AI generation directly to debug the issue
"""

import os
import uuid
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# Test the AI generation function directly
async def test_ai_generation():
    try:
        # Initialize Gemini chat
        chat = LlmChat(
            api_key=os.environ['GEMINI_API_KEY'],
            session_id=f"assignment_{uuid.uuid4()}",
            system_message="You are an expert educational content creator for homeschool teachers."
        ).with_model("gemini", "gemini-2.5-pro")
        
        # Test Level 4 prompt
        prompt = """
        Create a "Learn to Code - Level 4" Python backend assignment for High School students.
        Topic: Python Backend Development
        
        Generate:
        1. 2-3 multiple-choice questions about Python and backend development
        2. 1-2 simple Python coding exercises for backend concepts
        
        Return your response in this EXACT JSON format:
        {
            "questions": [
                {
                    "question": "What is Python commonly used for?",
                    "options": ["Web backends, data science, automation", "Only games", "Only websites", "Only mobile apps"],
                    "correct_answer": 0
                }
            ],
            "coding_exercises": [
                {
                    "prompt": "Write Python code to create a simple function that returns a greeting message",
                    "language": "python",
                    "starter_code": "# Define a function called greet\\ndef greet(name):\\n    # Your code here\\n    pass\\n\\n# Test the function\\nprint(greet('World'))",
                    "correct_answer": "def greet(name):\\n    return f'Hello, {name}!'\\n\\nprint(greet('World'))",
                    "explanation": "This function takes a name parameter and returns a formatted greeting string."
                }
            ]
        }
        """
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        print("AI Response:")
        print(response)
        
        # Try to parse the response
        response_text = response.strip()
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != -1:
            json_text = response_text[start:end]
            result = json.loads(json_text)
            print("\nParsed JSON:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print("No JSON found in response")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ai_generation())
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
from jose import JWTError, jwt
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings
SECRET_KEY = "homeschool_hub_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Homeschool Hub API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "teacher"  # teacher or student

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str

class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    username: str
    teacher_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudentLogin(BaseModel):
    username: str
    password: str

# Assignment Models
class AssignmentGenerate(BaseModel):
    subject: str
    grade_level: str
    topic: str
    coding_level: Optional[int] = None  # 1-4 for Learn to Code assignments
    youtube_url: Optional[str] = None

class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer: int  # Index of correct answer (0-3)

class CodingExercise(BaseModel):
    prompt: str
    language: str  # "html", "javascript", "python"
    starter_code: Optional[str] = None
    correct_answer: str
    explanation: Optional[str] = None

class DragDropItem(BaseModel):
    id: str
    content: str  # The text/label of the item to drag

class DragDropZone(BaseModel):
    id: str
    label: str  # Label for the drop zone
    correct_item_id: str  # ID of the item that belongs here

class DragDropPuzzle(BaseModel):
    prompt: str  # Instructions for the puzzle
    items: List[DragDropItem]  # Items to drag
    zones: List[DragDropZone]  # Drop zones where items should be placed
    explanation: Optional[str] = None

class InteractiveWordActivity(BaseModel):
    instruction: str  # e.g., "Click on the word 'cat'"
    target_word: str  # The word student should click
    sentence_index: int  # Which sentence contains the word (0-based)

class LearnToReadContent(BaseModel):
    story: List[str]  # List of 5-7 short sentences
    activities: List[InteractiveWordActivity]  # Interactive word-click activities

class SpellingWordList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    teacher_id: str
    student_id: str
    name: str  # e.g., "Week 1 Words"
    words: List[str]  # List of 10 spelling words
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True

class SpellingWordListCreate(BaseModel):
    student_id: str
    name: str
    words: List[str]

class SpellingPracticeWord(BaseModel):
    word: str
    attempts: int = 3  # Student writes it 3 times

class SpellingTestWord(BaseModel):
    word: str  # Student types it once after hearing it

class Assignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    subject: str
    grade_level: str
    topic: str
    questions: List[Question]
    reading_passage: Optional[str] = None
    coding_level: Optional[int] = None  # 1-4 for Learn to Code assignments
    coding_exercises: Optional[List[CodingExercise]] = None
    drag_drop_puzzle: Optional[DragDropPuzzle] = None  # For Critical Thinking Skills assignments
    learn_to_read_content: Optional[LearnToReadContent] = None  # For Learn to Read assignments
    spelling_type: Optional[str] = None  # "practice" or "test"
    spelling_word_list_id: Optional[str] = None  # Reference to SpellingWordList
    spelling_words: Optional[List[str]] = None  # The actual words for this assignment
    youtube_url: Optional[str] = None
    teacher_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssignmentAssign(BaseModel):
    assignment_id: str
    student_ids: List[str]

class StudentAssignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assignment_id: str
    student_id: str
    teacher_id: str
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = None
    answers: Optional[List[int]] = None  # Student's MCQ answers (indices)
    coding_answers: Optional[List[str]] = None  # Student's code submissions
    drag_drop_answer: Optional[dict] = None  # Student's drag-drop answer {zone_id: item_id}
    interactive_word_answers: Optional[List[str]] = None  # Words clicked in Learn to Read
    spelling_practice_answers: Optional[dict] = None  # {word: [attempt1, attempt2, attempt3]}
    spelling_test_answers: Optional[List[str]] = None  # List of spellings for test
    score: Optional[float] = None
    completed: bool = False

class SubmissionRequest(BaseModel):
    student_assignment_id: str
    answers: Optional[List[int]] = None  # MCQ answers
    coding_answers: Optional[List[str]] = None  # Code answers
    drag_drop_answer: Optional[dict] = None  # Drag-drop answer {zone_id: item_id}
    interactive_word_answers: Optional[List[str]] = None  # Learn to Read word clicks
    spelling_practice_answers: Optional[dict] = None  # Spelling practice (3 attempts per word)
    spelling_test_answers: Optional[List[str]] = None  # Spelling test answers

# Reward System Models
class Reward(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    points_cost: int
    teacher_id: str
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PointTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    points: int  # positive for earning, negative for spending
    transaction_type: str  # "earned", "manual_add", "manual_subtract", "redeemed"
    reference_id: Optional[str] = None  # assignment_id or redemption_id
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RewardRedemption(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    reward_id: str
    reward_title: str
    reward_description: str
    points_spent: int
    redeemed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "approved"  # Auto-approved

class RewardCreate(BaseModel):
    title: str
    description: str
    points_cost: int

class ManualPointsAdjustment(BaseModel):
    student_id: str
    points: int  # positive to add, negative to subtract
    description: str

# Lesson Plan Models
class LessonPlanGenerate(BaseModel):
    subject: str
    grade_level: str
    topic: str

class LessonPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    subject: str
    grade_level: str
    topic: str
    content: str
    teacher_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Message Models
class MessageCreate(BaseModel):
    recipient_id: str
    content: str

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str
    content: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read: bool = False

# Token Model
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Auth Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Check if it's a teacher or student
    user = await db.users.find_one({"id": user_id})
    if user:
        return {"type": "teacher", "data": user}
    
    student = await db.students.find_one({"id": user_id})
    if student:
        return {"type": "student", "data": student}
    
    raise credentials_exception

# AI Helper Function
async def generate_assignment_with_ai(subject: str, grade_level: str, topic: str, coding_level: Optional[int] = None, youtube_url: Optional[str] = None):
    try:
        # Initialize Gemini chat
        chat = LlmChat(
            api_key=os.environ['GEMINI_API_KEY'],
            session_id=f"assignment_{uuid.uuid4()}",
            system_message="You are an expert educational content creator for homeschool teachers."
        ).with_model("gemini", "gemini-2.5-pro")
        
        if subject.lower() == "learn to code" and coding_level:
            if coding_level == 1:
                # Level 1: Programming Concepts (MCQ only)
                prompt = f"""
                Create a "Learn to Code - Level 1" assignment for {grade_level} students on programming concepts.
                Topic: {topic}
                
                This is for complete beginners who have never coded before. Generate 4-6 multiple-choice questions about:
                - What is programming/coding
                - Different programming languages (Python, JavaScript, HTML, etc.) and what they're used for
                - Basic concepts like websites, apps, games being made with code
                - How computers understand instructions
                
                Make it very beginner-friendly and engaging. Use simple language.
                
                Return your response in this EXACT JSON format:
                {{
                    "questions": [
                        {{
                            "question": "What is programming?",
                            "options": ["Writing instructions for computers", "Drawing pictures", "Playing games", "Reading books"],
                            "correct_answer": 0
                        }}
                    ]
                }}
                """
            elif coding_level == 2:
                # Level 2: HTML Fundamentals (code + MCQ)
                prompt = f"""
                Create a "Learn to Code - Level 2" HTML assignment for {grade_level} students.
                Topic: {topic}
                
                Generate:
                1. 2-3 multiple-choice questions about HTML basics
                2. 1-2 simple HTML coding exercises (building small HTML pages)
                
                Return your response in this EXACT JSON format:
                {{
                    "questions": [
                        {{
                            "question": "What does HTML stand for?",
                            "options": ["HyperText Markup Language", "High Tech Modern Language", "Home Tool Making Language", "Happy Time Making Language"],
                            "correct_answer": 0
                        }}
                    ],
                    "coding_exercises": [
                        {{
                            "prompt": "Create a simple HTML page with a title and paragraph about your favorite animal",
                            "language": "html",
                            "starter_code": "<!DOCTYPE html>\\n<html>\\n<head>\\n    <title></title>\\n</head>\\n<body>\\n\\n</body>\\n</html>",
                            "correct_answer": "<!DOCTYPE html>\\n<html>\\n<head>\\n    <title>My Favorite Animal</title>\\n</head>\\n<body>\\n    <h1>My Favorite Animal</h1>\\n    <p>Dogs are my favorite animals because they are loyal and friendly.</p>\\n</body>\\n</html>",
                            "explanation": "This shows proper HTML structure with title, heading, and paragraph tags."
                        }}
                    ]
                }}
                """
            elif coding_level == 3:
                # Level 3: JavaScript Basics
                prompt = f"""
                Create a "Learn to Code - Level 3" JavaScript assignment for {grade_level} students.
                Topic: {topic}
                
                Generate:
                1. 2-3 multiple-choice questions about JavaScript basics
                2. 1-2 simple JavaScript coding exercises
                
                Return your response in this EXACT JSON format:
                {{
                    "questions": [
                        {{
                            "question": "What is JavaScript mainly used for?",
                            "options": ["Making websites interactive", "Only for games", "Only for mobile apps", "Only for robots"],
                            "correct_answer": 0
                        }}
                    ],
                    "coding_exercises": [
                        {{
                            "prompt": "Write JavaScript code to show an alert with the message 'Hello World!'",
                            "language": "javascript",
                            "starter_code": "// Write your code here\\n",
                            "correct_answer": "alert('Hello World!');",
                            "explanation": "The alert() function displays a popup message to the user."
                        }}
                    ]
                }}
                """
            elif coding_level == 4:
                # Level 4: Python Backend
                prompt = f"""
                Create a "Learn to Code - Level 4" Python backend assignment for {grade_level} students.
                Topic: {topic}
                
                Generate:
                1. 2-3 multiple-choice questions about Python and backend development
                2. 1-2 simple Python coding exercises for backend concepts
                
                Return your response in this EXACT JSON format:
                {{
                    "questions": [
                        {{
                            "question": "What is Python commonly used for?",
                            "options": ["Web backends, data science, automation", "Only games", "Only websites", "Only mobile apps"],
                            "correct_answer": 0
                        }}
                    ],
                    "coding_exercises": [
                        {{
                            "prompt": "Write Python code to create a simple function that returns a greeting message",
                            "language": "python",
                            "starter_code": "# Define a function called greet\\ndef greet(name):\\n    # Your code here\\n    pass\\n\\n# Test the function\\nprint(greet('World'))",
                            "correct_answer": "def greet(name):\\n    return f'Hello, {{name}}!'\\n\\nprint(greet('World'))",
                            "explanation": "This function takes a name parameter and returns a formatted greeting string."
                        }}
                    ]
                }}
                """
            else:
                # Fallback for invalid levels
                prompt = f"""
                Create a basic programming concepts assignment for {grade_level} students.
                
                Return your response in this EXACT JSON format:
                {{
                    "questions": [
                        {{
                            "question": "What is programming?",
                            "options": ["Writing instructions for computers", "Drawing pictures", "Playing games", "Reading books"],
                            "correct_answer": 0
                        }}
                    ]
                }}
                """
        elif subject.lower() == "reading":
            # Determine story length based on grade level
            grade_map = {
                "1st Grade": "2 short paragraphs",
                "2nd Grade": "2-3 short paragraphs",
                "3rd Grade": "3 paragraphs",
                "4th Grade": "3-4 paragraphs",
                "5th Grade": "4 paragraphs",
                "6th Grade": "4-5 paragraphs",
                "7th Grade": "5 paragraphs",
                "8th Grade": "5-6 paragraphs",
                "9th Grade": "5-6 paragraphs",
                "10th Grade": "6 paragraphs",
                "11th Grade": "6 paragraphs",
                "12th Grade": "6 paragraphs"
            }
            story_length = grade_map.get(grade_level, "3-4 paragraphs")
            
            prompt = f"""
            Create a reading assignment for {grade_level} students on the topic: {topic}
            
            Please generate:
            1. An original engaging story ({story_length}) appropriate for {grade_level} level
               - For lower grades (1st-3rd): Use simple vocabulary and short sentences
               - For middle grades (4th-6th): Use moderate vocabulary and varied sentence structure
               - For upper grades (7th-12th): Use advanced vocabulary and complex sentence structure
            2. EXACTLY 4 multiple-choice questions that mix:
               - Reading comprehension (understanding plot, theme, main idea)
               - Vocabulary in context (word meanings from the story)
            
            Return your response in this EXACT JSON format:
            {{
                "reading_passage": "The complete story text here...",
                "questions": [
                    {{
                        "question": "Question text?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 0
                    }},
                    {{
                        "question": "Question text?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 1
                    }},
                    {{
                        "question": "Question text?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 2
                    }},
                    {{
                        "question": "Question text?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 3
                    }}
                ]
            }}
            
            Make sure the story is engaging, age-appropriate, and the questions test both comprehension and vocabulary.
            """
        elif subject.lower() == "critical thinking skills":
            # Determine puzzle complexity based on grade level
            grade_complexity = {
                "1st Grade": "very simple, 3-4 items",
                "2nd Grade": "simple, 4 items",
                "3rd Grade": "simple to moderate, 4-5 items",
                "4th Grade": "moderate, 5 items",
                "5th Grade": "moderate, 5-6 items",
                "6th Grade": "moderate to challenging, 6 items",
                "7th Grade": "challenging, 6-7 items",
                "8th Grade": "challenging, 7 items",
                "9th Grade": "complex, 7-8 items",
                "10th Grade": "complex, 8 items",
                "11th Grade": "very complex, 8-9 items",
                "12th Grade": "very complex, 9-10 items"
            }
            complexity = grade_complexity.get(grade_level, "moderate, 5 items")
            
            prompt = f"""
            Create a Critical Thinking Skills drag-and-drop puzzle for {grade_level} students on the topic: {topic}
            
            Choose between logic puzzle or pattern recognition:
            
            LOGIC PUZZLE examples:
            - Arrange items by size (smallest to largest)
            - Arrange events in chronological order
            - Categorize items by properties
            - Sequence steps in a process
            
            PATTERN RECOGNITION examples:
            - Complete a color sequence (red, blue, red, blue, ?, ?)
            - Complete a number pattern (2, 4, 8, 16, ?, ?)
            - Complete a shape pattern
            - Complete an alphabetical pattern
            
            Difficulty: {complexity}
            
            Create 1 puzzle with:
            - Clear instructions
            - Items that need to be dragged (provide unique IDs like "item1", "item2", etc.)
            - Drop zones where items belong (provide unique IDs like "zone1", "zone2", etc.)
            - Each zone should have a clear label showing what goes there
            - Make it grade-appropriate and engaging
            
            Return your response in this EXACT JSON format:
            {{
                "drag_drop_puzzle": {{
                    "prompt": "Instructions for the puzzle",
                    "items": [
                        {{"id": "item1", "content": "Item text 1"}},
                        {{"id": "item2", "content": "Item text 2"}}
                    ],
                    "zones": [
                        {{"id": "zone1", "label": "Zone label 1", "correct_item_id": "item1"}},
                        {{"id": "zone2", "label": "Zone label 2", "correct_item_id": "item2"}}
                    ],
                    "explanation": "Explanation of the correct solution"
                }},
                "questions": []
            }}
            
            Make the puzzle challenging but appropriate for {grade_level}.
            """
        elif subject.lower() == "learn to read":
            prompt = f"""
            Create a "Learn to Read" mini book for 1st grade students on the topic: {topic}
            
            Generate:
            1. A simple story with EXACTLY 5-7 short sentences (1st grade reading level)
            2. 3-4 interactive word activities where students click on specific words
            
            Requirements:
            - Use simple, common words appropriate for beginning readers
            - Short sentences (5-8 words each)
            - Engaging story about {topic}
            - Activities should ask students to find and click on specific words in the story
            
            Return your response in this EXACT JSON format:
            {{
                "learn_to_read_content": {{
                    "story": [
                        "First sentence here.",
                        "Second sentence here.",
                        "Third sentence here.",
                        "Fourth sentence here.",
                        "Fifth sentence here."
                    ],
                    "activities": [
                        {{
                            "instruction": "Click on the word 'cat'",
                            "target_word": "cat",
                            "sentence_index": 0
                        }},
                        {{
                            "instruction": "Find and click the word 'run'",
                            "target_word": "run",
                            "sentence_index": 2
                        }}
                    ]
                }},
                "questions": []
            }}
            
            Make it fun and engaging for 1st graders learning to read!
            """
        elif subject.lower() == "spelling":
            # Determine word count and complexity based on grade level
            grade_word_count = {
                "1st Grade": "5-7 simple words",
                "2nd Grade": "7-9 words",
                "3rd Grade": "10 words",
                "4th Grade": "10-12 words",
                "5th Grade": "12 words",
                "6th Grade": "12-15 words",
                "7th Grade": "15 words",
                "8th Grade": "15 words",
                "9th Grade": "15-18 words",
                "10th Grade": "18 words",
                "11th Grade": "18-20 words",
                "12th Grade": "20 words"
            }
            word_count = grade_word_count.get(grade_level, "10 words")
            
            prompt = f"""
            Create a spelling assignment for {grade_level} students on the topic: {topic}
            
            Generate:
            1. A word list of {word_count} appropriate for {grade_level}
            2. Mixed exercise types: spelling test (typing), fill-in-the-blank, and multiple choice
            
            Requirements:
            - Words should be grade-appropriate and related to {topic}
            - Create a mix of all three exercise types
            - Each word should have an example sentence
            - For fill-in-blank: Create a sentence with ___ where the spelling word should go
            - For multiple choice: Provide 4 spelling options (1 correct, 3 incorrect but plausible)
            - Include 2-3 exercises per word type
            
            Return your response in this EXACT JSON format:
            {{
                "spelling_words": [
                    {{"word": "example", "example_sentence": "This is an example sentence."}},
                    {{"word": "another", "example_sentence": "Here is another word."}}
                ],
                "spelling_exercises": [
                    {{
                        "exercise_type": "typing_test",
                        "word": "example",
                        "example_sentence": "This is an example sentence.",
                        "correct_answer": "example"
                    }},
                    {{
                        "exercise_type": "fill_blank",
                        "word": "example",
                        "fill_blank_sentence": "This is an ___ sentence.",
                        "correct_answer": "example"
                    }},
                    {{
                        "exercise_type": "multiple_choice",
                        "word": "example",
                        "example_sentence": "This is an example sentence.",
                        "multiple_choice_options": ["example", "exampel", "exampl", "exmple"],
                        "correct_answer": "example"
                    }}
                ],
                "questions": []
            }}
            
            Make sure words are appropriate for {grade_level} and related to {topic}.
            """
        else:
            youtube_context = ""
            if youtube_url:
                youtube_context = f"\n\nNote: This assignment is meant to accompany a YouTube video: {youtube_url}\nCreate questions that could relate to or extend the video content."
            
            prompt = f"""
            Create an educational assignment for {grade_level} students in {subject} on the topic: {topic}{youtube_context}
            
            Generate 5-8 multiple-choice questions with 4 options each. Questions should be:
            - Appropriate for {grade_level} difficulty level
            - Focused on {topic}
            - Clear and educational
            
            Return your response in this EXACT JSON format:
            {{
                "questions": [
                    {{
                        "question": "Question text?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 0
                    }}
                ]
            }}
            
            Ensure all questions are educational and test understanding of {topic}.
            """
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse the AI response
        try:
            # Extract JSON from the response
            response_text = response.strip()
            # Find JSON block
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_text = response_text[start:end]
                result = json.loads(json_text)
                return result
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            print(f"Raw response: {response}")
            # Fallback questions
            return {
                "questions": [
                    {
                        "question": f"What is an important concept in {topic}?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 0
                    }
                ]
            }
    except Exception as e:
        print(f"Error generating assignment: {e}")
        # Return fallback content
        return {
            "questions": [
                {
                    "question": f"What is an important concept in {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0
                }
            ]
        }

async def generate_lesson_plan_with_ai(subject: str, grade_level: str, topic: str):
    try:
        chat = LlmChat(
            api_key=os.environ['GEMINI_API_KEY'],
            session_id=f"lesson_{uuid.uuid4()}",
            system_message="You are an expert curriculum designer and teacher."
        ).with_model("gemini", "gemini-2.5-pro")
        
        prompt = f"""
        Create a detailed lesson plan for {grade_level} students in {subject} on the topic: {topic}
        
        Include:
        1. Learning Objectives (2-3 clear, measurable goals)
        2. Materials Needed (list of resources and supplies)
        3. Lesson Activities (step-by-step activities with time estimates)
        4. Assessment Methods (how to evaluate student understanding)
        5. Extension Activities (optional enrichment activities)
        
        Make it practical and age-appropriate for {grade_level} students.
        Format as a structured lesson plan that a homeschool parent can easily follow.
        """
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        print(f"Error generating lesson plan: {e}")
        return f"Basic lesson plan for {subject} - {topic} at {grade_level} level. This lesson would cover fundamental concepts and include hands-on activities."

# Auth Routes
@api_router.post("/auth/teacher/register", response_model=Token)
async def register_teacher(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new teacher
    hashed_password = hash_password(user_data.password)
    user_dict = user_data.dict()
    user_dict.pop('password')
    user = User(**user_dict)
    
    # Store user with hashed password
    user_with_password = user.dict()
    user_with_password['password'] = hashed_password
    await db.users.insert_one(user_with_password)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.dict()
    }

@api_router.post("/auth/teacher/login", response_model=Token)
async def login_teacher(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['id']}, expires_delta=access_token_expires
    )
    
    # Remove password from user data
    user_dict = User(**user).dict()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

@api_router.post("/auth/student/login", response_model=Token)
async def login_student(student_data: StudentLogin):
    student = await db.students.find_one({"username": student_data.username})
    if not student or not verify_password(student_data.password, student['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": student['id']}, expires_delta=access_token_expires
    )
    
    # Remove password from student data
    student_dict = Student(**student).dict()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": student_dict
    }

# Student Management Routes
@api_router.post("/students", response_model=Student)
async def create_student(student_data: StudentCreate, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create students")
    
    # Check if username already exists
    existing_student = await db.students.find_one({"username": student_data.username})
    if existing_student:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create student
    hashed_password = hash_password(student_data.password)
    student_dict = student_data.dict()
    student_dict.pop('password')
    student_dict['teacher_id'] = current_user["data"]["id"]
    student = Student(**student_dict)
    
    # Store student with hashed password
    student_with_password = student.dict()
    student_with_password['password'] = hashed_password
    await db.students.insert_one(student_with_password)
    
    return student

@api_router.get("/students", response_model=List[Student])
async def get_students(current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view students")
    
    students = await db.students.find({"teacher_id": current_user["data"]["id"]}).to_list(1000)
    return [Student(**student) for student in students]

@api_router.delete("/students/{student_id}")
async def delete_student(student_id: str, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete students")
    
    result = await db.students.delete_one({
        "id": student_id,
        "teacher_id": current_user["data"]["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student deleted successfully"}

# Assignment Routes
@api_router.post("/assignments/generate", response_model=Assignment)
async def generate_assignment(assignment_data: AssignmentGenerate, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can generate assignments")
    
    # Generate assignment using AI
    ai_result = await generate_assignment_with_ai(
        assignment_data.subject,
        assignment_data.grade_level,
        assignment_data.topic,
        assignment_data.coding_level,
        assignment_data.youtube_url
    )
    
    # Create assignment object
    drag_drop_puzzle = None
    if ai_result.get("drag_drop_puzzle"):
        drag_drop_puzzle = DragDropPuzzle(**ai_result["drag_drop_puzzle"])
    
    learn_to_read_content = None
    if ai_result.get("learn_to_read_content"):
        learn_to_read_content = LearnToReadContent(**ai_result["learn_to_read_content"])
    
    spelling_words = None
    if ai_result.get("spelling_words"):
        spelling_words = [SpellingWord(**w) for w in ai_result["spelling_words"]]
    
    spelling_exercises = None
    if ai_result.get("spelling_exercises"):
        spelling_exercises = [SpellingExercise(**ex) for ex in ai_result["spelling_exercises"]]
    
    assignment = Assignment(
        title=f"{assignment_data.subject} - {assignment_data.topic}" + (f" (Level {assignment_data.coding_level})" if assignment_data.coding_level else ""),
        subject=assignment_data.subject,
        grade_level=assignment_data.grade_level,
        topic=assignment_data.topic,
        questions=[Question(**q) for q in ai_result["questions"]],
        reading_passage=ai_result.get("reading_passage"),
        coding_level=assignment_data.coding_level,
        coding_exercises=[CodingExercise(**ex) for ex in ai_result.get("coding_exercises", [])],
        drag_drop_puzzle=drag_drop_puzzle,
        learn_to_read_content=learn_to_read_content,
        spelling_exercises=spelling_exercises,
        spelling_words=spelling_words,
        youtube_url=assignment_data.youtube_url,
        teacher_id=current_user["data"]["id"]
    )
    
    # Save to database
    await db.assignments.insert_one(assignment.dict())
    
    return assignment

@api_router.post("/assignments/assign")
async def assign_assignment(assign_data: AssignmentAssign, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can assign assignments")
    
    # Verify assignment belongs to teacher
    assignment = await db.assignments.find_one({
        "id": assign_data.assignment_id,
        "teacher_id": current_user["data"]["id"]
    })
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Create student assignments
    student_assignments = []
    for student_id in assign_data.student_ids:
        student_assignment = StudentAssignment(
            assignment_id=assign_data.assignment_id,
            student_id=student_id,
            teacher_id=current_user["data"]["id"]
        )
        student_assignments.append(student_assignment.dict())
    
    if student_assignments:
        await db.student_assignments.insert_many(student_assignments)
    
    return {"message": f"Assignment assigned to {len(student_assignments)} students"}

@api_router.get("/assignments", response_model=List[Assignment])
async def get_assignments(current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view assignments")
    
    assignments = await db.assignments.find({"teacher_id": current_user["data"]["id"]}).to_list(1000)
    return [Assignment(**assignment) for assignment in assignments]

# Student Assignment Routes
@api_router.get("/student/assignments", response_model=List[dict])
async def get_student_assignments(current_user=Depends(get_current_user)):
    if current_user["type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their assignments")
    
    # Get student assignments
    student_assignments = await db.student_assignments.find({
        "student_id": current_user["data"]["id"]
    }).to_list(1000)
    
    # Get assignment details
    result = []
    for sa in student_assignments:
        assignment = await db.assignments.find_one({"id": sa["assignment_id"]})
        if assignment:
            result.append({
                "student_assignment_id": sa["id"],
                "assignment": Assignment(**assignment).dict(),
                "completed": sa["completed"],
                "score": sa.get("score"),
                "submitted_at": sa.get("submitted_at"),
                "assigned_at": sa["assigned_at"]
            })
    
    return result

@api_router.get("/student/assignments/{student_assignment_id}", response_model=dict)
async def get_student_assignment_by_id(student_assignment_id: str, current_user=Depends(get_current_user)):
    if current_user["type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their assignments")
    
    # Get student assignment
    student_assignment = await db.student_assignments.find_one({
        "id": student_assignment_id,
        "student_id": current_user["data"]["id"]
    })
    
    if not student_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Get assignment details
    assignment = await db.assignments.find_one({"id": student_assignment["assignment_id"]})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment details not found")
    
    return {
        "student_assignment_id": student_assignment["id"],
        "assignment": Assignment(**assignment).dict(),
        "completed": student_assignment["completed"],
        "score": student_assignment.get("score"),
        "submitted_at": student_assignment.get("submitted_at"),
        "assigned_at": student_assignment["assigned_at"],
        "answers": student_assignment.get("answers", []),
        "coding_answers": student_assignment.get("coding_answers", []),
        "drag_drop_answer": student_assignment.get("drag_drop_answer", {}),
        "interactive_word_answers": student_assignment.get("interactive_word_answers", []),
        "spelling_answers": student_assignment.get("spelling_answers", [])
    }

@api_router.post("/student/assignments/submit")
async def submit_assignment(submission: SubmissionRequest, current_user=Depends(get_current_user)):
    if current_user["type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")
    
    # Get student assignment
    student_assignment = await db.student_assignments.find_one({
        "id": submission.student_assignment_id,
        "student_id": current_user["data"]["id"]
    })
    
    if not student_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if student_assignment["completed"]:
        raise HTTPException(status_code=400, detail="Assignment already submitted")
    
    # Get assignment details for grading
    assignment = await db.assignments.find_one({"id": student_assignment["assignment_id"]})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment details not found")
    
    # Calculate score for MCQ questions
    mcq_correct = 0
    total_mcq = len(assignment["questions"])
    
    if submission.answers:
        for i, answer in enumerate(submission.answers):
            if i < total_mcq and answer == assignment["questions"][i]["correct_answer"]:
                mcq_correct += 1
    
    # Calculate score for coding exercises (simple string matching for now)
    coding_correct = 0
    total_coding = len(assignment.get("coding_exercises", []))
    
    if submission.coding_answers and total_coding > 0:
        for i, code_answer in enumerate(submission.coding_answers):
            if i < total_coding:
                correct_code = assignment["coding_exercises"][i]["correct_answer"]
                # Simple string matching (normalize whitespace)
                if code_answer.strip().replace(" ", "").replace("\n", "") == correct_code.strip().replace(" ", "").replace("\n", ""):
                    coding_correct += 1
    
    # Calculate score for drag-and-drop puzzle
    drag_drop_correct = 0
    total_drag_drop = 0
    
    if assignment.get("drag_drop_puzzle") and submission.drag_drop_answer:
        puzzle = assignment["drag_drop_puzzle"]
        total_drag_drop = len(puzzle["zones"])
        
        # Check each zone to see if correct item was placed
        for zone in puzzle["zones"]:
            zone_id = zone["id"]
            correct_item_id = zone["correct_item_id"]
            student_answer = submission.drag_drop_answer.get(zone_id)
            
            if student_answer == correct_item_id:
                drag_drop_correct += 1
    
    # Calculate score for Learn to Read interactive activities
    learn_to_read_correct = 0
    total_learn_to_read = 0
    
    if assignment.get("learn_to_read_content") and submission.interactive_word_answers:
        activities = assignment["learn_to_read_content"]["activities"]
        total_learn_to_read = len(activities)
        
        for i, activity in enumerate(activities):
            if i < len(submission.interactive_word_answers):
                # Check if student clicked the correct word
                if submission.interactive_word_answers[i].lower() == activity["target_word"].lower():
                    learn_to_read_correct += 1
    
    # Calculate score for Spelling exercises
    spelling_correct = 0
    total_spelling = 0
    
    if assignment.get("spelling_exercises") and submission.spelling_answers:
        total_spelling = len(assignment["spelling_exercises"])
        
        for i, exercise in enumerate(assignment["spelling_exercises"]):
            if i < len(submission.spelling_answers):
                student_answer = submission.spelling_answers[i].strip().lower()
                correct_answer = exercise["correct_answer"].strip().lower()
                
                if student_answer == correct_answer:
                    spelling_correct += 1
    
    # Calculate overall score
    total_questions = total_mcq + total_coding + total_drag_drop + total_learn_to_read + total_spelling
    total_correct = mcq_correct + coding_correct + drag_drop_correct + learn_to_read_correct + spelling_correct
    score = (total_correct / total_questions) * 100 if total_questions > 0 else 0
    
    # Award points for grades 85% or higher
    points_earned = 0
    if score >= 85:
        points_earned = 5
        
        # Create point transaction
        point_transaction = PointTransaction(
            student_id=current_user["data"]["id"],
            points=points_earned,
            transaction_type="earned",
            reference_id=student_assignment["assignment_id"],
            description=f"Earned 5 points for scoring {round(score)}% on assignment"
        )
        await db.point_transactions.insert_one(point_transaction.dict())
    
    # Update student assignment
    await db.student_assignments.update_one(
        {"id": submission.student_assignment_id},
        {
            "$set": {
                "answers": submission.answers,
                "coding_answers": submission.coding_answers,
                "drag_drop_answer": submission.drag_drop_answer,
                "interactive_word_answers": submission.interactive_word_answers,
                "spelling_answers": submission.spelling_answers,
                "score": score,
                "completed": True,
                "submitted_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": "Assignment submitted successfully",
        "score": score,
        "mcq_correct": mcq_correct,
        "coding_correct": coding_correct,
        "drag_drop_correct": drag_drop_correct,
        "learn_to_read_correct": learn_to_read_correct,
        "spelling_correct": spelling_correct,
        "total_mcq": total_mcq,
        "total_coding": total_coding,
        "total_drag_drop": total_drag_drop,
        "total_learn_to_read": total_learn_to_read,
        "total_spelling": total_spelling,
        "total_questions": total_questions
    }

# Lesson Plan Routes
@api_router.post("/lesson-plans/generate", response_model=LessonPlan)
async def generate_lesson_plan(lesson_data: LessonPlanGenerate, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can generate lesson plans")
    
    # Generate lesson plan using AI
    content = await generate_lesson_plan_with_ai(
        lesson_data.subject,
        lesson_data.grade_level,
        lesson_data.topic
    )
    
    # Create lesson plan object
    lesson_plan = LessonPlan(
        title=f"{lesson_data.subject} - {lesson_data.topic}",
        subject=lesson_data.subject,
        grade_level=lesson_data.grade_level,
        topic=lesson_data.topic,
        content=content,
        teacher_id=current_user["data"]["id"]
    )
    
    # Save to database
    await db.lesson_plans.insert_one(lesson_plan.dict())
    
    return lesson_plan

@api_router.get("/lesson-plans", response_model=List[LessonPlan])
async def get_lesson_plans(current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view lesson plans")
    
    lesson_plans = await db.lesson_plans.find({"teacher_id": current_user["data"]["id"]}).to_list(1000)
    return [LessonPlan(**lp) for lp in lesson_plans]

# Gradebook Routes
@api_router.get("/gradebook")
async def get_gradebook(current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view gradebook")
    
    # Get all students
    students = await db.students.find({"teacher_id": current_user["data"]["id"]}).to_list(1000)
    
    # Get all completed assignments for each student
    gradebook = []
    for student in students:
        student_assignments = await db.student_assignments.find({
            "student_id": student["id"],
            "completed": True
        }).to_list(1000)
        
        assignments_with_details = []
        for sa in student_assignments:
            assignment = await db.assignments.find_one({"id": sa["assignment_id"]})
            if assignment:
                assignments_with_details.append({
                    "assignment_title": assignment["title"],
                    "subject": assignment["subject"],
                    "score": sa["score"],
                    "submitted_at": sa["submitted_at"]
                })
        
        gradebook.append({
            "student": Student(**student).dict(),
            "assignments": assignments_with_details
        })
    
    return gradebook

# Messaging Routes
@api_router.post("/messages", response_model=Message)
async def send_message(message_data: MessageCreate, current_user=Depends(get_current_user)):
    message = Message(
        sender_id=current_user["data"]["id"],
        recipient_id=message_data.recipient_id,
        content=message_data.content
    )
    
    await db.messages.insert_one(message.dict())
    return message

@api_router.get("/messages/{contact_id}", response_model=List[Message])
async def get_messages(contact_id: str, current_user=Depends(get_current_user)):
    messages = await db.messages.find({
        "$or": [
            {"sender_id": current_user["data"]["id"], "recipient_id": contact_id},
            {"sender_id": contact_id, "recipient_id": current_user["data"]["id"]}
        ]
    }).sort("sent_at", 1).to_list(1000)
    
    # Mark messages as read
    await db.messages.update_many(
        {"sender_id": contact_id, "recipient_id": current_user["data"]["id"], "read": False},
        {"$set": {"read": True}}
    )
    
    return [Message(**message) for message in messages]

@api_router.get("/messages", response_model=List[dict])
async def get_conversations(current_user=Depends(get_current_user)):
    if current_user["type"] == "teacher":
        # Get all students for this teacher
        students = await db.students.find({"teacher_id": current_user["data"]["id"]}).to_list(1000)
        contacts = [{"id": s["id"], "name": f"{s['first_name']} {s['last_name']}", "type": "student"} for s in students]
    else:
        # Get teacher for this student
        teacher = await db.users.find_one({"id": current_user["data"]["teacher_id"]})
        contacts = [{"id": teacher["id"], "name": f"{teacher['first_name']} {teacher['last_name']}", "type": "teacher"}] if teacher else []
    
    # Get last message with each contact
    conversations = []
    for contact in contacts:
        last_message = await db.messages.find_one(
            {
                "$or": [
                    {"sender_id": current_user["data"]["id"], "recipient_id": contact["id"]},
                    {"sender_id": contact["id"], "recipient_id": current_user["data"]["id"]}
                ]
            },
            sort=[("sent_at", -1)]
        )
        
        conversations.append({
            "contact": contact,
            "last_message": Message(**last_message).dict() if last_message else None
        })
    
    return conversations

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Homeschool Hub API"}

# Include the router in the main app
# Reward System Routes
@api_router.get("/rewards", response_model=List[Reward])
async def get_rewards(current_user=Depends(get_current_user)):
    # Both teachers and students can view rewards
    if current_user["type"] == "teacher":
        rewards = await db.rewards.find({"teacher_id": current_user["data"]["id"]}).to_list(1000)
    else:
        # Students see rewards from their teacher
        student = await db.students.find_one({"id": current_user["data"]["id"]})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        rewards = await db.rewards.find({"teacher_id": student["teacher_id"], "active": True}).to_list(1000)
    
    return [Reward(**reward) for reward in rewards]

@api_router.post("/rewards", response_model=Reward)
async def create_reward(reward_data: RewardCreate, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create rewards")
    
    reward = Reward(
        title=reward_data.title,
        description=reward_data.description,
        points_cost=reward_data.points_cost,
        teacher_id=current_user["data"]["id"]
    )
    
    await db.rewards.insert_one(reward.dict())
    return reward

@api_router.put("/rewards/{reward_id}", response_model=Reward)
async def update_reward(reward_id: str, reward_data: RewardCreate, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can update rewards")
    
    reward = await db.rewards.find_one({"id": reward_id, "teacher_id": current_user["data"]["id"]})
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    await db.rewards.update_one(
        {"id": reward_id},
        {"$set": {
            "title": reward_data.title,
            "description": reward_data.description,
            "points_cost": reward_data.points_cost
        }}
    )
    
    updated_reward = await db.rewards.find_one({"id": reward_id})
    return Reward(**updated_reward)

@api_router.delete("/rewards/{reward_id}")
async def delete_reward(reward_id: str, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete rewards")
    
    result = await db.rewards.delete_one({"id": reward_id, "teacher_id": current_user["data"]["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    return {"message": "Reward deleted successfully"}

@api_router.get("/student/points")
async def get_student_points(current_user=Depends(get_current_user)):
    if current_user["type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their points")
    
    # Get all transactions
    transactions = await db.point_transactions.find({"student_id": current_user["data"]["id"]}).to_list(1000)
    
    # Calculate total points
    total_points = sum(t["points"] for t in transactions)
    
    # Get redemption history
    redemptions = await db.reward_redemptions.find({"student_id": current_user["data"]["id"]}).to_list(1000)
    
    return {
        "total_points": total_points,
        "transactions": [PointTransaction(**t) for t in transactions],
        "redemptions": [RewardRedemption(**r) for r in redemptions]
    }

@api_router.post("/student/redeem")
async def redeem_reward(reward_id: str, current_user=Depends(get_current_user)):
    if current_user["type"] != "student":
        raise HTTPException(status_code=403, detail="Only students can redeem rewards")
    
    # Get reward
    reward = await db.rewards.find_one({"id": reward_id, "active": True})
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found or inactive")
    
    # Calculate current points
    transactions = await db.point_transactions.find({"student_id": current_user["data"]["id"]}).to_list(1000)
    total_points = sum(t["points"] for t in transactions)
    
    # Check if student has enough points
    if total_points < reward["points_cost"]:
        raise HTTPException(status_code=400, detail=f"Not enough points. You have {total_points}, need {reward['points_cost']}")
    
    # Create redemption record
    redemption = RewardRedemption(
        student_id=current_user["data"]["id"],
        reward_id=reward["id"],
        reward_title=reward["title"],
        reward_description=reward["description"],
        points_spent=reward["points_cost"]
    )
    await db.reward_redemptions.insert_one(redemption.dict())
    
    # Deduct points
    point_transaction = PointTransaction(
        student_id=current_user["data"]["id"],
        points=-reward["points_cost"],
        transaction_type="redeemed",
        reference_id=redemption.id,
        description=f"Redeemed: {reward['title']}"
    )
    await db.point_transactions.insert_one(point_transaction.dict())
    
    return {
        "message": "Reward redeemed successfully!",
        "redemption": redemption,
        "remaining_points": total_points - reward["points_cost"]
    }

@api_router.post("/teacher/points")
async def adjust_student_points(adjustment: ManualPointsAdjustment, current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can adjust points")
    
    # Verify student belongs to teacher
    student = await db.students.find_one({"id": adjustment.student_id, "teacher_id": current_user["data"]["id"]})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create transaction
    transaction_type = "manual_add" if adjustment.points > 0 else "manual_subtract"
    point_transaction = PointTransaction(
        student_id=adjustment.student_id,
        points=adjustment.points,
        transaction_type=transaction_type,
        description=adjustment.description
    )
    await db.point_transactions.insert_one(point_transaction.dict())
    
    # Get new total
    transactions = await db.point_transactions.find({"student_id": adjustment.student_id}).to_list(1000)
    total_points = sum(t["points"] for t in transactions)
    
    return {
        "message": "Points adjusted successfully",
        "points_adjusted": adjustment.points,
        "new_total": total_points
    }

@api_router.get("/teacher/student-points")
async def get_all_students_points(current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view student points")
    
    # Get all students for this teacher
    students = await db.students.find({"teacher_id": current_user["data"]["id"]}).to_list(1000)
    
    result = []
    for student in students:
        # Get transactions
        transactions = await db.point_transactions.find({"student_id": student["id"]}).to_list(1000)
        total_points = sum(t["points"] for t in transactions)
        
        # Get redemptions
        redemptions = await db.reward_redemptions.find({"student_id": student["id"]}).to_list(1000)
        
        result.append({
            "student_id": student["id"],
            "student_name": f"{student['first_name']} {student['last_name']}",
            "username": student["username"],
            "total_points": total_points,
            "transactions": [PointTransaction(**t) for t in transactions],
            "redemptions": [RewardRedemption(**r) for r in redemptions]
        })
    
    return result

@api_router.post("/teacher/initialize-rewards")
async def initialize_default_rewards(current_user=Depends(get_current_user)):
    if current_user["type"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can initialize rewards")
    
    # Check if teacher already has rewards
    existing_rewards = await db.rewards.find({"teacher_id": current_user["data"]["id"]}).to_list(1)
    if existing_rewards:
        return {"message": "Rewards already initialized"}
    
    # Create default rewards
    default_rewards = [
        {"title": "1 Hour of Game Time", "description": "Play games for 1 hour", "points_cost": 50},
        {"title": "2 Hours of Game Time", "description": "Play games for 2 hours", "points_cost": 100},
        {"title": "12oz Coke", "description": "Enjoy a cold 12oz Coke", "points_cost": 250},
        {"title": "TV at Night", "description": "Watch TV at night for one night", "points_cost": 300},
        {"title": "One Day Off School", "description": "Take a break! One day off from school", "points_cost": 400}
    ]
    
    rewards_to_insert = []
    for reward_data in default_rewards:
        reward = Reward(
            title=reward_data["title"],
            description=reward_data["description"],
            points_cost=reward_data["points_cost"],
            teacher_id=current_user["data"]["id"]
        )
        rewards_to_insert.append(reward.dict())
    
    await db.rewards.insert_many(rewards_to_insert)
    
    return {"message": "Default rewards initialized successfully", "count": len(rewards_to_insert)}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

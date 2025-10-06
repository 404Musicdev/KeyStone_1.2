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

class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer: int  # Index of correct answer (0-3)

class Assignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    subject: str
    grade_level: str
    topic: str
    questions: List[Question]
    reading_passage: Optional[str] = None
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
    answers: Optional[List[int]] = None  # Student's answers (indices)
    score: Optional[float] = None
    completed: bool = False

class SubmissionRequest(BaseModel):
    student_assignment_id: str
    answers: List[int]

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
async def generate_assignment_with_ai(subject: str, grade_level: str, topic: str, youtube_url: Optional[str] = None):
    try:
        # Initialize Gemini chat
        chat = LlmChat(
            api_key=os.environ['GEMINI_API_KEY'],
            session_id=f"assignment_{uuid.uuid4()}",
            system_message="You are an expert educational content creator for homeschool teachers."
        ).with_model("gemini", "gemini-2.5-pro")
        
        if subject.lower() == "learning to read":
            prompt = f"""
            Create a "Learning to Read" assignment for {grade_level} students on the topic: {topic}
            
            This is for young students who are still learning to read. Please generate:
            1. A very simple reading passage using only 10-14 words total, focusing on basic phonics and sight words
            2. 2 simple multiple-choice questions about the passage (very basic comprehension)
            
            The reading passage should:
            - Use simple, common words that young children can sound out
            - Be about something familiar (animals, family, toys, etc.)
            - Have short, simple sentences
            - Be encouraging and fun
            
            Example words to use: cat, dog, run, play, mom, dad, big, red, go, see, like, has, is, the, a
            
            Return your response in this EXACT JSON format:
            {{
                "reading_passage": "The simple passage here using only 10-14 words...",
                "questions": [
                    {{
                        "question": "Simple question about the passage?",
                        "options": ["Yes", "No", "Maybe", "I don't know"],
                        "correct_answer": 0
                    }},
                    {{
                        "question": "Another simple question?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 1
                    }}
                ]
            }}
            
            Make sure everything is appropriate for beginning readers in {grade_level}.
            """
        elif subject.lower() == "reading":
            prompt = f"""
            Create a reading assignment for {grade_level} students on the topic: {topic}
            
            Please generate:
            1. An original short story (2-4 paragraphs) appropriate for {grade_level} level
            2. 4 multiple-choice questions about the story (plot, characters, details)
            
            Return your response in this EXACT JSON format:
            {{
                "reading_passage": "The complete story text here...",
                "questions": [
                    {{
                        "question": "Question text?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 0
                    }}
                ]
            }}
            
            Make sure the story is engaging and age-appropriate for {grade_level}.
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
        assignment_data.youtube_url
    )
    
    # Create assignment object
    assignment = Assignment(
        title=f"{assignment_data.subject} - {assignment_data.topic}",
        subject=assignment_data.subject,
        grade_level=assignment_data.grade_level,
        topic=assignment_data.topic,
        questions=[Question(**q) for q in ai_result["questions"]],
        reading_passage=ai_result.get("reading_passage"),
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
    
    # Calculate score
    correct_answers = 0
    total_questions = len(assignment["questions"])
    
    for i, answer in enumerate(submission.answers):
        if i < total_questions and answer == assignment["questions"][i]["correct_answer"]:
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Update student assignment
    await db.student_assignments.update_one(
        {"id": submission.student_assignment_id},
        {
            "$set": {
                "answers": submission.answers,
                "score": score,
                "completed": True,
                "submitted_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": "Assignment submitted successfully",
        "score": score,
        "correct_answers": correct_answers,
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

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import uuid
from prometheus_client import Counter, Histogram, start_http_server
import sys

# Add parent directory to path to import database modules
sys.path.append("..")
from database import models, database, crud
from database.database import get_db
from tasks.tasks import analyze_video, generate_user_stats

# API models
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class WorkoutBase(BaseModel):
    title: str
    description: Optional[str] = None
    workout_type: str

class WorkoutCreate(WorkoutBase):
    pass

class Workout(WorkoutBase):
    id: int
    user_id: int
    created_at: datetime
    video_path: Optional[str] = None
    analysis_status: str
    analysis_results: Optional[dict] = None
    
    class Config:
        orm_mode = True

# Initialize FastAPI app
app = FastAPI(
    title="Fitness App API",
    description="Backend API for fitness mobile app with ML video analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you would specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the web UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])

# Start metrics server on a different port to avoid conflict with the API
start_http_server(8888)

# Secret key and algorithm for JWT
SECRET_KEY = "YOUR_SECRET_KEY"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Authentication functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# API Endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user_email = crud.get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_username = crud.get_user_by_username(db, username=user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    return crud.create_user(db=db, email=user.email, username=user.username, password=user.password)

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user

@app.post("/workouts/", response_model=Workout, status_code=status.HTTP_201_CREATED)
async def create_workout(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    workout_type: str = Form(...),
    video: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Create a unique filename
    file_extension = os.path.splitext(video.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(await video.read())
    
    # Create workout record in database
    workout = crud.create_workout(
        db=db,
        user_id=current_user.id,
        title=title,
        description=description,
        workout_type=workout_type,
        video_path=file_path
    )
    
    # Trigger background task for video analysis using Celery
    background_tasks.add_task(analyze_video.delay, workout.id, file_path)
    
    return workout

@app.get("/workouts/", response_model=List[Workout])
async def read_workouts(
    skip: int = 0, 
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    workouts = crud.get_user_workouts(db, user_id=current_user.id, skip=skip, limit=limit)
    return workouts

@app.get("/workouts/{workout_id}", response_model=Workout)
async def read_workout(
    workout_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    workout = crud.get_workout(db, workout_id=workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    if workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this workout")
    return workout

@app.get("/users/me/stats")
async def get_user_stats(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user)
):
    # Trigger background task to generate user statistics
    task = generate_user_stats.delay(current_user.id)
    
    return {
        "message": "Statistics generation started",
        "task_id": task.id
    }

# Serve uploaded videos (for testing purposes only)
@app.get("/uploads/{filename}")
async def get_upload(
    filename: str,
    current_user = Depends(get_current_active_user)
):
    return FileResponse(f"uploads/{filename}")

# Serve the web UI
@app.get("/")
async def get_ui():
    return FileResponse("static/index.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Documentation endpoints are automatically generated by FastAPI

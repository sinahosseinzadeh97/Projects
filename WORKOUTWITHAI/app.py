import os
import uuid
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import redis

# ML imports
import cv2
import numpy as np
import mediapipe as mp
from huggingface_hub import InferenceClient
import openai
from pydub import AudioSegment
from pydub.playback import play

# Celery for background tasks
from celery import Celery
from celery.result import AsyncResult

# Database models and utilities
from database.models import User, Video, Analysis
from database.database import get_db, engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Fitness Video Analysis System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure AWS S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)
S3_BUCKET = os.getenv('S3_BUCKET_NAME', 'fitness-analysis-videos')

# Configure Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0
)

# Configure Celery
celery_app = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure Hugging Face client
hf_client = InferenceClient(
    os.getenv('HF_API_URL', 'https://api-inference.huggingface.co/models/fitness-classification')
)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Celery Tasks
@celery_app.task(name="tasks.process_video")
def process_video(video_id: str, s3_key: str) -> Dict[str, Any]:
    """
    Process a fitness video:
    1. Download from S3
    2. Extract frames
    3. Run pose estimation
    4. Classify exercise
    5. Generate feedback
    6. Create AR overlays
    7. Synthesize audio feedback
    8. Upload results to S3
    """
    try:
        logger.info(f"Starting processing of video {video_id}")
        
        # Download video from S3
        local_video_path = f"/tmp/{video_id}.mp4"
        s3_client.download_file(S3_BUCKET, s3_key, local_video_path)
        
        # Process video
        results = analyze_video(local_video_path, video_id)
        
        # Update database with results
        with Session(engine) as db:
            analysis = db.query(Analysis).filter(Analysis.video_id == video_id).first()
            if analysis:
                analysis.status = "completed"
                analysis.results = results
                analysis.completed_at = datetime.utcnow()
                db.commit()
        
        return {"status": "success", "video_id": video_id, "results": results}
    
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")
        
        # Update database with error
        with Session(engine) as db:
            analysis = db.query(Analysis).filter(Analysis.video_id == video_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error = str(e)
                db.commit()
        
        return {"status": "error", "video_id": video_id, "error": str(e)}

def analyze_video(video_path: str, video_id: str) -> Dict[str, Any]:
    """Analyze a fitness video with pose estimation and exercise classification"""
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Error opening video file {video_path}")
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Set up output video
    output_path = f"/tmp/{video_id}_analyzed.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Set up pose detection
    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        # Process frames
        frame_count = 0
        keypoints_sequence = []
        joint_angles_sequence = []
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            # Process every 3rd frame to speed up analysis
            if frame_count % 3 == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Run pose detection
                results = pose.process(frame_rgb)
                
                if results.pose_landmarks:
                    # Extract keypoints
                    keypoints = []
                    for landmark in results.pose_landmarks.landmark:
                        keypoints.append({
                            'x': landmark.x,
                            'y': landmark.y,
                            'z': landmark.z,
                            'visibility': landmark.visibility
                        })
                    keypoints_sequence.append(keypoints)
                    
                    # Calculate joint angles
                    joint_angles = calculate_joint_angles(results.pose_landmarks.landmark)
                    joint_angles_sequence.append(joint_angles)
                    
                    # Draw pose landmarks on frame
                    annotated_frame = create_ar_overlay(frame.copy(), results, joint_angles)
                    out.write(annotated_frame)
                else:
                    # If no pose detected, write original frame
                    out.write(frame)
            else:
                # Write original frame for skipped frames
                out.write(frame)
            
            frame_count += 1
            
            # Show progress
            if frame_count % 30 == 0:
                logger.info(f"Processed {frame_count}/{total_frames} frames")
    
    # Release resources
    cap.release()
    out.release()
    
    # Upload processed video to S3
    s3_client.upload_file(
        output_path, 
        S3_BUCKET, 
        f"processed/{video_id}_analyzed.mp4"
    )
    
    # Classify exercise based on keypoints and joint angles
    exercise_classification = classify_exercise(keypoints_sequence, joint_angles_sequence)
    
    # Generate feedback using OpenAI
    feedback = generate_feedback(exercise_classification, joint_angles_sequence)
    
    # Generate TTS audio for feedback
    audio_path = generate_audio_feedback(feedback, video_id)
    
    # Upload audio to S3
    s3_client.upload_file(
        audio_path,
        S3_BUCKET,
        f"audio/{video_id}_feedback.mp3"
    )
    
    # Return analysis results
    return {
        "exercise_type": exercise_classification["exercise_type"],
        "confidence": exercise_classification["confidence"],
        "form_quality": exercise_classification["form_quality"],
        "repetitions": exercise_classification["repetitions"],
        "feedback": feedback,
        "processed_video_url": f"processed/{video_id}_analyzed.mp4",
        "audio_feedback_url": f"audio/{video_id}_feedback.mp3",
        "total_frames_processed": frame_count
    }

def calculate_joint_angles(landmarks) -> Dict[str, float]:
    """Calculate key joint angles from pose landmarks"""
    # Helper function to calculate angle between three points
    def calculate_angle(a, b, c):
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    # Calculate key angles
    joint_angles = {}
    
    # Left knee angle
    joint_angles["left_knee"] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    )
    
    # Right knee angle
    joint_angles["right_knee"] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    )
    
    # Left elbow angle
    joint_angles["left_elbow"] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    )
    
    # Right elbow angle
    joint_angles["right_elbow"] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    )
    
    # Left hip angle
    joint_angles["left_hip"] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    )
    
    # Right hip angle
    joint_angles["right_hip"] = calculate_angle(
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    )
    
    return joint_angles

def create_ar_overlay(frame, pose_results, joint_angles):
    """Create AR overlay with form feedback on video frame"""
    # Draw pose landmarks
    mp_drawing.draw_landmarks(
        frame,
        pose_results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
    )
    
    # Add joint angle information
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    color = (255, 255, 255)
    thickness = 1
    
    # Display knee angles
    left_knee_landmark = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_knee_px = (int(left_knee_landmark.x * frame.shape[1]), int(left_knee_landmark.y * frame.shape[0]))
    cv2.putText(frame, f"{joint_angles['left_knee']:.1f}°", 
                (left_knee_px[0] + 10, left_knee_px[1]), 
                font, font_scale, color, thickness)
    
    right_knee_landmark = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    right_knee_px = (int(right_knee_landmark.x * frame.shape[1]), int(right_knee_landmark.y * frame.shape[0]))
    cv2.putText(frame, f"{joint_angles['right_knee']:.1f}°", 
                (right_knee_px[0] + 10, right_knee_px[1]), 
                font, font_scale, color, thickness)
    
    # Display elbow angles
    left_elbow_landmark = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    left_elbow_px = (int(left_elbow_landmark.x * frame.shape[1]), int(left_elbow_landmark.y * frame.shape[0]))
    cv2.putText(frame, f"{joint_angles['left_elbow']:.1f}°", 
                (left_elbow_px[0] + 10, left_elbow_px[1]), 
                font, font_scale, color, thickness)
    
    right_elbow_landmark = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
    right_elbow_px = (int(right_elbow_landmark.x * frame.shape[1]), int(right_elbow_landmark.y * frame.shape[0]))
    cv2.putText(frame, f"{joint_angles['right_elbow']:.1f}°", 
                (right_elbow_px[0] + 10, right_elbow_px[1]), 
                font, font_scale, color, thickness)
    
    # Identify form issues based on joint angles
    # This is a simplified example - in a real application, you'd have 
    # exercise-specific rules for form checking
    form_issues = []
    
    # Check knee angles (example for squats)
    knee_angle_avg = (joint_angles['left_knee'] + joint_angles['right_knee']) / 2
    if knee_angle_avg > 100:
        form_issues.append("Bend knees more")
    elif knee_angle_avg < 60:
        form_issues.append("Knees too bent")
    
    # Add form feedback to frame
    y_offset = 30
    for issue in form_issues:
        cv2.putText(frame, issue, (20, y_offset), 
                    font, font_scale * 1.5, (0, 0, 255), thickness + 1)
        y_offset += 30
    
    return frame

def classify_exercise(keypoints_sequence, joint_angles_sequence):
    """Classify exercise type using Hugging Face model"""
    # Prepare data for classification
    # In a real application, you would properly format the data according to
    # the model's expected input structure
    classification_data = {
        "keypoints": keypoints_sequence[::10],  # Sample every 10th frame to reduce data
        "joint_angles": joint_angles_sequence[::10]
    }
    
    try:
        # Call Hugging Face model
        # This is a placeholder - in reality, you'd need to format the data according to model requirements
        response = hf_client.post(json=classification_data)
        
        # Process response
        if isinstance(response, dict) and "error" in response:
            logger.error(f"Error from Hugging Face API: {response['error']}")
            # Fallback classification
            return {
                "exercise_type": "unknown",
                "confidence": 0.0,
                "form_quality": "unknown",
                "repetitions": 0
            }
        
        # Extract classification results
        # This assumes the model returns a specific format - adjust as needed for your model
        exercise_type = response.get("exercise_type", "unknown")
        confidence = response.get("confidence", 0.0)
        form_quality = response.get("form_quality", "unknown")
        repetitions = response.get("repetitions", 0)
        
        return {
            "exercise_type": exercise_type,
            "confidence": confidence,
            "form_quality": form_quality,
            "repetitions": repetitions
        }
        
    except Exception as e:
        logger.error(f"Error calling Hugging Face API: {str(e)}")
        # Fallback classification
        return {
            "exercise_type": "unknown",
            "confidence": 0.0,
            "form_quality": "unknown",
            "repetitions": 0
        }

def generate_feedback(exercise_data, joint_angles_sequence):
    """Generate personalized feedback using OpenAI API"""
    # Create prompt for OpenAI
    exercise_type = exercise_data["exercise_type"]
    form_quality = exercise_data["form_quality"]
    repetitions = exercise_data["repetitions"]
    
    # Calculate average joint angles across sequence
    avg_joint_angles = {}
    if joint_angles_sequence:
        for angle_name in joint_angles_sequence[0].keys():
            avg_joint_angles[angle_name] = sum(frame[angle_name] for frame in joint_angles_sequence) / len(joint_angles_sequence)
    
    # Construct prompt
    prompt = f"""
    Generate detailed, helpful feedback for a fitness video analysis. 
    
    Exercise Information:
    - Exercise Type: {exercise_type}
    - Form Quality: {form_quality}
    - Repetitions Performed: {repetitions}
    - Average Joint Angles:
      - Left Knee: {avg_joint_angles.get('left_knee', 'N/A'):.1f}°
      - Right Knee: {avg_joint_angles.get('right_knee', 'N/A'):.1f}°
      - Left Elbow: {avg_joint_angles.get('left_elbow', 'N/A'):.1f}°
      - Right Elbow: {avg_joint_angles.get('right_elbow', 'N/A'):.1f}°
      - Left Hip: {avg_joint_angles.get('left_hip', 'N/A'):.1f}°
      - Right Hip: {avg_joint_angles.get('right_hip', 'N/A'):.1f}°
    
    Provide specific feedback on technique based on the joint angles.
    Include 3-4 specific improvements the person could make to their form.
    Close with encouragement for their next workout.
    Make the feedback motivational, supportive, and actionable.
    """
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional fitness coach with expertise in exercise form and technique."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract feedback
        feedback = response.choices[0].message['content'].strip()
        return feedback
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        # Return generic feedback as fallback
        return f"You completed {repetitions} repetitions of {exercise_type}. Keep practicing to improve your form."

def generate_audio_feedback(feedback_text, video_id):
    """Generate audio feedback using a TTS service"""
    try:
        # Use OpenAI's TTS API
        response = openai.Audio.create(
            model="tts-1",
            voice="alloy",
            input=feedback_text
        )
        
        # Save audio to file
        audio_path = f"/tmp/{video_id}_feedback.mp3"
        with open(audio_path, "wb") as f:
            f.write(response)
        
        return audio_path
        
    except Exception as e:
        logger.error(f"Error generating audio feedback: {str(e)}")
        # Return path to a default audio file
        return "/app/static/default_feedback.mp3"

# API Endpoints
@app.post("/api/videos/upload")
async def upload_video(
    video: UploadFile = File(...),
    title: str = Form(...), 
    description: Optional[str] = Form(None),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Upload a fitness video for analysis"""
    try:
        # Generate a unique ID for the video
        video_id = str(uuid.uuid4())
        
        # Get file extension
        file_extension = os.path.splitext(video.filename)[1]
        if file_extension.lower() not in ['.mp4', '.avi', '.mov', '.wmv']:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload MP4, AVI, MOV, or WMV.")
        
        # Create S3 key
        s3_key = f"uploads/{video_id}{file_extension}"
        
        # Upload file to S3
        try:
            video_content = await video.read()
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=video_content,
                ContentType=video.content_type
            )
        except ClientError as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload video to cloud storage")
        
        # Create database entries
        video_db = Video(
            id=video_id,
            user_id=user_id,
            title=title,
            description=description,
            original_filename=video.filename,
            s3_key=s3_key,
            content_type=video.content_type,
            file_size=len(video_content),
            created_at=datetime.utcnow()
        )
        db.add(video_db)
        
        analysis_db = Analysis(
            video_id=video_id,
            status="queued",
            created_at=datetime.utcnow()
        )
        db.add(analysis_db)
        db.commit()
        
        # Trigger Celery task
        task = process_video.delay(video_id, s3_key)
        
        # Store task ID in Redis for status checking
        redis_client.set(f"task:{video_id}", task.id)
        
        return {
            "video_id": video_id,
            "status": "queued",
            "message": "Video uploaded successfully and queued for analysis"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/api/videos/{video_id}/status")
async def get_video_status(video_id: str, db: Session = Depends(get_db)):
    """Get the processing status of a video"""
    # Get analysis from database
    analysis = db.query(Analysis).filter(Analysis.video_id == video_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Video analysis not found")
    
    # Get task ID from Redis
    task_id = redis_client.get(f"task:{video_id}")
    task_status = None
    
    if task_id:
        # Check Celery task status
        task_result = AsyncResult(task_id.decode('utf-8'), app=celery_app)
        task_status = task_result.status
    
    return {
        "video_id": video_id,
        "status": analysis.status,
        "task_status": task_status,
        "created_at": analysis.created_at,
        "completed_at": analysis.completed_at,
        "error": analysis.error
    }

@app.get("/api/videos/{video_id}/results")
async def get_video_results(video_id: str, db: Session = Depends(get_db)):
    """Get the analysis results for a video"""
    # Get analysis from database
    analysis = db.query(Analysis).filter(Analysis.video_id == video_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Video analysis not found")
    
    if analysis.status != "completed":
        return {
            "video_id": video_id,
            "status": analysis.status,
            "message": "Analysis not yet completed"
        }
    
    # Get video details
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Generate signed URLs for processed video and audio
    processed_video_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': f"processed/{video_id}_analyzed.mp4"
        },
        ExpiresIn=3600  # URL valid for 1 hour
    )
    
    audio_feedback_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': f"audio/{video_id}_feedback.mp3"
        },
        ExpiresIn=3600  # URL valid for 1 hour
    )
    
    # Return results with signed URLs
    return {
        "video_id": video_id,
        "title": video.title,
        "description": video.description,
        "status": "completed",
        "results": analysis.results,
        "processed_video_url": processed_video_url,
        "audio_feedback_url": audio_feedback_url,
        "completed_at": analysis.completed_at
    }

@app.get("/", response_class=HTMLResponse)
async def get_home_page():
    """Serve the home page"""
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

# Run the app with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
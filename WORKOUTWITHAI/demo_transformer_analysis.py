#!/usr/bin/env python3
import os
import argparse
import torch
import cv2
import matplotlib.pyplot as plt
import numpy as np
from enhanced_video_analyzer import EnhancedVideoAnalyzer
from transformer_models import VideoActionRecognizer, FormAnalyzer, FeedbackGenerator
import gradio as gr
from PIL import Image

def process_video(video_path, output_dir=None):
    """Process video with the enhanced transformer-based analyzer"""
    # Create output directory if not provided
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(video_path), 'analysis_results')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing video: {video_path}")
    print(f"Results will be saved to: {output_dir}")
    
    # Initialize analyzer
    analyzer = EnhancedVideoAnalyzer()
    
    # Process video
    results = analyzer.process_video(video_path, output_dir)
    
    # Extract key results
    exercise_type = results['exercise_type']
    repetitions = results['repetitions']
    form_quality = results['form_quality']['overall_quality']
    exercise_confidence = results['exercise_confidence'][exercise_type]
    feedback = results['feedback']
    annotated_video = results['annotated_video']
    
    # Print results
    print("\n" + "="*50)
    print(f"RESULTS FOR: {os.path.basename(video_path)}")
    print("="*50)
    print(f"Exercise Type: {exercise_type.upper()} (Confidence: {exercise_confidence:.2f})")
    print(f"Repetitions: {repetitions}")
    print(f"Form Quality: {form_quality.upper()}")
    print(f"\nAI Feedback:")
    print(f"{feedback}")
    print("="*50)
    
    return results, annotated_video

def visualize_results(results, output_dir):
    """Generate visualizations of the analysis results"""
    # Create figures directory
    figures_dir = os.path.join(output_dir, 'figures')
    os.makedirs(figures_dir, exist_ok=True)
    
    try:
        # 1. Exercise confidence visualization
        plt.figure(figsize=(10, 6))
        exercise_confidence = results['exercise_confidence']
        exercises = list(exercise_confidence.keys())
        confidences = list(exercise_confidence.values())
        
        # Sort by confidence
        sorted_indices = np.argsort(confidences)[::-1]  # Descending
        exercises = [exercises[i] for i in sorted_indices]
        confidences = [confidences[i] for i in sorted_indices]
        
        # Create bar chart
        plt.bar(exercises, confidences, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
        plt.ylim(0, 1.0)
        plt.xlabel('Exercise Type')
        plt.ylabel('Confidence Score')
        plt.title('Exercise Classification Confidence')
        plt.savefig(os.path.join(figures_dir, 'exercise_confidence.png'))
        plt.close()
    except Exception as e:
        print(f"Error creating exercise confidence visualization: {str(e)}")
    
    try:
        # 2. Form quality visualization
        plt.figure(figsize=(8, 8))
        form_scores = results['form_quality']['score']
        labels = list(form_scores.keys())
        scores = list(form_scores.values())
        
        # Create pie chart
        plt.pie(scores, labels=labels, autopct='%1.1f%%', 
                colors=['#2ecc71', '#f39c12', '#e74c3c'])
        plt.title('Form Quality Analysis')
        plt.savefig(os.path.join(figures_dir, 'form_quality.png'))
        plt.close()
    except Exception as e:
        print(f"Error creating form quality visualization: {str(e)}")
    
    try:
        # 3. Exercise segments timeline
        if 'exercise_segments' in results and results['exercise_segments']:
            # Make figure wider for better readability with many reps
            plt.figure(figsize=(14, 6))
            segments = results['exercise_segments']
            
            # Extract timestamps
            timestamps = [seg['timestamp'] for seg in segments]
            rep_numbers = [seg['rep_number'] for seg in segments]
            
            # Create better visualization
            # Use a colored strip to show timeline
            plt.axhspan(0.9, 1.1, color='#f0f0f0', alpha=0.3)
            
            # Add vertical grid lines for better readability
            plt.grid(axis='x', alpha=0.3, linestyle='--')
            
            # Create timeline with larger markers
            plt.scatter(timestamps, [1] * len(timestamps), marker='o', s=120, color='#3498db', zorder=5)
            
            # Add rep numbers with improved spacing
            # Determine if we need to show all rep numbers or select a subset
            total_reps = len(segments)
            
            if total_reps <= 10:
                # If few reps, show all numbers
                for i, seg in enumerate(segments):
                    plt.text(seg['timestamp'], 1.15, f"Rep {seg['rep_number']}", ha='center', fontsize=10)
            else:
                # For many reps, show a selection to avoid overlap
                # Show first, last, and a selection in between
                show_indices = [0]  # Always show first rep
                
                # Add some reps in between (every nth rep)
                step = max(1, total_reps // 8)  # Show about 8 labels
                for i in range(step, total_reps - 1, step):
                    show_indices.append(i)
                    
                # Always show last rep
                if total_reps > 1:
                    show_indices.append(total_reps - 1)
                
                # Place labels
                for i in show_indices:
                    seg = segments[i]
                    plt.text(seg['timestamp'], 1.15, f"Rep {seg['rep_number']}", ha='center', fontsize=10)
                
            # Add title with total rep count
            plt.ylim(0.8, 1.3)
            plt.yticks([])
            plt.xlim(0, 1)
            plt.xlabel('Video Timeline (normalized)', fontsize=12)
            plt.title(f'Exercise Repetitions Timeline: {results["repetitions"]} reps detected', fontsize=14)
            
            # Add annotation for better understanding
            if total_reps > 0:
                avg_spacing = 1.0 / total_reps if total_reps > 1 else 0.5
                plt.annotate('Each dot represents one repetition', 
                            xy=(avg_spacing, 0.85), 
                            xytext=(avg_spacing, 0.85),
                            ha='center', fontsize=10, color='#555555')
            
            plt.tight_layout()
            plt.savefig(os.path.join(figures_dir, 'repetitions_timeline.png'), dpi=100)
            plt.close()
    except Exception as e:
        print(f"Error creating repetitions timeline: {str(e)}")
    
    return figures_dir

def create_gradio_demo():
    """Create a Gradio demo for the enhanced video analyzer"""
    # Function for video file analysis
    def analyze_video(video_path):
        """Analyze the video with error handling"""
        # Process the video
        temp_dir = os.path.join(os.path.dirname(video_path), 'temp_gradio_output')
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            results, annotated_video = process_video(video_path, temp_dir)
            
            # Create visualizations
            vis_dir = visualize_results(results, temp_dir)
            
            # Format results for display
            exercise_type = results['exercise_type'].capitalize()
            repetitions = results['repetitions']
            form_quality = results['form_quality']['overall_quality'].capitalize()
            feedback = results['feedback']
            
            # Load visualization images
            try:
                confidence_img_path = os.path.join(vis_dir, 'exercise_confidence.png')
                confidence_img = Image.open(confidence_img_path) if os.path.exists(confidence_img_path) else None
                
                form_img_path = os.path.join(vis_dir, 'form_quality.png')
                form_img = Image.open(form_img_path) if os.path.exists(form_img_path) else None
                
                timeline_path = os.path.join(vis_dir, 'repetitions_timeline.png')
                timeline_img = Image.open(timeline_path) if os.path.exists(timeline_path) else None
            except Exception as e:
                print(f"Error loading visualizations: {str(e)}")
                confidence_img = None
                form_img = None
                timeline_img = None
            
            markdown = f"""
            # Analysis Results
            
            ## Exercise Detection
            **Detected Exercise:** {exercise_type}
            **Repetition Count:** {repetitions}
            
            ## Form Quality
            **Overall Form Quality:** {form_quality}
            
            ## AI Feedback
            {feedback}
            """
            
            return annotated_video, markdown, confidence_img, form_img, timeline_img
            
        except Exception as e:
            import traceback
            print(f"Error in video analysis: {str(e)}")
            print(traceback.format_exc())
            
            # Create error message
            error_md = f"""
            # Error Processing Video
            
            Sorry, we encountered an error processing your video: **{str(e)}**
            
            Please try:
            1. Using a shorter video
            2. Uploading a video with clearer visibility of the person
            3. Uploading a video in MP4 format
            """
            
            return None, error_md, None, None, None
    
    # Real-time webcam analysis function
    def process_webcam_frame(frame):
        """Process a single webcam frame with MediaPipe pose estimation"""
        import numpy as np
        import cv2
        
        # Check if frame is None or empty
        if frame is None:
            return np.zeros((300, 400, 3), dtype=np.uint8), "No input", "Please enable your webcam"
        
        # Convert PIL image or array to OpenCV format if needed
        if not isinstance(frame, np.ndarray):
            # Try to convert if it's not a numpy array (like a PIL image)
            try:
                frame = np.array(frame)
            except:
                return np.zeros((300, 400, 3), dtype=np.uint8), "Invalid input", "Camera input format error"
        
        # Initialize MediaPipe pose on first call
        if not hasattr(process_webcam_frame, "pose"):
            process_webcam_frame.pose = mp.solutions.pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            process_webcam_frame.mp_drawing = mp.solutions.drawing_utils
            process_webcam_frame.mp_drawing_styles = mp.solutions.drawing_styles
            process_webcam_frame.current_exercise = "unknown"
            process_webcam_frame.rep_counter = 0
            process_webcam_frame.form_issues = []
            process_webcam_frame.frame_count = 0
            process_webcam_frame.last_audio_time = 0
            # For rep counting
            process_webcam_frame.last_position = None
            process_webcam_frame.rep_positions = {
                "squat": {"up": False, "down": False},
                "pushup": {"up": False, "down": False},
                "plank": {"up": False, "down": False},
                "pullup": {"up": False, "down": False},
                "lunge": {"up": False, "down": False},
                "running": {"up": False, "down": False}
            }
            process_webcam_frame.rep_started = False
            print("MediaPipe pose initialized")
        
        # Convert to RGB for MediaPipe
        try:
            # Make sure the frame is in the correct format for OpenCV
            if len(frame.shape) == 2:  # Grayscale
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 4:  # RGBA
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = process_webcam_frame.pose.process(rgb_frame)
            
            # Print frame info for debugging
            print(f"Frame shape: {frame.shape}, Pose detected: {results.pose_landmarks is not None}")
            
            # If no pose detected, return the original frame
            if not results.pose_landmarks:
                return frame, "No pose detected", "Please ensure your full body is visible in the frame."
            
            # Draw pose landmarks on the frame
            annotated_frame = frame.copy()
            process_webcam_frame.mp_drawing.draw_landmarks(
                annotated_frame,
                results.pose_landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=process_webcam_frame.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Increment frame counter
            process_webcam_frame.frame_count += 1
            
            # Every 30 frames (approximately 1 second), analyze the pose for exercise
            if process_webcam_frame.frame_count % 30 == 0:
                # Extract key landmarks for analysis
                landmarks = results.pose_landmarks.landmark
                
                # Simplified exercise detection based on pose
                # In a real implementation, this would use the full transformer models
                if is_squat_position(landmarks):
                    process_webcam_frame.current_exercise = "squat"
                    form_feedback, has_issues = analyze_squat_form(landmarks)
                    
                    # Rep counting for squats
                    left_knee_angle = calculate_angle(
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
                    )
                    
                    # Detect down position (knee bent)
                    if left_knee_angle < 90 and not process_webcam_frame.rep_positions["squat"]["down"]:
                        process_webcam_frame.rep_positions["squat"]["down"] = True
                        process_webcam_frame.rep_positions["squat"]["up"] = False
                        process_webcam_frame.rep_started = True
                    
                    # Detect up position (knee straight) and count rep if we were in down position
                    if left_knee_angle > 160 and process_webcam_frame.rep_started and process_webcam_frame.rep_positions["squat"]["down"]:
                        process_webcam_frame.rep_positions["squat"]["up"] = True
                        process_webcam_frame.rep_positions["squat"]["down"] = False
                        process_webcam_frame.rep_counter += 1
                        print(f"Squat rep detected! Count: {process_webcam_frame.rep_counter}")
                    
                elif is_pushup_position(landmarks):
                    process_webcam_frame.current_exercise = "pushup"
                    form_feedback, has_issues = analyze_pushup_form(landmarks)
                    
                    # Rep counting for pushups
                    left_elbow_angle = calculate_angle(
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
                    )
                    
                    # Detect down position (elbow bent)
                    if left_elbow_angle < 90 and not process_webcam_frame.rep_positions["pushup"]["down"]:
                        process_webcam_frame.rep_positions["pushup"]["down"] = True
                        process_webcam_frame.rep_positions["pushup"]["up"] = False
                        process_webcam_frame.rep_started = True
                    
                    # Detect up position (elbow straight) and count rep if we were in down position
                    if left_elbow_angle > 160 and process_webcam_frame.rep_started and process_webcam_frame.rep_positions["pushup"]["down"]:
                        process_webcam_frame.rep_positions["pushup"]["up"] = True
                        process_webcam_frame.rep_positions["pushup"]["down"] = False
                        process_webcam_frame.rep_counter += 1
                        print(f"Pushup rep detected! Count: {process_webcam_frame.rep_counter}")
                elif is_plank_position(landmarks):
                    process_webcam_frame.current_exercise = "plank"
                    form_feedback, has_issues = analyze_plank_form(landmarks)
                    
                    # Rep counting for planks
                    left_elbow_angle = calculate_angle(
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
                    )
                    
                    # Detect down position (elbow bent)
                    if left_elbow_angle < 90 and not process_webcam_frame.rep_positions["plank"]["down"]:
                        process_webcam_frame.rep_positions["plank"]["down"] = True
                        process_webcam_frame.rep_positions["plank"]["up"] = False
                        process_webcam_frame.rep_started = True
                    
                    # Detect up position (elbow straight) and count rep if we were in down position
                    if left_elbow_angle > 160 and process_webcam_frame.rep_started and process_webcam_frame.rep_positions["plank"]["down"]:
                        process_webcam_frame.rep_positions["plank"]["up"] = True
                        process_webcam_frame.rep_positions["plank"]["down"] = False
                        process_webcam_frame.rep_counter += 1
                        print(f"Plank rep detected! Count: {process_webcam_frame.rep_counter}")
                elif is_pullup_position(landmarks):
                    process_webcam_frame.current_exercise = "pullup"
                    form_feedback, has_issues = analyze_pullup_form(landmarks)
                    
                    # Rep counting for pullups
                    left_elbow_angle = calculate_angle(
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
                    )
                    
                    # Detect down position (elbow bent)
                    if left_elbow_angle < 90 and not process_webcam_frame.rep_positions["pullup"]["down"]:
                        process_webcam_frame.rep_positions["pullup"]["down"] = True
                        process_webcam_frame.rep_positions["pullup"]["up"] = False
                        process_webcam_frame.rep_started = True
                    
                    # Detect up position (elbow straight) and count rep if we were in down position
                    if left_elbow_angle > 160 and process_webcam_frame.rep_started and process_webcam_frame.rep_positions["pullup"]["down"]:
                        process_webcam_frame.rep_positions["pullup"]["up"] = True
                        process_webcam_frame.rep_positions["pullup"]["down"] = False
                        process_webcam_frame.rep_counter += 1
                        print(f"Pullup rep detected! Count: {process_webcam_frame.rep_counter}")
                elif is_lunge_position(landmarks):
                    process_webcam_frame.current_exercise = "lunge"
                    form_feedback, has_issues = analyze_lunge_form(landmarks)
                    
                    # Rep counting for lunges
                    left_knee_angle = calculate_angle(
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value],
                        landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
                    )
                    
                    # Detect down position (knee bent)
                    if left_knee_angle < 90 and not process_webcam_frame.rep_positions["lunge"]["down"]:
                        process_webcam_frame.rep_positions["lunge"]["down"] = True
                        process_webcam_frame.rep_positions["lunge"]["up"] = False
                        process_webcam_frame.rep_started = True
                    
                    # Detect up position (knee straight) and count rep if we were in down position
                    if left_knee_angle > 160 and process_webcam_frame.rep_started and process_webcam_frame.rep_positions["lunge"]["down"]:
                        process_webcam_frame.rep_positions["lunge"]["up"] = True
                        process_webcam_frame.rep_positions["lunge"]["down"] = False
                        process_webcam_frame.rep_counter += 1
                        print(f"Lunge rep detected! Count: {process_webcam_frame.rep_counter}")
                else:
                    process_webcam_frame.current_exercise = "unknown"
                    form_feedback = "Position not recognized as a specific exercise"
                    has_issues = False
                
                # Store form issues for AR overlay
                process_webcam_frame.form_issues = form_feedback if has_issues else []
            
            # Add AR overlays for form feedback
            if process_webcam_frame.form_issues:
                for i, issue in enumerate(process_webcam_frame.form_issues):
                    # Add text overlay with the form issue
                    cv2.putText(
                        annotated_frame,
                        issue,
                        (10, 30 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),  # Red color for incorrect form
                        2
                    )
            
            # Add exercise and rep information
            cv2.putText(
                annotated_frame,
                f"Exercise: {process_webcam_frame.current_exercise.capitalize()}",
                (10, annotated_frame.shape[0] - 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            cv2.putText(
                annotated_frame,
                f"Reps: {process_webcam_frame.rep_counter}",
                (10, annotated_frame.shape[0] - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            # Generate feedback text
            if process_webcam_frame.form_issues:
                feedback_text = "Form Issues Detected:\n" + "\n".join(process_webcam_frame.form_issues)
            else:
                feedback_text = "Good form! Keep going."
            
            return annotated_frame, process_webcam_frame.current_exercise.capitalize(), feedback_text
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            return frame, "Processing error", f"Error: {str(e)}"
    
    # Helper functions for pose analysis
    def calculate_angle(a, b, c):
        """Calculate the angle between three points"""
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    # Comprehensive exercise classification system
    class ExerciseClassifier:
        """Advanced exercise classification system for real-time pose data"""
        
        def __init__(self):
            # Define exercise categories
            self.exercises = {
                "squat": {
                    "key_indicators": ["knee flexion", "hip flexion", "vertical torso"],
                    "common_errors": ["knees caving inward", "insufficient depth", "forward lean"]
                },
                "pushup": {
                    "key_indicators": ["horizontal body", "elbow flexion", "straight spine"],
                    "common_errors": ["sagging hips", "raised hips", "incomplete range"]
                },
                "plank": {
                    "key_indicators": ["horizontal alignment", "static position", "neutral spine"],
                    "common_errors": ["sagging hips", "raised hips", "head dropping"]
                },
                "pullup": {
                    "key_indicators": ["arms overhead", "vertical pulling", "elbow flexion"],
                    "common_errors": ["insufficient height", "asymmetric movement"]
                },
                "lunge": {
                    "key_indicators": ["split stance", "front knee flexion", "vertical torso"],
                    "common_errors": ["knee extending past toes", "insufficient depth"]
                },
                "burpee": {
                    "key_indicators": ["position changes", "full body engagement", "jump component"],
                    "common_errors": ["poor push-up form", "incomplete extensions"]
                },
                "jumping_jack": {
                    "key_indicators": ["arm and leg spreading", "rhythmic movement", "jumping"],
                    "common_errors": ["limited range", "asymmetric movements"]
                },
                "deadlift": {
                    "key_indicators": ["hip hinge", "neutral spine", "knee extension"],
                    "common_errors": ["rounded back", "insufficient hip hinge"]
                }
            }
            
            # Initialize tracking
            self.history = []  # Store recent classifications
            self.confidence_scores = {}
            
        def classify(self, landmarks):
            """Classify exercise based on pose landmarks"""
            # Reset confidence scores
            self.confidence_scores = {exercise: 0.0 for exercise in self.exercises.keys()}
            
            # Extract joint data
            joint_data = self._extract_joint_data(landmarks)
            
            # Calculate confidence scores for each exercise
            self._calculate_confidence_scores(joint_data)
            
            # Update history for temporal smoothing
            if len(self.history) > 5:
                self.history.pop(0)
            
            # Get highest confidence exercise
            best_exercise = max(self.confidence_scores.items(), key=lambda x: x[1])
            exercise_type = best_exercise[0]
            confidence = best_exercise[1]
            
            # Only classify if confidence exceeds threshold
            if confidence < 0.4:
                exercise_type = "unknown"
                feedback = "No recognizable exercise pattern detected"
                form_issues = []
                has_issues = False
            else:
                # Add to history
                self.history.append(exercise_type)
                
                # Analyze form and generate feedback
                feedback, form_issues, has_issues = self._analyze_form(exercise_type, joint_data)
            
            # Return results
            return {
                "exercise_type": exercise_type,
                "confidence": confidence,
                "feedback": feedback,
                "form_issues": form_issues,
                "has_issues": has_issues
            }
        
        def _extract_joint_data(self, landmarks):
            """Extract relevant joint angles and positions"""
            joint_data = {}
            
            # Calculate key angles
            joint_data["knee_angle"] = {
                "left": calculate_angle(landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value],
                                       landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value],
                                       landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]),
                "right": calculate_angle(landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value],
                                        landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value],
                                        landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value])
            }
            
            joint_data["elbow_angle"] = {
                "left": calculate_angle(landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value],
                                       landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value],
                                       landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]),
                "right": calculate_angle(landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value],
                                        landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value],
                                        landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value])
            }
            
            # Store positions for form analysis
            joint_data["positions"] = {
                "hip": {"left": landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value], 
                        "right": landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]},
                "knee": {"left": landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value],
                         "right": landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value]},
                "ankle": {"left": landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value],
                          "right": landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value]},
                "shoulder": {"left": landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value],
                             "right": landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]},
                "elbow": {"left": landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value],
                          "right": landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value]},
                "wrist": {"left": landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value],
                          "right": landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value]},
                "nose": landmarks[mp.solutions.pose.PoseLandmark.NOSE.value]
            }
            
            # Calculate torso angle (approximation)
            shoulder_mid_y = (landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y + 
                             landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2
            hip_mid_y = (landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y + 
                        landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value].y) / 2
            shoulder_mid_x = (landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].x + 
                             landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].x) / 2
            hip_mid_x = (landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].x + 
                        landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value].x) / 2
            
            dx = shoulder_mid_x - hip_mid_x
            dy = shoulder_mid_y - hip_mid_y
            joint_data["torso_angle"] = np.abs(np.degrees(np.arctan2(dx, -dy)))
            
            return joint_data
        
        def _calculate_confidence_scores(self, joint_data):
            """Calculate confidence scores for each exercise"""
            # Calculate squat confidence
            squat_conf = 0.0
            knee_angle_avg = (joint_data["knee_angle"]["left"] + joint_data["knee_angle"]["right"]) / 2
            if knee_angle_avg < 140:  # Bent knees
                squat_conf += 0.5
                if knee_angle_avg < 100:  # Deeper squat
                    squat_conf += 0.2
            if joint_data["torso_angle"] < 45:  # Relatively upright torso
                squat_conf += 0.3
            self.confidence_scores["squat"] = min(1.0, squat_conf)
            
            # Calculate pushup confidence
            pushup_conf = 0.0
            if 70 < joint_data["torso_angle"] < 110:  # Horizontal body
                pushup_conf += 0.5
            elbow_angle_avg = (joint_data["elbow_angle"]["left"] + joint_data["elbow_angle"]["right"]) / 2
            if elbow_angle_avg < 140:  # Bent elbows
                pushup_conf += 0.4
            self.confidence_scores["pushup"] = min(1.0, pushup_conf)
            
            # Calculate plank confidence
            plank_conf = 0.0
            if 70 < joint_data["torso_angle"] < 110:  # Horizontal body
                plank_conf += 0.5
            # Check body alignment
            left_shoulder = joint_data["positions"]["shoulder"]["left"]
            left_hip = joint_data["positions"]["hip"]["left"]
            left_ankle = joint_data["positions"]["ankle"]["left"]
            if abs(left_shoulder.y - left_hip.y) < 0.1 and abs(left_hip.y - left_ankle.y) < 0.1:
                plank_conf += 0.5
            self.confidence_scores["plank"] = min(1.0, plank_conf)
            
            # Similar implementations for other exercises...
            # (Added placeholder values for other exercises)
            self.confidence_scores["pullup"] = 0.2
            self.confidence_scores["lunge"] = 0.1
            self.confidence_scores["deadlift"] = 0.1
            self.confidence_scores["burpee"] = 0.1
            self.confidence_scores["jumping_jack"] = 0.1
        
        def _analyze_form(self, exercise_type, joint_data):
            """Analyze exercise form and provide feedback"""
            form_issues = []
            has_issues = False
            
            if exercise_type == "squat":
                # Check knee alignment
                left_knee = joint_data["positions"]["knee"]["left"]
                left_ankle = joint_data["positions"]["ankle"]["left"]
                if left_knee.x > left_ankle.x + 0.1:
                    form_issues.append("Knees too far forward")
                    has_issues = True
                
                # Check squat depth
                if joint_data["knee_angle"]["left"] > 100 and joint_data["knee_angle"]["right"] > 100:
                    form_issues.append("Squat not deep enough")
                    has_issues = True
                
                # Check torso angle
                if joint_data["torso_angle"] > 45:
                    form_issues.append("Keep back more upright")
                    has_issues = True
            
            elif exercise_type == "pushup":
                # Check body alignment
                left_shoulder = joint_data["positions"]["shoulder"]["left"]
                left_hip = joint_data["positions"]["hip"]["left"]
                if left_hip.y > left_shoulder.y + 0.1:
                    form_issues.append("Hips sagging - keep body straight")
                    has_issues = True
                
                if left_hip.y < left_shoulder.y - 0.1:
                    form_issues.append("Hips too high - lower your body")
                    has_issues = True
                
                # Check elbow angle
                if joint_data["elbow_angle"]["left"] > 110 or joint_data["elbow_angle"]["right"] > 110:
                    form_issues.append("Lower your body more")
                    has_issues = True
            
            elif exercise_type == "plank":
                # Check body alignment
                left_shoulder = joint_data["positions"]["shoulder"]["left"]
                left_hip = joint_data["positions"]["hip"]["left"]
                left_ankle = joint_data["positions"]["ankle"]["left"]
                
                if abs(left_shoulder.y - left_hip.y) > 0.1 or abs(left_hip.y - left_ankle.y) > 0.1:
                    form_issues.append("Body not aligned - maintain straight line")
                    has_issues = True
            
            # Generate feedback text
            if has_issues:
                feedback = "Form needs improvement: " + ", ".join(form_issues)
            else:
                feedback = f"Good {exercise_type} form! Keep it up."
            
            return feedback, form_issues, has_issues
    
    # Import MediaPipe at module level for helper functions
    import mediapipe as mp
    
    def is_squat_position(landmarks):
        """Detect if the pose is likely a squat"""
        # Basic check: knees bent and relatively symmetrical positioning
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        
        # Calculate knee angle
        knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        
        # If knee angle is less than 120 degrees, it's likely a squat position
        return knee_angle < 120
    
    def is_pushup_position(landmarks):
        """Detect if the pose is likely a pushup"""
        # Basic check: body parallel to ground, arms bent
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        
        # Check if body is relatively horizontal
        nose = landmarks[mp.solutions.pose.PoseLandmark.NOSE.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        
        # If nose and ankle are at similar height, and arms are bent, it's likely a pushup
        return abs(nose.y - left_ankle.y) < 0.2 and left_shoulder.y < left_elbow.y
    
    def is_plank_position(landmarks):
        """Detect if the pose is likely a plank"""
        # Check if body is horizontal and straight
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        
        # Calculate angles to check body alignment
        body_alignment = abs(left_shoulder.y - left_hip.y) < 0.1 and abs(left_hip.y - left_ankle.y) < 0.1
        
        # Check arm position (straight or bent depending on plank type)
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        elbow_angle = calculate_angle(left_shoulder, left_elbow, landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value])
        
        # Could be straight-arm or bent-arm plank
        arm_position = (elbow_angle > 160) or (elbow_angle < 120 and elbow_angle > 70)
        
        return body_alignment and arm_position
    
    def is_pullup_position(landmarks):
        """Detect if the pose is likely a pullup"""
        # Check arm position and head above hands
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        nose = landmarks[mp.solutions.pose.PoseLandmark.NOSE.value]
        
        # Arms should be bent and above shoulders, head above hands
        arms_bent = calculate_angle(left_shoulder, left_elbow, left_wrist) < 140
        arms_overhead = left_wrist.y < left_shoulder.y
        head_position = nose.y > left_wrist.y
        
        return arms_bent and arms_overhead and head_position
    
    def is_lunge_position(landmarks):
        """Detect if the pose is likely a lunge"""
        # One leg forward bent, one leg back
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # Calculate knee angles
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        # Check for split stance (one knee bent, one extended)
        split_stance = (left_knee_angle < 110 and right_knee_angle > 150) or (right_knee_angle < 110 and left_knee_angle > 150)
        
        # Check for feet separated front to back
        feet_separated = abs(left_ankle.x - right_ankle.x) > 0.2
        
        return split_stance and feet_separated
    
    def is_running_position(landmarks):
        """Detect if the pose is likely running"""
        # Check for dynamic leg and arm movement patterns
        left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # One arm forward, one back (opposite pattern)
        arms_opposite = (left_wrist.x > right_wrist.x + 0.2) or (right_wrist.x > left_wrist.x + 0.2)
        
        # Feet separated (one forward, one back)
        feet_dynamic = abs(left_ankle.y - right_ankle.y) > 0.1
        
        # Both feet off ground or one foot off ground
        left_ankle_height = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value].y
        right_ankle_height = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value].y
        feet_off_ground = (left_ankle_height < 0.9) or (right_ankle_height < 0.9)
        
        return arms_opposite and feet_dynamic and feet_off_ground
    
    def analyze_squat_form(landmarks):
        """Analyze squat form and return feedback"""
        issues = []
        has_issues = False
        
        # Get key landmarks
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # Calculate knee angles
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        # Check if knees are too far forward (knee over toes)
        if left_knee.x > left_ankle.x + 0.1 or right_knee.x > right_ankle.x + 0.1:
            issues.append("Knees too far forward")
            has_issues = True
        
        # Check if squat is deep enough
        if left_knee_angle > 100 and right_knee_angle > 100:
            issues.append("Squat not deep enough")
            has_issues = True
        
        # Check if back is arched too much
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        if abs(left_shoulder.x - left_hip.x) > 0.15:
            issues.append("Keep back straight")
            has_issues = True
        
        return issues, has_issues
    
    def analyze_pushup_form(landmarks):
        """Analyze pushup form and return feedback"""
        issues = []
        has_issues = False
        
        # Get key landmarks
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value]
        
        # Calculate elbow angles
        left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        # Check if elbows are bent properly
        if left_elbow_angle > 110 or right_elbow_angle > 110:
            issues.append("Lower your body more")
            has_issues = True
        
        # Check if body is straight
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        
        # Check if hips are sagging
        if left_hip.y > left_shoulder.y + 0.1:
            issues.append("Hips too low - keep body straight")
            has_issues = True
        
        # Check if hips are too high
        if left_hip.y < left_shoulder.y - 0.1:
            issues.append("Hips too high - lower your body")
            has_issues = True
        
        return issues, has_issues
    
    def analyze_plank_form(landmarks):
        """Analyze plank form and return feedback"""
        issues = []
        has_issues = False
        
        # Get key landmarks
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        
        # Calculate angles to check body alignment
        body_alignment = abs(left_shoulder.y - left_hip.y) < 0.1 and abs(left_hip.y - left_ankle.y) < 0.1
        
        # Check arm position (straight or bent depending on plank type)
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        elbow_angle = calculate_angle(left_shoulder, left_elbow, landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value])
        
        # Could be straight-arm or bent-arm plank
        arm_position = (elbow_angle > 160) or (elbow_angle < 120 and elbow_angle > 70)
        
        if not body_alignment or not arm_position:
            issues.append("Incorrect body alignment or arm position")
            has_issues = True
        
        return issues, has_issues
    
    def analyze_pullup_form(landmarks):
        """Analyze pullup form and return feedback"""
        issues = []
        has_issues = False
        
        # Get key landmarks
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value]
        
        # Calculate elbow angles
        left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        # Check if elbows are bent properly
        if left_elbow_angle > 110 or right_elbow_angle > 110:
            issues.append("Lower your body more")
            has_issues = True
        
        # Check if body is straight
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        
        # Check if hips are sagging
        if left_hip.y > left_shoulder.y + 0.1:
            issues.append("Hips too low - keep body straight")
            has_issues = True
        
        # Check if hips are too high
        if left_hip.y < left_shoulder.y - 0.1:
            issues.append("Hips too high - lower your body")
            has_issues = True
        
        return issues, has_issues
    
    def analyze_lunge_form(landmarks):
        """Analyze lunge form and return feedback"""
        issues = []
        has_issues = False
        
        # Get key landmarks
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value]
        
        # Calculate knee angles
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        # Check for split stance (one knee bent, one extended)
        split_stance = (left_knee_angle < 110 and right_knee_angle > 150) or (right_knee_angle < 110 and left_knee_angle > 150)
        
        # Check for feet separated front to back
        feet_separated = abs(left_ankle.x - right_ankle.x) > 0.2
        
        if not split_stance or not feet_separated:
            issues.append("Incorrect lunge form")
            has_issues = True
        
        return issues, has_issues
    
    # Create the interface
    with gr.Blocks(title="Enhanced Sports Video Analysis Demo") as demo:
        gr.Markdown("# Enhanced Sports Video Analysis with Transformer Models")
        
        with gr.Tabs():
            with gr.TabItem("Video File Analysis"):
                gr.Markdown("""
                Upload a video of someone performing exercises (squats, pushups, lunges, or jumping jacks) to get started.
                """)
                
                with gr.Row():
                    input_video = gr.Video(label="Upload Exercise Video")
                    output_video = gr.Video(label="Annotated Video")
                
                analyze_btn = gr.Button("Analyze Video", variant="primary")
                
                with gr.Row():
                    results_md = gr.Markdown()
                
                with gr.Row():
                    confidence_plot = gr.Image(label="Exercise Classification Confidence")
                    form_plot = gr.Image(label="Form Quality Analysis")
                
                timeline_plot = gr.Image(label="Repetitions Timeline")
                
                analyze_btn.click(
                    analyze_video,
                    inputs=[input_video],
                    outputs=[output_video, results_md, confidence_plot, form_plot, timeline_plot]
                )
            
            with gr.TabItem("Real-Time Webcam Analysis"):
                gr.Markdown("""
                # Real-Time Exercise Analysis with AR Feedback
                
                This feature uses your webcam to provide real-time exercise form analysis with visual AR overlays.
                
                **How it works:**
                1. MediaPipe tracks your body pose in real-time
                2. The system analyzes your form and provides immediate feedback
                3. Visual AR overlays highlight areas that need correction
                4. Audio feedback helps guide your movements
                
                **Note:** For best results, ensure your full body is visible in the frame and you have adequate lighting.
                """)
                
                with gr.Row():
                    webcam_input = gr.Image(sources=["webcam"], streaming=True, label="Your Webcam")
                    webcam_output = gr.Image(label="Real-Time Analysis with AR Overlay")
                
                exercise_label = gr.Text(label="Detected Exercise", value="None detected")
                feedback_text = gr.Textbox(label="Form Feedback", value="Position yourself in the frame to begin analysis")
                
                # Add JavaScript for Text-to-Speech
                gr.HTML("""
                <script>
                    // Initialize speech synthesis
                    const synth = window.speechSynthesis;
                    let lastSpokenText = "";
                    let lastSpeechTime = 0;
                    
                    // Function to speak feedback
                    function speakFeedback(text) {
                        // Don't repeat the same feedback too quickly (3 second cooldown)
                        const now = Date.now();
                        if (text === lastSpokenText && now - lastSpeechTime < 3000) {
                            return;
                        }
                        
                        // Cancel any ongoing speech
                        synth.cancel();
                        
                        // Create new speech utterance
                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.rate = 1.0;
                        utterance.pitch = 1.0;
                        
                        // Speak the feedback
                        synth.speak(utterance);
                        
                        // Update tracking variables
                        lastSpokenText = text;
                        lastSpeechTime = now;
                    }
                    
                    // Set up observer to watch for feedback changes
                    document.addEventListener('DOMContentLoaded', () => {
                        // Find the feedback text element (may need adjustment based on Gradio's structure)
                        const feedbackObserver = new MutationObserver((mutations) => {
                            for (const mutation of mutations) {
                                if (mutation.type === 'childList' || mutation.type === 'characterData') {
                                    const text = mutation.target.textContent || "";
                                    if (text.includes("Issues Detected")) {
                                        // Extract and speak just the issues
                                        const issuesText = text.split("Issues Detected:")[1].trim();
                                        speakFeedback(issuesText);
                                    }
                                }
                            }
                        });
                        
                        // Start observing after a delay to ensure Gradio has rendered
                        setTimeout(() => {
                            const feedbackElements = document.querySelectorAll('[data-testid="textbox"]');
                            feedbackElements.forEach(el => {
                                feedbackObserver.observe(el, { 
                                    childList: true, 
                                    characterData: true,
                                    subtree: true 
                                });
                            });
                        }, 2000);
                    });
                </script>
                """)
                
                # Set up the webcam processing
                webcam_input.stream(
                    process_webcam_frame,
                    inputs=[webcam_input],
                    outputs=[webcam_output, exercise_label, feedback_text]
                )
    
    return demo

def main():
    """Main function to run the demo"""
    parser = argparse.ArgumentParser(description="Demo for enhanced video analysis with transformers")
    parser.add_argument('--mode', type=str, choices=['cli', 'gradio'], default='cli',
                      help='Demo mode: cli for command line, gradio for web interface')
    parser.add_argument('--video', type=str, help='Path to video file (required for cli mode)')
    parser.add_argument('--output', type=str, help='Path to output directory (optional)')
    
    args = parser.parse_args()
    
    if args.mode == 'cli':
        if not args.video:
            parser.error("--video is required for cli mode")
        
        # Run CLI demo
        results, annotated_video = process_video(args.video, args.output)
        visualize_results(results, os.path.dirname(annotated_video))
        
        print(f"\nAnnotated video saved to: {annotated_video}")
        print(f"Visualization figures saved to: {os.path.join(os.path.dirname(annotated_video), 'figures')}")
    
    elif args.mode == 'gradio':
        # Run Gradio demo
        demo = create_gradio_demo()
        demo.launch(share=True)

if __name__ == "__main__":
    main() 
import cv2
import mediapipe as mp
import numpy as np
import os
import json
import time
from typing import Dict, List, Tuple, Optional, Any

class VideoProcessor:
    """
    Class for processing workout videos and extracting frames
    """
    def __init__(self, video_path: str, output_dir: Optional[str] = None):
        self.video_path = video_path
        self.output_dir = output_dir or os.path.join(os.path.dirname(video_path), "frames")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def extract_frames(self, frame_rate: int = 5) -> List[str]:
        """
        Extract frames from video at specified frame rate
        
        Args:
            frame_rate: Number of frames to extract per second
            
        Returns:
            List of paths to extracted frames
        """
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {self.video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame interval
        frame_interval = int(fps / frame_rate)
        if frame_interval < 1:
            frame_interval = 1
            
        frame_paths = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                frame_path = os.path.join(self.output_dir, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                
            frame_count += 1
            
        cap.release()
        return frame_paths


class PoseEstimator:
    """
    Class for estimating human poses in workout videos using MediaPipe
    """
    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process a single frame to detect pose landmarks
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (annotated_frame, pose_landmarks_dict)
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(frame_rgb)
        
        # Convert landmarks to dictionary
        landmarks_dict = {}
        if results.pose_landmarks:
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks_dict[f"landmark_{idx}"] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                }
        
        # Draw pose landmarks on the frame
        annotated_frame = frame.copy()
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
        return annotated_frame, landmarks_dict
    
    def process_video(self, video_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process entire video and extract pose landmarks for each frame
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save output files
            
        Returns:
            Dictionary with analysis results
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(video_path), "analysis")
        os.makedirs(output_dir, exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Prepare output video
        output_video_path = os.path.join(output_dir, "annotated_video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        # Process frames
        frame_count = 0
        landmarks_by_frame = {}
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frame
            annotated_frame, landmarks = self.process_frame(frame)
            
            # Save landmarks
            landmarks_by_frame[frame_count] = landmarks
            
            # Write to output video
            out.write(annotated_frame)
            
            # Save keyframes
            if frame_count % int(fps) == 0:  # Save one frame per second
                keyframe_path = os.path.join(output_dir, f"keyframe_{frame_count:06d}.jpg")
                cv2.imwrite(keyframe_path, annotated_frame)
                
            frame_count += 1
            
        # Release resources
        cap.release()
        out.release()
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save landmarks to file
        landmarks_path = os.path.join(output_dir, "pose_landmarks.json")
        with open(landmarks_path, 'w') as f:
            json.dump(landmarks_by_frame, f)
            
        # Prepare results
        results = {
            "total_frames": total_frames,
            "processed_frames": frame_count,
            "fps": fps,
            "processing_time": processing_time,
            "output_video": output_video_path,
            "landmarks_file": landmarks_path
        }
        
        return results


class ExerciseClassifier:
    """
    Class for classifying exercises based on pose landmarks
    """
    def __init__(self):
        # Define exercise patterns
        self.exercise_patterns = {
            "squat": self._is_squat,
            "pushup": self._is_pushup,
            "lunge": self._is_lunge,
            "jumping_jack": self._is_jumping_jack
        }
        
    def _is_squat(self, landmarks: Dict[str, Dict[str, float]]) -> bool:
        """Check if pose represents a squat position"""
        if not landmarks:
            return False
            
        # Get key landmarks
        hip = landmarks.get("landmark_24", {})  # Right hip
        knee = landmarks.get("landmark_26", {})  # Right knee
        ankle = landmarks.get("landmark_28", {})  # Right ankle
        
        if not (hip and knee and ankle):
            return False
            
        # Calculate knee angle
        hip_y = hip.get("y", 0)
        knee_y = knee.get("y", 0)
        ankle_y = ankle.get("y", 0)
        
        # In a squat, knee is lower than hip and higher than ankle
        return knee_y > hip_y and knee_y < ankle_y
        
    def _is_pushup(self, landmarks: Dict[str, Dict[str, float]]) -> bool:
        """Check if pose represents a pushup position"""
        if not landmarks:
            return False
            
        # Get key landmarks
        shoulder = landmarks.get("landmark_12", {})  # Right shoulder
        elbow = landmarks.get("landmark_14", {})  # Right elbow
        wrist = landmarks.get("landmark_16", {})  # Right wrist
        
        if not (shoulder and elbow and wrist):
            return False
            
        # In a pushup, body is parallel to ground
        shoulder_y = shoulder.get("y", 0)
        elbow_y = elbow.get("y", 0)
        
        # Shoulders and elbows should be at similar height
        return abs(shoulder_y - elbow_y) < 0.1
        
    def _is_lunge(self, landmarks: Dict[str, Dict[str, float]]) -> bool:
        """Check if pose represents a lunge position"""
        if not landmarks:
            return False
            
        # Get key landmarks
        left_knee = landmarks.get("landmark_25", {})  # Left knee
        right_knee = landmarks.get("landmark_26", {})  # Right knee
        
        if not (left_knee and right_knee):
            return False
            
        # In a lunge, one knee is much lower than the other
        left_knee_y = left_knee.get("y", 0)
        right_knee_y = right_knee.get("y", 0)
        
        return abs(left_knee_y - right_knee_y) > 0.2
        
    def _is_jumping_jack(self, landmarks: Dict[str, Dict[str, float]]) -> bool:
        """Check if pose represents a jumping jack position"""
        if not landmarks:
            return False
            
        # Get key landmarks
        left_wrist = landmarks.get("landmark_15", {})  # Left wrist
        right_wrist = landmarks.get("landmark_16", {})  # Right wrist
        left_ankle = landmarks.get("landmark_27", {})  # Left ankle
        right_ankle = landmarks.get("landmark_28", {})  # Right ankle
        
        if not (left_wrist and right_wrist and left_ankle and right_ankle):
            return False
            
        # In a jumping jack, arms and legs are spread wide
        left_wrist_x = left_wrist.get("x", 0)
        right_wrist_x = right_wrist.get("x", 0)
        left_ankle_x = left_ankle.get("x", 0)
        right_ankle_x = right_ankle.get("x", 0)
        
        arms_spread = abs(left_wrist_x - right_wrist_x) > 0.5
        legs_spread = abs(left_ankle_x - right_ankle_x) > 0.3
        
        return arms_spread and legs_spread
        
    def classify_frame(self, landmarks: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Classify exercise in a single frame
        
        Args:
            landmarks: Dictionary of pose landmarks
            
        Returns:
            Dictionary with confidence scores for each exercise type
        """
        results = {}
        
        for exercise, check_func in self.exercise_patterns.items():
            results[exercise] = 1.0 if check_func(landmarks) else 0.0
            
        return results
        
    def classify_video(self, landmarks_by_frame: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, Any]:
        """
        Classify exercises in a video
        
        Args:
            landmarks_by_frame: Dictionary of pose landmarks by frame
            
        Returns:
            Dictionary with exercise classification results
        """
        frame_classifications = {}
        exercise_counts = {exercise: 0 for exercise in self.exercise_patterns.keys()}
        
        for frame_idx, landmarks in landmarks_by_frame.items():
            classification = self.classify_frame(landmarks)
            frame_classifications[frame_idx] = classification
            
            # Count exercises
            for exercise, confidence in classification.items():
                if confidence > 0.5:
                    exercise_counts[exercise] += 1
                    
        # Calculate dominant exercise
        dominant_exercise = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else None
        
        # Calculate estimated calories burned (very simplified)
        total_frames = len(landmarks_by_frame)
        if total_frames > 0:
            # Assume 30 fps and 5 calories per minute of exercise
            duration_minutes = total_frames / (30 * 60)
            calories_burned = duration_minutes * 5
        else:
            calories_burned = 0
            
        results = {
            "frame_classifications": frame_classifications,
            "exercise_counts": exercise_counts,
            "dominant_exercise": dominant_exercise,
            "calories_burned": calories_burned
        }
        
        return results


class WorkoutAnalyzer:
    """
    Main class for analyzing workout videos
    """
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir
        self.pose_estimator = PoseEstimator()
        self.exercise_classifier = ExerciseClassifier()
        
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        Analyze workout video
        
        Args:
            video_path: Path to input video
            
        Returns:
            Dictionary with analysis results
        """
        # Create output directory
        if self.output_dir is None:
            self.output_dir = os.path.join(os.path.dirname(video_path), "analysis")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Process video and extract pose landmarks
        pose_results = self.pose_estimator.process_video(video_path, self.output_dir)
        
        # Load landmarks from file
        landmarks_path = pose_results["landmarks_file"]
        with open(landmarks_path, 'r') as f:
            landmarks_by_frame = json.load(f)
            
        # Classify exercises
        classification_results = self.exercise_classifier.classify_video(landmarks_by_frame)
        
        # Combine results
        results = {
            **pose_results,
            **classification_results,
            "video_path": video_path,
            "output_dir": self.output_dir
        }
        
        # Save final results
        results_path = os.path.join(self.output_dir, "analysis_results.json")
        with open(results_path, 'w') as f:
            # Convert any non-serializable objects to strings
            serializable_results = {k: str(v) if not isinstance(v, (dict, list, str, int, float, bool, type(None))) else v 
                                   for k, v in results.items()}
            json.dump(serializable_results, f, indent=2)
            
        return results


# Example usage
if __name__ == "__main__":
    # This would be used for testing
    video_path = "path/to/workout_video.mp4"
    analyzer = WorkoutAnalyzer()
    results = analyzer.analyze_video(video_path)
    print(f"Analysis complete. Results saved to {results['output_dir']}")

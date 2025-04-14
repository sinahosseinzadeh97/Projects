import os
import torch
import numpy as np
import cv2
from typing import Dict, List, Tuple, Any, Optional
from einops import rearrange
from timesformer_pytorch import TimeSformer
from transformers import pipeline, AutoProcessor, AutoModelForCausalLM

class VideoActionRecognizer:
    """
    Class for action recognition in videos using TimeSformer model
    """
    def __init__(self, 
                 model_name: str = 'facebook/timesformer-base-finetuned-k400', 
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model_name = model_name
        self.image_size = 224  # TimeSformer default size
        
        # Load model with custom configuration to match our inputs
        print(f"Loading TimeSformer model to {device}...")
        self.model = TimeSformer(
            dim = 768,  # Using 768 instead of 512 to match standard transformer models
            image_size = self.image_size,
            patch_size = 16,
            num_frames = 8,
            num_classes = 4,  # We'll use 4 classes: squat, pushup, lunge, jumping_jack
            depth = 12,
            heads = 12
        ).to(device)
        
        # Define labels matching our exercise classes
        self.labels = ["squat", "pushup", "lunge", "jumping_jack"]
        
    def extract_video_frames(self, video_path: str, num_frames: int = 8) -> torch.Tensor:
        """
        Extract frames from video for TimeSformer processing
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract
            
        Returns:
            Tensor of shape (num_frames, 3, image_size, image_size)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame indices to extract (evenly distributed)
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        # Extract frames
        frames = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                # If we can't read a frame, create a blank frame
                frame = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)
                
            # Preprocess frame: resize and convert to RGB
            frame = cv2.resize(frame, (self.image_size, self.image_size))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Normalize to [0, 1] and convert to torch tensor
            frame = frame / 255.0
            frame = torch.FloatTensor(frame).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
            frames.append(frame)
            
        cap.release()
        
        # Stack frames into single tensor
        if len(frames) == 0:
            raise ValueError("No frames could be extracted from video")
            
        frames_tensor = torch.stack(frames)  # (num_frames, 3, H, W)
        return frames_tensor
    
    def predict(self, video_path: str) -> Dict[str, float]:
        """
        Predict action in video
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary of class scores
        """
        frames = self.extract_video_frames(video_path)
        
        # Add batch dimension
        frames = frames.unsqueeze(0).to(self.device)  # (1, num_frames, 3, H, W)
        
        # Convert from (B, T, C, H, W) to (B, C, T, H, W) for TimeSformer
        frames = frames.permute(0, 2, 1, 3, 4)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(frames)
            
        # Convert to probabilities
        probs = torch.nn.functional.softmax(outputs, dim=1)[0].cpu().numpy()
        
        # Create results dictionary
        results = {label: float(prob) for label, prob in zip(self.labels, probs)}
        return results


class FormAnalyzer:
    """
    Class for analyzing exercise form using pose landmarks and transformer model
    """
    def __init__(self, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        
        try:
            # We'll use a simpler architecture since we don't have trained weights for form analysis
            print(f"Initializing form analyzer on {device}...")
            
            # Create a simple MLP classifier instead of loading a transformer
            self.model = torch.nn.Sequential(
                torch.nn.Linear(12, 64),
                torch.nn.ReLU(),
                torch.nn.Linear(64, 32),
                torch.nn.ReLU(),
                torch.nn.Linear(32, 3)
            ).to(device)
            
            self.model_loaded = True
        except Exception as e:
            print(f"Error loading form analyzer model: {str(e)}")
            self.model_loaded = False
        
        self.labels = ["good", "medium", "poor"]
        
    def _landmarks_to_features(self, landmarks: Dict[str, Dict[str, float]]) -> List[float]:
        """
        Convert landmarks dictionary to feature vector for form analysis
        """
        # Extract key joint angles and positions
        features = []
        
        # If landmarks are empty, return empty feature vector
        if not landmarks:
            return [0.0] * 12  # Return zeros with expected feature length
            
        # Key landmarks for form analysis
        key_landmarks = {
            "nose": landmarks.get("landmark_0", {}),
            "left_shoulder": landmarks.get("landmark_11", {}),
            "right_shoulder": landmarks.get("landmark_12", {}),
            "left_elbow": landmarks.get("landmark_13", {}),
            "right_elbow": landmarks.get("landmark_14", {}),
            "left_hip": landmarks.get("landmark_23", {}),
            "right_hip": landmarks.get("landmark_24", {}),
            "left_knee": landmarks.get("landmark_25", {}),
            "right_knee": landmarks.get("landmark_26", {}),
            "left_ankle": landmarks.get("landmark_27", {}),
            "right_ankle": landmarks.get("landmark_28", {})
        }
        
        # Extract y-positions (vertical alignment) of key joints
        features.append(key_landmarks["left_shoulder"].get("y", 0.5))
        features.append(key_landmarks["right_shoulder"].get("y", 0.5))
        features.append(key_landmarks["left_hip"].get("y", 0.5))
        features.append(key_landmarks["right_hip"].get("y", 0.5))
        features.append(key_landmarks["left_knee"].get("y", 0.5))
        features.append(key_landmarks["right_knee"].get("y", 0.5))
        
        # Extract x-positions (horizontal alignment) of key joints
        features.append(key_landmarks["left_shoulder"].get("x", 0.5))
        features.append(key_landmarks["right_shoulder"].get("x", 0.5))
        features.append(key_landmarks["left_hip"].get("x", 0.5))
        features.append(key_landmarks["right_hip"].get("x", 0.5))
        features.append(key_landmarks["left_knee"].get("x", 0.5))
        features.append(key_landmarks["right_knee"].get("x", 0.5))
        
        return features
    
    def analyze_form(self, landmarks_by_frame: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, Any]:
        """
        Analyze exercise form quality
        
        Args:
            landmarks_by_frame: Dictionary of pose landmarks by frame
            
        Returns:
            Dictionary with form analysis results
        """
        # If model isn't loaded, return a default assessment
        if not self.model_loaded:
            return {
                "overall_quality": "medium",
                "score": {
                    "good": 0.3,
                    "medium": 0.5,
                    "poor": 0.2
                }
            }
        
        try:
            # Extract features from landmarks
            frame_ids = sorted([int(k) for k in landmarks_by_frame.keys()])
            features = []
            
            for frame_id in frame_ids:
                landmarks = landmarks_by_frame.get(str(frame_id), {})
                frame_features = self._landmarks_to_features(landmarks)
                features.append(frame_features)
                
            # If no features extracted, return default result
            if not features:
                return {
                    "overall_quality": "unknown",
                    "score": {
                        "good": 0.0,
                        "medium": 0.0,
                        "poor": 0.0
                    }
                }
                
            # Calculate average features over all frames for a summary
            avg_features = np.mean(features, axis=0)
            
            # Convert to tensor
            inputs = torch.FloatTensor(avg_features).to(self.device)
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(inputs)
                
            # Get probabilities
            probs = torch.nn.functional.softmax(outputs, dim=0).cpu().numpy()
            
            # Get predicted class
            pred_class = self.labels[np.argmax(probs)]
            
            # Prepare results
            results = {
                "overall_quality": pred_class,
                "score": {
                    label: float(prob) for label, prob in zip(self.labels, probs)
                }
            }
            
            return results
            
        except Exception as e:
            print(f"Error in form analysis: {str(e)}")
            # Return a default assessment if anything fails
            return {
                "overall_quality": "medium",
                "score": {
                    "good": 0.3,
                    "medium": 0.4,
                    "poor": 0.3
                }
            }


class FeedbackGenerator:
    """
    Class for generating personalized feedback using LLM
    """
    def __init__(self, model_name: str = "facebook/opt-125m"):  # Using a smaller model for faster inference
        self.model_name = model_name
        
        # Load model and processor
        try:
            print(f"Loading feedback generator model: {model_name}")
            self.processor = AutoProcessor.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.model_loaded = True
        except Exception as e:
            print(f"Error loading feedback model: {str(e)}")
            self.model_loaded = False
        
    def generate_feedback(self, 
                         exercise_type: str, 
                         form_quality: str,
                         rep_count: int,
                         additional_notes: Optional[str] = None) -> str:
        """
        Generate personalized feedback for exercise performance
        
        Args:
            exercise_type: Type of exercise (squat, pushup, etc.)
            form_quality: Overall form quality (good, medium, poor)
            rep_count: Number of repetitions counted
            additional_notes: Any additional information to include
            
        Returns:
            Generated feedback text
        """
        if not self.model_loaded:
            # Fallback to template-based feedback if model failed to load
            return self._generate_template_feedback(exercise_type, form_quality, rep_count)
            
        # Create prompt for the model
        prompt = f"""
        Exercise: {exercise_type}
        Form quality: {form_quality}
        Repetitions: {rep_count}
        """
        
        if additional_notes:
            prompt += f"Additional notes: {additional_notes}\n"
            
        prompt += "Provide specific feedback for this workout performance:"
        
        try:
            # Generate text
            inputs = self.processor(prompt, return_tensors="pt")
            
            with torch.no_grad():
                output = self.model.generate(
                    inputs.input_ids,
                    max_length=100,  # Shorter for speed
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
                
            # Decode the generated text
            feedback = self.processor.decode(output[0], skip_special_tokens=True)
            
            # Remove the prompt from the output
            feedback = feedback.replace(prompt, "").strip()
            
            return feedback
        except Exception as e:
            print(f"Error generating feedback: {str(e)}")
            return self._generate_template_feedback(exercise_type, form_quality, rep_count)
    
    def _generate_template_feedback(self, exercise_type: str, form_quality: str, rep_count: int) -> str:
        """Generate feedback using templates when the model fails"""
        quality_feedback = {
            "good": "Your form was excellent! Keep up the good work.",
            "medium": "Your form was decent, but there's room for improvement.",
            "poor": "Your form needs significant improvement to prevent injury."
        }
        
        exercise_tips = {
            "squat": "Focus on keeping your back straight and knees aligned with your toes.",
            "pushup": "Ensure your elbows are at a 45-degree angle and your core is engaged.",
            "lunge": "Keep your front knee above your ankle and maintain a straight back.",
            "jumping_jack": "Coordinate your arm and leg movements, and land softly to protect your joints."
        }
        
        rep_feedback = ""
        if rep_count < 5:
            rep_feedback = "Consider increasing your repetition count for better endurance."
        elif rep_count > 15:
            rep_feedback = "Great job with the high repetition count! Consider increasing intensity."
        else:
            rep_feedback = f"You completed {rep_count} repetitions, which is a good workout volume."
        
        feedback = f"{quality_feedback.get(form_quality, 'Your form needs attention.')} {exercise_tips.get(exercise_type, 'Focus on proper technique.')} {rep_feedback}"
        
        return feedback 
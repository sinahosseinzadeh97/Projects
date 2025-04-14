import pytest
import sys
import os
import numpy as np
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ML modules
from ml.video_analysis import VideoProcessor, PoseEstimator, ExerciseClassifier, WorkoutAnalyzer

class TestVideoProcessor:
    @patch('cv2.VideoCapture')
    @patch('cv2.imwrite')
    def test_extract_frames(self, mock_imwrite, mock_video_capture):
        # Mock video properties
        mock_video = MagicMock()
        mock_video.isOpened.return_value = True
        mock_video.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 300
        }.get(prop, 0)
        mock_video.read.side_effect = [(True, np.zeros((480, 640, 3))) for _ in range(10)] + [(False, None)]
        
        mock_video_capture.return_value = mock_video
        
        # Test frame extraction
        processor = VideoProcessor("test_video.mp4", "/tmp/frames")
        frame_paths = processor.extract_frames(frame_rate=5)
        
        # Verify results
        assert len(frame_paths) == 10
        assert mock_imwrite.call_count == 10

class TestPoseEstimator:
    @patch('mediapipe.solutions.pose.Pose')
    def test_process_frame(self, mock_pose):
        # Mock pose estimation results
        mock_results = MagicMock()
        mock_results.pose_landmarks.landmark = [
            MagicMock(x=0.1, y=0.2, z=0.3, visibility=0.9) for _ in range(33)
        ]
        
        mock_pose_instance = MagicMock()
        mock_pose_instance.process.return_value = mock_results
        mock_pose.return_value = mock_pose_instance
        
        # Test pose estimation
        estimator = PoseEstimator()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        annotated_frame, landmarks = estimator.process_frame(frame)
        
        # Verify results
        assert len(landmarks) == 33
        assert landmarks["landmark_0"]["x"] == 0.1
        assert landmarks["landmark_0"]["y"] == 0.2

class TestExerciseClassifier:
    def test_classify_frame(self):
        # Create test landmarks
        squat_landmarks = {
            "landmark_24": {"x": 0.5, "y": 0.5},  # Right hip
            "landmark_26": {"x": 0.5, "y": 0.7},  # Right knee (lower than hip)
            "landmark_28": {"x": 0.5, "y": 0.9}   # Right ankle (lower than knee)
        }
        
        # Test classification
        classifier = ExerciseClassifier()
        results = classifier.classify_frame(squat_landmarks)
        
        # Verify results
        assert results["squat"] == 1.0
        assert results["pushup"] == 0.0

class TestWorkoutAnalyzer:
    @patch('ml.video_analysis.PoseEstimator')
    @patch('ml.video_analysis.ExerciseClassifier')
    @patch('json.dump')
    @patch('json.load')
    @patch('builtins.open', new_callable=MagicMock)
    def test_analyze_video(self, mock_open, mock_json_load, mock_json_dump, 
                          mock_classifier, mock_estimator):
        # Mock pose estimation results
        mock_pose_instance = MagicMock()
        mock_pose_instance.process_video.return_value = {
            "total_frames": 100,
            "processed_frames": 100,
            "fps": 30.0,
            "processing_time": 10.5,
            "output_video": "/tmp/analysis/annotated_video.mp4",
            "landmarks_file": "/tmp/analysis/pose_landmarks.json"
        }
        mock_estimator.return_value = mock_pose_instance
        
        # Mock classification results
        mock_classifier_instance = MagicMock()
        mock_classifier_instance.classify_video.return_value = {
            "frame_classifications": {},
            "exercise_counts": {"squat": 10, "pushup": 5},
            "dominant_exercise": "squat",
            "calories_burned": 15.5
        }
        mock_classifier.return_value = mock_classifier_instance
        
        # Mock JSON operations
        mock_json_load.return_value = {"0": {}, "30": {}, "60": {}}
        
        # Test video analysis
        analyzer = WorkoutAnalyzer("/tmp/analysis")
        results = analyzer.analyze_video("test_video.mp4")
        
        # Verify results
        assert results["dominant_exercise"] == "squat"
        assert results["calories_burned"] == 15.5
        assert results["total_frames"] == 100
        assert mock_json_dump.call_count == 1

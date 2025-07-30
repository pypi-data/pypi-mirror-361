"""
Motion tracking implementations using camera and MediaPipe.
"""

import cv2
import numpy as np
import time
from typing import Dict, Tuple, Optional, List
from .core import MotionTracker, MotionData

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class CameraTracker(MotionTracker):
    """Basic camera-based motion tracker using OpenCV."""
    
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self.is_active = False
        self.frame_width = 640
        self.frame_height = 480
        
    def start_tracking(self) -> bool:
        """Start camera tracking."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.is_active = True
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop_tracking(self) -> None:
        """Stop camera tracking."""
        self.is_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def get_motion_data(self) -> Optional[MotionData]:
        """Get motion data from camera frame."""
        if not self.is_active or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Simple motion detection using frame differencing
        if hasattr(self, 'prev_frame'):
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            prev_gray = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(gray, prev_gray)
            
            # Find contours
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Extract motion data
            body_parts = {}
            confidence = {}
            
            for i, contour in enumerate(contours[:5]):  # Limit to 5 largest contours
                if cv2.contourArea(contour) > 500:  # Filter small contours
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        # Normalize coordinates
                        x = cx / self.frame_width
                        y = cy / self.frame_height
                        z = 0.0  # No depth info in basic camera
                        
                        body_parts[f"motion_{i}"] = (x, y, z)
                        confidence[f"motion_{i}"] = 0.7  # Basic confidence
            
            self.prev_frame = frame.copy()
            
            return MotionData(
                timestamp=time.time(),
                body_parts=body_parts,
                confidence=confidence
            )
        else:
            self.prev_frame = frame.copy()
            return MotionData(
                timestamp=time.time(),
                body_parts={},
                confidence={}
            )
    
    def is_tracking(self) -> bool:
        """Check if tracking is active."""
        return self.is_active


class MediaPipeTracker(MotionTracker):
    """Advanced motion tracker using MediaPipe Pose."""
    
    def __init__(self, camera_index: int = 0):
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError("MediaPipe is not available. Install with: pip install mediapipe")
        
        self.camera_index = camera_index
        self.cap = None
        self.is_active = False
        self.mp_pose = mp.solutions.pose
        self.pose = None
        
        # MediaPipe pose landmarks mapping
        self.landmark_names = {
            0: "nose",
            1: "left_eye_inner", 2: "left_eye", 3: "left_eye_outer",
            4: "right_eye_inner", 5: "right_eye", 6: "right_eye_outer",
            7: "left_ear", 8: "right_ear",
            9: "mouth_left", 10: "mouth_right",
            11: "left_shoulder", 12: "right_shoulder",
            13: "left_elbow", 14: "right_elbow",
            15: "left_wrist", 16: "right_wrist",
            17: "left_pinky", 18: "right_pinky",
            19: "left_index", 20: "right_index",
            21: "left_thumb", 22: "right_thumb",
            23: "left_hip", 24: "right_hip",
            25: "left_knee", 26: "right_knee",
            27: "left_ankle", 28: "right_ankle",
            29: "left_heel", 30: "right_heel",
            31: "left_foot_index", 32: "right_foot_index"
        }
    
    def start_tracking(self) -> bool:
        """Start MediaPipe pose tracking."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                return False
            
            self.pose = self.mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.is_active = True
            return True
        except Exception as e:
            print(f"Error starting MediaPipe tracking: {e}")
            return False
    
    def stop_tracking(self) -> None:
        """Stop MediaPipe tracking."""
        self.is_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.pose:
            self.pose.close()
            self.pose = None
    
    def get_motion_data(self) -> Optional[MotionData]:
        """Get motion data from MediaPipe pose detection."""
        if not self.is_active or not self.cap or not self.pose:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        body_parts = {}
        confidence = {}
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            frame_height, frame_width, _ = frame.shape
            
            for landmark_id, landmark in enumerate(landmarks):
                if landmark_id in self.landmark_names:
                    # Normalize coordinates
                    x = landmark.x
                    y = landmark.y
                    z = landmark.z
                    
                    body_parts[self.landmark_names[landmark_id]] = (x, y, z)
                    confidence[self.landmark_names[landmark_id]] = landmark.visibility
        
        return MotionData(
            timestamp=time.time(),
            body_parts=body_parts,
            confidence=confidence
        )
    
    def is_tracking(self) -> bool:
        """Check if tracking is active."""
        return self.is_active
    
    def get_available_landmarks(self) -> List[str]:
        """Get list of available landmark names."""
        return list(self.landmark_names.values()) 
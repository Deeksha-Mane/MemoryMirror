"""Video capture functionality for Memory Mirror application."""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple
from src.utils.config import config

logger = logging.getLogger(__name__)

class VideoCapture:
    """Handles webcam initialization and frame capture."""
    
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_initialized = False
        self.device_index = config.get('camera.device_index', 0)
        self.resolution = config.get('camera.resolution', [640, 480])
        self.fps = config.get('camera.fps', 30)
    
    def initialize_camera(self) -> bool:
        """Initialize the camera with configured settings."""
        try:
            # Release any existing camera connection
            if self.cap is not None:
                self.cap.release()
            
            # Initialize camera
            self.cap = cv2.VideoCapture(self.device_index)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera at index {self.device_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Test frame capture
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.error("Failed to capture test frame from camera")
                self.cap.release()
                return False
            
            self.is_initialized = True
            logger.info(f"Camera initialized successfully at {self.resolution[0]}x{self.resolution[1]} @ {self.fps}fps")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            if self.cap is not None:
                self.cap.release()
            return False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Capture and return a frame from the camera."""
        if not self.is_initialized or self.cap is None:
            logger.warning("Camera not initialized")
            return None
        
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.warning("Failed to capture frame")
                return None
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def is_camera_available(self) -> bool:
        """Check if camera is available and working."""
        if not self.is_initialized:
            return self.initialize_camera()
        
        if self.cap is None:
            return False
        
        # Test if we can still capture frames
        ret, frame = self.cap.read()
        return ret and frame is not None
    
    def get_camera_info(self) -> dict:
        """Get current camera information."""
        if not self.is_initialized or self.cap is None:
            return {}
        
        try:
            return {
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
                'device_index': self.device_index,
                'is_available': self.is_camera_available()
            }
        except Exception as e:
            logger.error(f"Error getting camera info: {e}")
            return {}
    
    def release_camera(self) -> None:
        """Release the camera resources."""
        try:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.is_initialized = False
            logger.info("Camera released successfully")
        except Exception as e:
            logger.error(f"Error releasing camera: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.release_camera()
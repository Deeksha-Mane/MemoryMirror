"""Frame processing utilities for Memory Mirror application."""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class FrameProcessor:
    """Processes video frames for optimal face detection."""
    
    def __init__(self):
        self.target_width = 640
        self.target_height = 480
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Apply preprocessing to frame for better face detection."""
        if frame is None:
            return None
        
        try:
            # Resize frame if needed
            processed_frame = self.resize_frame(frame, (self.target_width, self.target_height))
            
            # Enhance lighting conditions
            processed_frame = self.enhance_lighting(processed_frame)
            
            # Reduce noise
            processed_frame = cv2.bilateralFilter(processed_frame, 9, 75, 75)
            
            return processed_frame
            
        except Exception as e:
            logger.error(f"Error preprocessing frame: {e}")
            return frame
    
    def resize_frame(self, frame: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Resize frame to target dimensions while maintaining aspect ratio."""
        if frame is None:
            return None
        
        try:
            height, width = frame.shape[:2]
            target_width, target_height = target_size
            
            # Calculate aspect ratio
            aspect_ratio = width / height
            target_aspect_ratio = target_width / target_height
            
            if aspect_ratio > target_aspect_ratio:
                # Frame is wider than target
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                # Frame is taller than target
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            
            # Resize frame
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Create canvas with target size
            canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
            
            # Center the resized frame on canvas
            y_offset = (target_height - new_height) // 2
            x_offset = (target_width - new_width) // 2
            canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_frame
            
            return canvas
            
        except Exception as e:
            logger.error(f"Error resizing frame: {e}")
            return frame
    
    def enhance_lighting(self, frame: np.ndarray) -> np.ndarray:
        """Enhance lighting conditions for better face detection."""
        if frame is None:
            return None
        
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            
            # Split channels
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels back
            enhanced_lab = cv2.merge([l, a, b])
            
            # Convert back to BGR
            enhanced_frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced_frame
            
        except Exception as e:
            logger.error(f"Error enhancing lighting: {e}")
            return frame
    
    def detect_blur(self, frame: np.ndarray) -> float:
        """Detect blur level in frame using Laplacian variance."""
        if frame is None:
            return 0.0
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            return laplacian_var
            
        except Exception as e:
            logger.error(f"Error detecting blur: {e}")
            return 0.0
    
    def is_frame_suitable(self, frame: np.ndarray, blur_threshold: float = 100.0) -> bool:
        """Check if frame is suitable for face detection."""
        if frame is None:
            return False
        
        try:
            # Check if frame is not empty
            if frame.size == 0:
                return False
            
            # Check blur level
            blur_level = self.detect_blur(frame)
            if blur_level < blur_threshold:
                logger.debug(f"Frame too blurry: {blur_level:.2f} < {blur_threshold}")
                return False
            
            # Check brightness
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_brightness = np.mean(gray)
            
            # Frame should not be too dark or too bright
            if mean_brightness < 30 or mean_brightness > 225:
                logger.debug(f"Frame brightness unsuitable: {mean_brightness:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking frame suitability: {e}")
            return False
    
    def add_timestamp(self, frame: np.ndarray) -> np.ndarray:
        """Add timestamp to frame for debugging purposes."""
        if frame is None:
            return None
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add timestamp text
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (255, 255, 255), 2, cv2.LINE_AA)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error adding timestamp: {e}")
            return frame
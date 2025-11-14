"""Face detection functionality using OpenCV."""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from src.utils.config import config

logger = logging.getLogger(__name__)

class FaceDetector:
    """Detects faces in video frames using OpenCV."""
    
    def __init__(self):
        self.face_cascade = None
        self.min_face_size = (30, 30)
        self.scale_factor = 1.1
        self.min_neighbors = 5
        self.initialize_detector()
    
    def initialize_detector(self) -> bool:
        """Initialize the face detection cascade."""
        try:
            # Load the face cascade classifier
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                logger.error("Failed to load face cascade classifier")
                return False
            
            logger.info("Face detector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing face detector: {e}")
            return False
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces in the given frame."""
        if frame is None or self.face_cascade is None:
            return []
        
        try:
            # Convert frame to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=self.min_face_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Convert to list of dictionaries with additional info
            face_list = []
            for i, (x, y, w, h) in enumerate(faces):
                face_info = {
                    'id': i,
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(x + w // 2),
                    'center_y': int(y + h // 2),
                    'area': int(w * h),
                    'confidence': self._calculate_face_confidence(gray, x, y, w, h)
                }
                face_list.append(face_info)
            
            # Sort faces by area (largest first)
            face_list.sort(key=lambda f: f['area'], reverse=True)
            
            logger.debug(f"Detected {len(face_list)} faces")
            return face_list
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def extract_face_region(self, frame: np.ndarray, face_coords: Dict) -> Optional[np.ndarray]:
        """Extract face region from frame based on coordinates."""
        if frame is None or not face_coords:
            return None
        
        try:
            x = face_coords['x']
            y = face_coords['y']
            w = face_coords['width']
            h = face_coords['height']
            
            # Add padding around face
            padding = 20
            x_start = max(0, x - padding)
            y_start = max(0, y - padding)
            x_end = min(frame.shape[1], x + w + padding)
            y_end = min(frame.shape[0], y + h + padding)
            
            # Extract face region
            face_region = frame[y_start:y_end, x_start:x_end]
            
            # Resize to standard size for recognition
            if face_region.size > 0:
                face_region = cv2.resize(face_region, (160, 160), interpolation=cv2.INTER_AREA)
            
            return face_region
            
        except Exception as e:
            logger.error(f"Error extracting face region: {e}")
            return None
    
    def draw_face_boxes(self, frame: np.ndarray, faces: List[Dict], 
                       color: Tuple[int, int, int] = (0, 255, 0), 
                       thickness: int = 2) -> np.ndarray:
        """Draw bounding boxes around detected faces."""
        if frame is None or not faces:
            return frame
        
        try:
            result_frame = frame.copy()
            
            for face in faces:
                x, y, w, h = face['x'], face['y'], face['width'], face['height']
                
                # Draw rectangle around face
                cv2.rectangle(result_frame, (x, y), (x + w, y + h), color, thickness)
                
                # Add face ID label
                label = f"Face {face['id']}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.rectangle(result_frame, (x, y - label_size[1] - 10), 
                            (x + label_size[0], y), color, -1)
                cv2.putText(result_frame, label, (x, y - 5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            return result_frame
            
        except Exception as e:
            logger.error(f"Error drawing face boxes: {e}")
            return frame
    
    def _calculate_face_confidence(self, gray_frame: np.ndarray, x: int, y: int, 
                                 w: int, h: int) -> float:
        """Calculate confidence score for detected face."""
        try:
            # Extract face region
            face_region = gray_frame[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return 0.0
            
            # Calculate various quality metrics
            
            # 1. Size score (larger faces are generally better)
            size_score = min(1.0, (w * h) / (100 * 100))  # Normalize to 100x100
            
            # 2. Position score (faces in center are generally better)
            frame_center_x = gray_frame.shape[1] // 2
            frame_center_y = gray_frame.shape[0] // 2
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            distance_from_center = np.sqrt((face_center_x - frame_center_x)**2 + 
                                         (face_center_y - frame_center_y)**2)
            max_distance = np.sqrt(frame_center_x**2 + frame_center_y**2)
            position_score = 1.0 - (distance_from_center / max_distance)
            
            # 3. Contrast score (good contrast indicates clear features)
            contrast_score = np.std(face_region) / 255.0
            
            # Combine scores
            confidence = (size_score * 0.4 + position_score * 0.3 + contrast_score * 0.3)
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating face confidence: {e}")
            return 0.5
    
    def filter_faces_by_quality(self, faces: List[Dict], 
                               min_confidence: float = 0.3,
                               min_size: int = 1000) -> List[Dict]:
        """Filter faces based on quality metrics."""
        try:
            filtered_faces = []
            
            for face in faces:
                # Check confidence threshold
                if face['confidence'] < min_confidence:
                    continue
                
                # Check minimum size
                if face['area'] < min_size:
                    continue
                
                filtered_faces.append(face)
            
            logger.debug(f"Filtered {len(faces)} faces to {len(filtered_faces)} high-quality faces")
            return filtered_faces
            
        except Exception as e:
            logger.error(f"Error filtering faces: {e}")
            return faces
    
    def get_largest_face(self, faces: List[Dict]) -> Optional[Dict]:
        """Get the largest detected face."""
        if not faces:
            return None
        
        # Faces are already sorted by area in detect_faces
        return faces[0]
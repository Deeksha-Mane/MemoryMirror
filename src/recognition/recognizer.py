"""Face recognition functionality using DeepFace."""

import os
import numpy as np
import logging
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
import cv2

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    logging.warning("DeepFace not available. Face recognition will be limited.")

from src.utils.config import config

logger = logging.getLogger(__name__)

@dataclass
class RecognitionResult:
    """Result of face recognition operation."""
    person_id: str
    confidence: float
    is_known: bool
    timestamp: datetime
    distance: float = 0.0
    model_name: str = ""

class FaceRecognizer:
    """Matches detected faces against known database using DeepFace."""
    
    def __init__(self):
        self.known_faces_path = "known_faces"
        self.model_name = config.get('recognition.model_name', 'VGG-Face')
        self.detector_backend = config.get('recognition.detector_backend', 'opencv')
        self.confidence_threshold = config.get('recognition.confidence_threshold', 0.6)
        self.distance_metric = config.get('recognition.distance_metric', 'cosine')
        self.is_initialized = False
        self.known_persons = []
        
        if DEEPFACE_AVAILABLE:
            self.initialize_database()
    
    def initialize_database(self, known_faces_path: str = None) -> bool:
        """Initialize the face recognition database."""
        if not DEEPFACE_AVAILABLE:
            logger.error("DeepFace not available for face recognition")
            return False
        
        try:
            if known_faces_path:
                self.known_faces_path = known_faces_path
            
            # Check if known faces directory exists
            if not os.path.exists(self.known_faces_path):
                logger.warning(f"Known faces directory not found: {self.known_faces_path}")
                os.makedirs(self.known_faces_path, exist_ok=True)
                return False
            
            # Scan for known persons
            self.known_persons = []
            for person_dir in os.listdir(self.known_faces_path):
                person_path = os.path.join(self.known_faces_path, person_dir)
                if os.path.isdir(person_path):
                    # Check if directory has image files
                    image_files = [f for f in os.listdir(person_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                    if image_files:
                        self.known_persons.append(person_dir)
                        logger.info(f"Found {len(image_files)} images for person: {person_dir}")
            
            if not self.known_persons:
                logger.warning("No known persons found in database")
                return False
            
            logger.info(f"Face recognition database initialized with {len(self.known_persons)} persons")
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing face recognition database: {e}")
            return False
    
    def recognize_face(self, face_image: np.ndarray) -> RecognitionResult:
        """Recognize a face against the known database."""
        if not DEEPFACE_AVAILABLE or not self.is_initialized:
            return RecognitionResult(
                person_id="unknown",
                confidence=0.0,
                is_known=False,
                timestamp=datetime.now()
            )
        
        if face_image is None or face_image.size == 0:
            return RecognitionResult(
                person_id="unknown",
                confidence=0.0,
                is_known=False,
                timestamp=datetime.now()
            )
        
        try:
            best_match = None
            best_distance = float('inf')
            best_person = "unknown"
            
            # Compare against each known person
            for person_id in self.known_persons:
                person_path = os.path.join(self.known_faces_path, person_id)
                
                # Get all images for this person
                image_files = [f for f in os.listdir(person_path) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                
                person_distances = []
                
                for image_file in image_files:
                    image_path = os.path.join(person_path, image_file)
                    
                    try:
                        # Use DeepFace to verify faces
                        result = DeepFace.verify(
                            img1_path=face_image,
                            img2_path=image_path,
                            model_name=self.model_name,
                            detector_backend=self.detector_backend,
                            distance_metric=self.distance_metric,
                            enforce_detection=False
                        )
                        
                        distance = result['distance']
                        person_distances.append(distance)
                        
                    except Exception as e:
                        logger.debug(f"Error comparing with {image_path}: {e}")
                        continue
                
                # Use average distance for this person
                if person_distances:
                    avg_distance = np.mean(person_distances)
                    if avg_distance < best_distance:
                        best_distance = avg_distance
                        best_person = person_id
            
            # Determine if this is a known person based on threshold
            confidence = self._distance_to_confidence(best_distance)
            is_known = confidence >= self.confidence_threshold
            
            if not is_known:
                best_person = "unknown"
            
            result = RecognitionResult(
                person_id=best_person,
                confidence=confidence,
                is_known=is_known,
                timestamp=datetime.now(),
                distance=best_distance,
                model_name=self.model_name
            )
            
            logger.debug(f"Recognition result: {best_person} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error during face recognition: {e}")
            return RecognitionResult(
                person_id="unknown",
                confidence=0.0,
                is_known=False,
                timestamp=datetime.now()
            )
    
    def recognize_face_simple(self, face_image: np.ndarray) -> RecognitionResult:
        """Simplified face recognition using DeepFace.find."""
        if not DEEPFACE_AVAILABLE or not self.is_initialized:
            return RecognitionResult(
                person_id="unknown",
                confidence=0.0,
                is_known=False,
                timestamp=datetime.now()
            )
        
        try:
            # Save temporary image for DeepFace
            temp_path = "temp_face.jpg"
            cv2.imwrite(temp_path, face_image)
            
            # Use DeepFace.find to search in database
            results = DeepFace.find(
                img_path=temp_path,
                db_path=self.known_faces_path,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                distance_metric=self.distance_metric,
                enforce_detection=False,
                silent=True
            )
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Process results
            if len(results) > 0 and len(results[0]) > 0:
                # Get the best match
                best_match = results[0].iloc[0]
                identity_path = best_match['identity']
                distance = best_match[f'{self.model_name}_{self.distance_metric}']
                
                # Extract person ID from path
                person_id = os.path.basename(os.path.dirname(identity_path))
                confidence = self._distance_to_confidence(distance)
                is_known = confidence >= self.confidence_threshold
                
                if not is_known:
                    person_id = "unknown"
                
                return RecognitionResult(
                    person_id=person_id,
                    confidence=confidence,
                    is_known=is_known,
                    timestamp=datetime.now(),
                    distance=distance,
                    model_name=self.model_name
                )
            
            # No matches found
            return RecognitionResult(
                person_id="unknown",
                confidence=0.0,
                is_known=False,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in simple face recognition: {e}")
            return RecognitionResult(
                person_id="unknown",
                confidence=0.0,
                is_known=False,
                timestamp=datetime.now()
            )
    
    def _distance_to_confidence(self, distance: float) -> float:
        """Convert distance metric to confidence score (0-1)."""
        try:
            if self.distance_metric == 'cosine':
                # Cosine distance: 0 = identical, 1 = completely different
                confidence = max(0.0, 1.0 - distance)
            elif self.distance_metric == 'euclidean':
                # Euclidean distance: lower is better, normalize to 0-1
                confidence = max(0.0, 1.0 - (distance / 2.0))
            elif self.distance_metric == 'euclidean_l2':
                # L2 normalized euclidean
                confidence = max(0.0, 1.0 - distance)
            else:
                # Default normalization
                confidence = max(0.0, 1.0 - distance)
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error converting distance to confidence: {e}")
            return 0.0
    
    def get_confidence_threshold(self) -> float:
        """Get the current confidence threshold."""
        return self.confidence_threshold
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """Set the confidence threshold for recognition."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to {self.confidence_threshold}")
    
    def update_database(self) -> bool:
        """Refresh the face database."""
        return self.initialize_database()
    
    def get_known_persons(self) -> List[str]:
        """Get list of known person IDs."""
        return self.known_persons.copy()
    
    def add_person_images(self, person_id: str, images: List[np.ndarray]) -> bool:
        """Add new images for a person to the database."""
        try:
            person_path = os.path.join(self.known_faces_path, person_id)
            os.makedirs(person_path, exist_ok=True)
            
            for i, image in enumerate(images):
                image_path = os.path.join(person_path, f"image_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                cv2.imwrite(image_path, image)
            
            # Refresh database
            self.update_database()
            logger.info(f"Added {len(images)} images for person: {person_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding person images: {e}")
            return False
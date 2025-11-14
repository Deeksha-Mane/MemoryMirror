"""Database management for Memory Mirror application."""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

from src.database.models import PersonProfile, DatabaseSettings, RecognitionHistory

logger = logging.getLogger(__name__)

class PersonDatabase:
    """Main database interface for managing person profiles."""
    
    def __init__(self, known_faces_dir: str = "known_faces", 
                 metadata_file: str = "data/caregiver_data.json"):
        self.known_faces_dir = known_faces_dir
        self.metadata_file = metadata_file
        self.profiles: Dict[str, PersonProfile] = {}
        self.settings: DatabaseSettings = DatabaseSettings()
        self.recognition_history: List[RecognitionHistory] = []
        
        # Load data
        self.load_known_faces()
        self.load_metadata()
    
    def load_known_faces(self, directory_path: str = None) -> None:
        """Load known faces from directory structure."""
        if directory_path:
            self.known_faces_dir = directory_path
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.known_faces_dir, exist_ok=True)
            
            # Scan for person directories
            for person_dir in os.listdir(self.known_faces_dir):
                person_path = os.path.join(self.known_faces_dir, person_dir)
                
                if os.path.isdir(person_path):
                    # Check for image files
                    image_files = [f for f in os.listdir(person_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                    
                    if image_files:
                        # Create or update profile
                        if person_dir not in self.profiles:
                            self.profiles[person_dir] = PersonProfile(
                                person_id=person_dir,
                                name=person_dir.title(),
                                relationship="Unknown"
                            )
                        
                        # Set photo path to first image
                        self.profiles[person_dir].photo_path = os.path.join(person_path, image_files[0])
                        
                        logger.info(f"Loaded {len(image_files)} images for {person_dir}")
            
            logger.info(f"Loaded {len(self.profiles)} person profiles from directory")
            
        except Exception as e:
            logger.error(f"Error loading known faces: {e}")
    
    def load_metadata(self, json_path: str = None) -> None:
        """Load metadata from JSON file."""
        if json_path:
            self.metadata_file = json_path
        
        try:
            if not os.path.exists(self.metadata_file):
                logger.warning(f"Metadata file not found: {self.metadata_file}")
                self._create_default_metadata()
                return
            
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load person data
            persons_data = data.get("persons", {})
            for person_id, person_data in persons_data.items():
                if person_id in self.profiles:
                    # Update existing profile with metadata
                    profile = self.profiles[person_id]
                    profile.name = person_data.get("name", profile.name)
                    profile.relationship = person_data.get("relationship", profile.relationship)
                    profile.language_preference = person_data.get("language_preference", "en")
                    profile.voice_message = person_data.get("voice_message", "")
                    profile.voice_message_translations = person_data.get("voice_message_translations", {})
                else:
                    # Create new profile from metadata
                    self.profiles[person_id] = PersonProfile.from_dict(person_id, person_data)
            
            # Load settings
            settings_data = data.get("settings", {})
            self.settings = DatabaseSettings.from_dict(settings_data)
            
            logger.info(f"Loaded metadata for {len(persons_data)} persons")
            
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            self._create_default_metadata()
    
    def save_metadata(self) -> bool:
        """Save current metadata to JSON file."""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
            
            # Prepare data structure
            data = {
                "persons": {
                    person_id: profile.to_dict() 
                    for person_id, profile in self.profiles.items()
                },
                "settings": self.settings.to_dict()
            }
            
            # Write to file
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved metadata to {self.metadata_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False
    
    def get_person_profile(self, person_id: str) -> Optional[PersonProfile]:
        """Get person profile by ID."""
        return self.profiles.get(person_id)
    
    def get_all_profiles(self) -> List[PersonProfile]:
        """Get all person profiles."""
        return list(self.profiles.values())
    
    def add_person_profile(self, profile: PersonProfile) -> bool:
        """Add a new person profile."""
        try:
            self.profiles[profile.person_id] = profile
            
            # Create directory for person's images
            person_dir = os.path.join(self.known_faces_dir, profile.person_id)
            os.makedirs(person_dir, exist_ok=True)
            
            logger.info(f"Added person profile: {profile.person_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding person profile: {e}")
            return False
    
    def update_person_profile(self, person_id: str, **kwargs) -> bool:
        """Update person profile with new data."""
        try:
            if person_id not in self.profiles:
                logger.warning(f"Person not found: {person_id}")
                return False
            
            profile = self.profiles[person_id]
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.updated_at = datetime.now()
            
            logger.info(f"Updated person profile: {person_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating person profile: {e}")
            return False
    
    def remove_person_profile(self, person_id: str) -> bool:
        """Remove person profile."""
        try:
            if person_id in self.profiles:
                del self.profiles[person_id]
                logger.info(f"Removed person profile: {person_id}")
                return True
            else:
                logger.warning(f"Person not found: {person_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing person profile: {e}")
            return False
    
    def refresh_database(self) -> bool:
        """Refresh the entire database."""
        try:
            self.profiles.clear()
            self.load_known_faces()
            self.load_metadata()
            self.generate_face_encodings()
            logger.info("Database refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing database: {e}")
            return False
    
    def generate_face_encodings(self) -> None:
        """Generate and cache face encodings for all persons."""
        try:
            for person_id, profile in self.profiles.items():
                person_path = os.path.join(self.known_faces_dir, person_id)
                
                if os.path.exists(person_path):
                    image_paths = DatabaseLoader.get_image_paths(person_path)
                    
                    # Store image paths in profile for recognition system
                    profile.face_encodings = image_paths  # Store paths instead of actual encodings
                    
                    logger.debug(f"Cached {len(image_paths)} image paths for {person_id}")
            
            logger.info("Face encodings generated for all persons")
            
        except Exception as e:
            logger.error(f"Error generating face encodings: {e}")
    
    def get_person_images(self, person_id: str) -> List[str]:
        """Get all image paths for a specific person."""
        try:
            person_path = os.path.join(self.known_faces_dir, person_id)
            return DatabaseLoader.get_image_paths(person_path)
            
        except Exception as e:
            logger.error(f"Error getting person images: {e}")
            return []
    
    def validate_person_images(self, person_id: str) -> Dict[str, bool]:
        """Validate that all images for a person exist and are readable."""
        validation_results = {}
        
        try:
            import cv2
            
            image_paths = self.get_person_images(person_id)
            
            for image_path in image_paths:
                try:
                    # Try to load the image
                    image = cv2.imread(image_path)
                    validation_results[image_path] = image is not None
                    
                except Exception:
                    validation_results[image_path] = False
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating person images: {e}")
            return validation_results
    
    def add_recognition_event(self, person_id: str, confidence: float) -> None:
        """Add a recognition event to history."""
        try:
            event = RecognitionHistory(
                person_id=person_id,
                timestamp=datetime.now(),
                confidence=confidence
            )
            
            self.recognition_history.append(event)
            
            # Keep only recent history (last 1000 events)
            if len(self.recognition_history) > 1000:
                self.recognition_history = self.recognition_history[-1000:]
            
        except Exception as e:
            logger.error(f"Error adding recognition event: {e}")
    
    def get_recognition_history(self, person_id: str = None, 
                              limit: int = 100) -> List[RecognitionHistory]:
        """Get recognition history."""
        try:
            history = self.recognition_history
            
            # Filter by person if specified
            if person_id:
                history = [h for h in history if h.person_id == person_id]
            
            # Sort by timestamp (most recent first)
            history.sort(key=lambda h: h.timestamp, reverse=True)
            
            # Apply limit
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recognition history: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        try:
            stats = {
                "total_persons": len(self.profiles),
                "persons_with_images": 0,
                "total_recognition_events": len(self.recognition_history),
                "languages_used": set(),
                "last_updated": None
            }
            
            # Count persons with images and collect languages
            for profile in self.profiles.values():
                if profile.photo_path and os.path.exists(profile.photo_path):
                    stats["persons_with_images"] += 1
                
                stats["languages_used"].add(profile.language_preference)
                
                if profile.updated_at:
                    if not stats["last_updated"] or profile.updated_at > stats["last_updated"]:
                        stats["last_updated"] = profile.updated_at
            
            stats["languages_used"] = list(stats["languages_used"])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def _create_default_metadata(self) -> None:
        """Create default metadata file."""
        try:
            default_data = {
                "persons": {},
                "settings": self.settings.to_dict()
            }
            
            # Add any existing profiles
            for person_id, profile in self.profiles.items():
                default_data["persons"][person_id] = profile.to_dict()
            
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created default metadata file: {self.metadata_file}")
            
        except Exception as e:
            logger.error(f"Error creating default metadata: {e}")

class DatabaseLoader:
    """Utility class for loading data from filesystem."""
    
    @staticmethod
    def validate_directory_structure(known_faces_dir: str) -> Dict[str, List[str]]:
        """Validate and return directory structure."""
        structure = {}
        
        try:
            if not os.path.exists(known_faces_dir):
                return structure
            
            for person_dir in os.listdir(known_faces_dir):
                person_path = os.path.join(known_faces_dir, person_dir)
                
                if os.path.isdir(person_path):
                    image_files = [f for f in os.listdir(person_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                    
                    if image_files:
                        structure[person_dir] = image_files
            
            return structure
            
        except Exception as e:
            logger.error(f"Error validating directory structure: {e}")
            return structure
    
    @staticmethod
    def get_image_paths(person_dir: str) -> List[str]:
        """Get all image paths for a person."""
        image_paths = []
        
        try:
            if os.path.exists(person_dir):
                for filename in os.listdir(person_dir):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        image_paths.append(os.path.join(person_dir, filename))
            
            return image_paths
            
        except Exception as e:
            logger.error(f"Error getting image paths: {e}")
            return image_paths
    
    @staticmethod
    def load_face_encodings(known_faces_dir: str) -> Dict[str, List[str]]:
        """Load and cache face encodings for all known persons."""
        face_encodings = {}
        
        try:
            import cv2
            
            for person_dir in os.listdir(known_faces_dir):
                person_path = os.path.join(known_faces_dir, person_dir)
                
                if os.path.isdir(person_path):
                    image_paths = DatabaseLoader.get_image_paths(person_path)
                    
                    if image_paths:
                        # Store image paths for this person
                        face_encodings[person_dir] = image_paths
                        logger.info(f"Loaded {len(image_paths)} images for {person_dir}")
            
            return face_encodings
            
        except Exception as e:
            logger.error(f"Error loading face encodings: {e}")
            return face_encodings
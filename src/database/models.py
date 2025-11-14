"""Data models for Memory Mirror application."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np

@dataclass
class PersonProfile:
    """Individual person data structure."""
    person_id: str
    name: str
    relationship: str
    language_preference: str = "en"
    voice_message: str = ""
    voice_message_translations: Dict[str, str] = field(default_factory=dict)
    photo_path: str = ""
    face_encodings: List[np.ndarray] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_voice_message(self, language: str = None) -> str:
        """Get voice message in specified language or default."""
        if not language:
            language = self.language_preference
        
        # Try to get message in requested language
        if language in self.voice_message_translations:
            return self.voice_message_translations[language]
        
        # Fall back to default voice message
        if self.voice_message:
            return self.voice_message
        
        # Fall back to English if available
        if "en" in self.voice_message_translations:
            return self.voice_message_translations["en"]
        
        # Default greeting
        return f"Hello {self.name}!"
    
    def add_voice_message_translation(self, language: str, message: str) -> None:
        """Add a voice message translation."""
        self.voice_message_translations[language] = message
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "relationship": self.relationship,
            "language_preference": self.language_preference,
            "voice_message": self.voice_message,
            "voice_message_translations": self.voice_message_translations,
            "photo_path": self.photo_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, person_id: str, data: Dict) -> 'PersonProfile':
        """Create PersonProfile from dictionary."""
        profile = cls(
            person_id=person_id,
            name=data.get("name", person_id),
            relationship=data.get("relationship", "Unknown"),
            language_preference=data.get("language_preference", "en"),
            voice_message=data.get("voice_message", ""),
            voice_message_translations=data.get("voice_message_translations", {}),
            photo_path=data.get("photo_path", "")
        )
        
        # Parse timestamps if available
        if "created_at" in data and data["created_at"]:
            try:
                profile.created_at = datetime.fromisoformat(data["created_at"])
            except:
                pass
        
        if "updated_at" in data and data["updated_at"]:
            try:
                profile.updated_at = datetime.fromisoformat(data["updated_at"])
            except:
                pass
        
        return profile

@dataclass
class DatabaseSettings:
    """Database configuration settings."""
    default_language: str = "en"
    recognition_threshold: float = 0.6
    audio_enabled: bool = True
    message_cooldown_seconds: int = 30
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "default_language": self.default_language,
            "recognition_threshold": self.recognition_threshold,
            "audio_enabled": self.audio_enabled,
            "message_cooldown_seconds": self.message_cooldown_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DatabaseSettings':
        """Create DatabaseSettings from dictionary."""
        return cls(
            default_language=data.get("default_language", "en"),
            recognition_threshold=data.get("recognition_threshold", 0.6),
            audio_enabled=data.get("audio_enabled", True),
            message_cooldown_seconds=data.get("message_cooldown_seconds", 30)
        )

@dataclass
class RecognitionHistory:
    """History of recognition events."""
    person_id: str
    timestamp: datetime
    confidence: float
    location: str = "unknown"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "person_id": self.person_id,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "location": self.location
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RecognitionHistory':
        """Create RecognitionHistory from dictionary."""
        return cls(
            person_id=data["person_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            confidence=data["confidence"],
            location=data.get("location", "unknown")
        )
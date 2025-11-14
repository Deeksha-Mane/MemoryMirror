"""Text-to-speech functionality for Memory Mirror application."""

import os
import logging
import tempfile
from typing import Optional, List, Dict
from datetime import datetime, timedelta

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logging.warning("gTTS not available. Text-to-speech will be limited.")

from src.utils.config import config

logger = logging.getLogger(__name__)

class TTSEngine:
    """Text-to-speech conversion using Google TTS."""
    
    def __init__(self):
        self.cache_dir = "assets/audio"
        self.supported_languages = self._get_supported_languages()
        self.default_language = config.get('languages.default', 'en')
        self.speech_rate = config.get('audio.speech_rate', 1.0)
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache for generated audio files
        self.audio_cache: Dict[str, str] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
    
    def generate_speech(self, text: str, language: str = None) -> Optional[str]:
        """Generate speech audio file from text."""
        if not GTTS_AVAILABLE:
            logger.warning("gTTS not available for speech generation")
            return None
        
        if not text or not text.strip():
            return None
        
        if not language:
            language = self.default_language
        
        # Normalize language code for gTTS
        language = self._normalize_language_code(language)
        
        try:
            # Check cache first
            cache_key = f"{text}_{language}"
            if self._is_cached(cache_key):
                return self.audio_cache[cache_key]
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tts_{language}_{timestamp}.mp3"
            filepath = os.path.join(self.cache_dir, filename)
            
            # Generate speech
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(filepath)
            
            # Cache the result
            self.audio_cache[cache_key] = filepath
            self.cache_expiry[cache_key] = datetime.now() + self.cache_duration
            
            logger.info(f"Generated speech for text: '{text[:50]}...' in language: {language}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def generate_speech_bytes(self, text: str, language: str = None) -> Optional[bytes]:
        """Generate speech as bytes without saving to file."""
        if not GTTS_AVAILABLE:
            return None
        
        if not text or not text.strip():
            return None
        
        if not language:
            language = self.default_language
        
        language = self._normalize_language_code(language)
        
        try:
            # Use temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                tts = gTTS(text=text, lang=language, slow=False)
                tts.save(temp_file.name)
                
                # Read the file content
                with open(temp_file.name, 'rb') as f:
                    audio_bytes = f.read()
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                return audio_bytes
                
        except Exception as e:
            logger.error(f"Error generating speech bytes: {e}")
            return None
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return list(self.supported_languages.keys())
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        normalized = self._normalize_language_code(language)
        return normalized in self.supported_languages
    
    def set_speech_parameters(self, speed: float = None, pitch: float = None) -> None:
        """Set voice parameters (limited support in gTTS)."""
        if speed is not None:
            self.speech_rate = max(0.5, min(2.0, speed))
            logger.info(f"Speech rate set to: {self.speech_rate}")
        
        # Note: gTTS doesn't support pitch adjustment
        if pitch is not None:
            logger.warning("Pitch adjustment not supported by gTTS")
    
    def clear_cache(self) -> None:
        """Clear the audio cache."""
        try:
            # Remove cached files
            for filepath in self.audio_cache.values():
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            # Clear cache dictionaries
            self.audio_cache.clear()
            self.cache_expiry.clear()
            
            logger.info("Audio cache cleared")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def cleanup_expired_cache(self) -> None:
        """Remove expired cache entries."""
        try:
            current_time = datetime.now()
            expired_keys = []
            
            for cache_key, expiry_time in self.cache_expiry.items():
                if current_time > expiry_time:
                    expired_keys.append(cache_key)
            
            for key in expired_keys:
                filepath = self.audio_cache.get(key)
                if filepath and os.path.exists(filepath):
                    os.remove(filepath)
                
                del self.audio_cache[key]
                del self.cache_expiry[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {e}")
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if audio is cached and not expired."""
        if cache_key not in self.audio_cache:
            return False
        
        if cache_key not in self.cache_expiry:
            return False
        
        if datetime.now() > self.cache_expiry[cache_key]:
            # Remove expired entry
            filepath = self.audio_cache[cache_key]
            if os.path.exists(filepath):
                os.remove(filepath)
            del self.audio_cache[cache_key]
            del self.cache_expiry[cache_key]
            return False
        
        # Check if file still exists
        filepath = self.audio_cache[cache_key]
        if not os.path.exists(filepath):
            del self.audio_cache[cache_key]
            del self.cache_expiry[cache_key]
            return False
        
        return True
    
    def _normalize_language_code(self, language: str) -> str:
        """Normalize language code for gTTS compatibility."""
        # Map common language codes to gTTS supported codes
        language_mapping = {
            'hi': 'hi',  # Hindi
            'en': 'en',  # English
            'es': 'es',  # Spanish
            'fr': 'fr',  # French
            'de': 'de',  # German
            'zh': 'zh',  # Chinese
            'ja': 'ja',  # Japanese
            'ko': 'ko',  # Korean
            'ar': 'ar',  # Arabic
            'ru': 'ru',  # Russian
            'pt': 'pt',  # Portuguese
            'it': 'it',  # Italian
            'nl': 'nl',  # Dutch
            'sv': 'sv',  # Swedish
            'da': 'da',  # Danish
            'no': 'no',  # Norwegian
            'fi': 'fi',  # Finnish
        }
        
        # Convert to lowercase and get first 2 characters
        lang_code = language.lower()[:2]
        
        return language_mapping.get(lang_code, 'en')  # Default to English
    
    def _get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages."""
        return {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'ru': 'Russian',
            'pt': 'Portuguese',
            'it': 'Italian',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish'
        }
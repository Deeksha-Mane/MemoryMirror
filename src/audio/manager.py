"""Audio management for Memory Mirror application."""

import os
import logging
import threading
from typing import Optional, Dict
from datetime import datetime, timedelta

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logging.warning("pygame not available. Audio playback will be limited.")

from src.audio.tts import TTSEngine
from src.utils.config import config

logger = logging.getLogger(__name__)

class AudioManager:
    """Main audio interface for the Memory Mirror system."""
    
    def __init__(self):
        self.tts_engine = TTSEngine()
        self.volume = config.get('audio.volume', 0.8)
        self.audio_enabled = config.get('audio.audio_enabled', True)
        self.message_cooldown = config.get('audio.message_cooldown_seconds', 30)
        
        # Track last played messages to prevent spam
        self.last_played: Dict[str, datetime] = {}
        
        # Audio playback state
        self.is_playing = False
        self.current_audio_file = None
        self.playback_thread = None
        
        # Initialize pygame mixer if available
        if PYGAME_AVAILABLE and self.audio_enabled:
            self._initialize_audio()
    
    def _initialize_audio(self) -> bool:
        """Initialize the audio system."""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.music.set_volume(self.volume)
            logger.info("Audio system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing audio system: {e}")
            return False
    
    def play_voice_message(self, message: str, language: str = 'en', person_id: str = None) -> bool:
        """Play a voice message with text-to-speech."""
        if not self.audio_enabled:
            logger.debug("Audio disabled, skipping voice message")
            return False
        
        if not PYGAME_AVAILABLE:
            logger.warning("pygame not available, cannot play audio")
            return False
        
        if not message or not message.strip():
            logger.warning("Empty message, skipping audio")
            return False
        
        try:
            # Check cooldown period
            if person_id and self._is_in_cooldown(person_id):
                logger.debug(f"Message for {person_id} is in cooldown period")
                return False
            
            # Stop any currently playing audio
            self.stop_current_audio()
            
            # Generate speech audio
            audio_file = self.tts_engine.generate_speech(message, language)
            if not audio_file:
                logger.error("Failed to generate speech audio")
                return False
            
            # Play audio in separate thread
            self.playback_thread = threading.Thread(
                target=self._play_audio_file,
                args=(audio_file, person_id),
                daemon=True
            )
            self.playback_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error playing voice message: {e}")
            return False
    
    def _play_audio_file(self, audio_file: str, person_id: str = None) -> None:
        """Play an audio file using pygame."""
        try:
            if not os.path.exists(audio_file):
                logger.error(f"Audio file not found: {audio_file}")
                return
            
            self.is_playing = True
            self.current_audio_file = audio_file
            
            # Load and play the audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Update last played timestamp
            if person_id:
                self.last_played[person_id] = datetime.now()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            self.is_playing = False
            self.current_audio_file = None
            
            logger.debug(f"Finished playing audio: {audio_file}")
            
        except Exception as e:
            logger.error(f"Error playing audio file: {e}")
            self.is_playing = False
            self.current_audio_file = None
    
    def stop_current_audio(self) -> None:
        """Stop any currently playing audio."""
        try:
            if PYGAME_AVAILABLE and self.is_playing:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.current_audio_file = None
                logger.debug("Stopped current audio playback")
                
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
    
    def is_audio_playing(self) -> bool:
        """Check if audio is currently playing."""
        try:
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                return pygame.mixer.music.get_busy()
            return self.is_playing
            
        except Exception as e:
            logger.error(f"Error checking audio status: {e}")
            return False
    
    def set_volume(self, volume: float) -> None:
        """Set the audio volume (0.0 to 1.0)."""
        try:
            self.volume = max(0.0, min(1.0, volume))
            
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.music.set_volume(self.volume)
            
            logger.info(f"Audio volume set to: {self.volume}")
            
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
    
    def get_volume(self) -> float:
        """Get the current audio volume."""
        return self.volume
    
    def enable_audio(self) -> None:
        """Enable audio playback."""
        self.audio_enabled = True
        if PYGAME_AVAILABLE and not pygame.mixer.get_init():
            self._initialize_audio()
        logger.info("Audio enabled")
    
    def disable_audio(self) -> None:
        """Disable audio playback."""
        self.stop_current_audio()
        self.audio_enabled = False
        logger.info("Audio disabled")
    
    def is_audio_enabled(self) -> bool:
        """Check if audio is enabled."""
        return self.audio_enabled
    
    def set_message_cooldown(self, seconds: int) -> None:
        """Set the cooldown period between messages for the same person."""
        self.message_cooldown = max(0, seconds)
        logger.info(f"Message cooldown set to: {self.message_cooldown} seconds")
    
    def _is_in_cooldown(self, person_id: str) -> bool:
        """Check if a person's message is in cooldown period."""
        if person_id not in self.last_played:
            return False
        
        time_since_last = datetime.now() - self.last_played[person_id]
        return time_since_last.total_seconds() < self.message_cooldown
    
    def get_last_played_time(self, person_id: str) -> Optional[datetime]:
        """Get the last time a message was played for a person."""
        return self.last_played.get(person_id)
    
    def clear_cooldown_history(self) -> None:
        """Clear the cooldown history for all persons."""
        self.last_played.clear()
        logger.info("Cooldown history cleared")
    
    def play_system_sound(self, sound_type: str = 'notification') -> bool:
        """Play a system sound."""
        try:
            # Define system sounds
            system_sounds = {
                'notification': 'Hello! System ready.',
                'error': 'An error occurred.',
                'startup': 'Memory Mirror system starting up.',
                'shutdown': 'Memory Mirror system shutting down.'
            }
            
            message = system_sounds.get(sound_type, 'System notification.')
            return self.play_voice_message(message, 'en', f'system_{sound_type}')
            
        except Exception as e:
            logger.error(f"Error playing system sound: {e}")
            return False
    
    def test_audio_system(self) -> bool:
        """Test the audio system functionality."""
        try:
            test_message = "Audio system test. If you can hear this, audio is working correctly."
            result = self.play_voice_message(test_message, 'en', 'audio_test')
            
            if result:
                logger.info("Audio system test completed successfully")
            else:
                logger.warning("Audio system test failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing audio system: {e}")
            return False
    
    def get_audio_info(self) -> Dict:
        """Get information about the audio system."""
        try:
            info = {
                'audio_enabled': self.audio_enabled,
                'pygame_available': PYGAME_AVAILABLE,
                'volume': self.volume,
                'is_playing': self.is_audio_playing(),
                'current_file': self.current_audio_file,
                'message_cooldown': self.message_cooldown,
                'supported_languages': self.tts_engine.get_supported_languages(),
                'cache_dir': self.tts_engine.cache_dir
            }
            
            if PYGAME_AVAILABLE:
                try:
                    mixer_info = pygame.mixer.get_init()
                    info['mixer_initialized'] = mixer_info is not None
                    if mixer_info:
                        info['mixer_frequency'] = mixer_info[0]
                        info['mixer_format'] = mixer_info[1]
                        info['mixer_channels'] = mixer_info[2]
                except:
                    info['mixer_initialized'] = False
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {'error': str(e)}
    
    def cleanup(self) -> None:
        """Cleanup audio resources."""
        try:
            self.stop_current_audio()
            
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.quit()
            
            # Clean up TTS cache
            self.tts_engine.cleanup_expired_cache()
            
            logger.info("Audio system cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during audio cleanup: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.cleanup()
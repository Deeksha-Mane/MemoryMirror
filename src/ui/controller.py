"""UI controller for Memory Mirror Streamlit interface."""

import streamlit as st
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.ui.display import DisplayManager
from src.ui.language import language_manager
from src.database.models import PersonProfile
from src.recognition.recognizer import RecognitionResult
from src.audio.manager import AudioManager

logger = logging.getLogger(__name__)

class UIController:
    """Main interface controller that coordinates UI components."""
    
    def __init__(self):
        self.display_manager = DisplayManager()
        self.audio_manager = AudioManager()
        self.current_person = None
        self.last_recognition_time = None
        self.error_count = 0
        self.max_errors = 5
        
        # Initialize session state
        self._initialize_session_state()
    
    def initialize_interface(self) -> None:
        """Initialize the Streamlit interface."""
        try:
            # Apply custom styling
            self.display_manager.apply_theme_styling()
            
            # Set up the main layout
            st.title("🪞 Memory Mirror")
            st.markdown("---")
            
            # Create main content area
            self.main_container = st.container()
            
            # Create video feed placeholder
            self.video_placeholder = st.empty()
            
            # Create status area
            self.status_container = st.container()
            
            logger.info("UI interface initialized")
            
        except Exception as e:
            logger.error(f"Error initializing interface: {e}")
            self.handle_error_state(e)
    
    def update_display(self, recognition_result: RecognitionResult, 
                      person_profile: PersonProfile = None) -> None:
        """Update display based on recognition result."""
        try:
            with self.status_container:
                if recognition_result.is_known and person_profile:
                    # Display recognized person
                    self.show_person_info(person_profile, recognition_result.confidence)
                    
                    # Play voice message if enabled
                    self._play_person_voice_message(person_profile)
                    
                elif recognition_result.person_id == "unknown":
                    # Show unknown person state
                    self.display_manager.render_unknown_person_state()
                else:
                    # Show neutral state
                    self.show_neutral_state()
            
            self.last_recognition_time = datetime.now()
            self.error_count = 0  # Reset error count on successful update
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
            self.handle_error_state(e)
    
    def show_neutral_state(self, language: str = None) -> None:
        """Display the neutral 'Ready to recognize' state."""
        try:
            with self.status_container:
                self.display_manager.render_neutral_state(language)
            
            self.current_person = None
            
        except Exception as e:
            logger.error(f"Error showing neutral state: {e}")
            self.handle_error_state(e)
    
    def show_person_info(self, profile: PersonProfile, confidence: float = 0.0) -> None:
        """Display person information card."""
        try:
            with self.status_container:
                self.display_manager.render_person_card(profile, confidence)
            
            self.current_person = profile
            
            # Update session state
            st.session_state.last_recognized_person = profile.person_id
            st.session_state.last_recognition_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error showing person info: {e}")
            self.handle_error_state(e)
    
    def handle_error_state(self, error: Exception) -> None:
        """Handle and display error states."""
        try:
            self.error_count += 1
            
            # Determine error type and message
            error_message = self._get_user_friendly_error_message(error)
            
            with self.status_container:
                self.display_manager.render_error_state(error_message)
            
            # If too many errors, suggest restart
            if self.error_count >= self.max_errors:
                st.error("Multiple errors detected. Please restart the application.")
                st.stop()
            
        except Exception as e:
            logger.critical(f"Critical error in error handler: {e}")
            st.error("Critical system error. Please restart the application.")
            st.stop()
    
    def show_loading_state(self, message: str = "loading") -> None:
        """Show loading state with spinner."""
        try:
            with self.status_container:
                self.display_manager.render_loading_state(message)
                
        except Exception as e:
            logger.error(f"Error showing loading state: {e}")
    
    def show_status_message(self, message: str, message_type: str = "info", 
                           language: str = None) -> None:
        """Show a status message."""
        try:
            with self.status_container:
                self.display_manager.render_status_message(message, language, message_type)
                
        except Exception as e:
            logger.error(f"Error showing status message: {e}")
    
    def render_video_feed(self, frame) -> None:
        """Render the video feed."""
        try:
            self.display_manager.render_video_feed(frame, self.video_placeholder)
            
        except Exception as e:
            logger.error(f"Error rendering video feed: {e}")
    
    def render_sidebar(self, database_stats: Dict[str, Any] = None, 
                      audio_info: Dict[str, Any] = None) -> None:
        """Render sidebar with system information and controls."""
        try:
            with st.sidebar:
                st.markdown("### 🔧 System Status")
                
                # Database stats
                if database_stats:
                    st.markdown(f"**Persons:** {database_stats.get('total_persons', 0)}")
                    st.markdown(f"**With Photos:** {database_stats.get('persons_with_images', 0)}")
                    
                    languages = database_stats.get('languages_used', [])
                    if languages:
                        st.markdown(f"**Languages:** {', '.join(languages)}")
                
                # Audio status
                if audio_info:
                    audio_status = "🔊 Enabled" if audio_info.get('audio_enabled') else "🔇 Disabled"
                    st.markdown(f"**Audio:** {audio_status}")
                    
                    if audio_info.get('is_playing'):
                        st.markdown("🎵 **Playing audio...**")
                
                st.markdown("---")
                
                # Controls
                st.markdown("### 🎛️ Controls")
                
                # Language selector
                self._render_language_selector()
                
                # Audio controls
                self._render_audio_controls()
                
                # Display options
                self._render_display_options()
                
                # System actions
                self._render_system_actions()
                
        except Exception as e:
            logger.error(f"Error rendering sidebar: {e}")
    
    def _render_language_selector(self) -> None:
        """Render language selection dropdown."""
        try:
            languages = language_manager.get_supported_languages()
            current_lang = language_manager.get_current_language()
            
            selected_lang = st.selectbox(
                "Interface Language",
                languages,
                index=languages.index(current_lang) if current_lang in languages else 0,
                format_func=language_manager.get_language_name,
                key="language_selector"
            )
            
            if selected_lang != current_lang:
                language_manager.set_current_language(selected_lang)
                st.session_state.interface_language = selected_lang
                st.experimental_rerun()
                
        except Exception as e:
            logger.error(f"Error rendering language selector: {e}")
    
    def _render_audio_controls(self) -> None:
        """Render audio control buttons."""
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔊 Test Audio", key="test_audio"):
                    self.audio_manager.test_audio_system()
            
            with col2:
                if st.button("🔇 Stop Audio", key="stop_audio"):
                    self.audio_manager.stop_current_audio()
            
            # Volume slider
            current_volume = self.audio_manager.get_volume()
            new_volume = st.slider("Volume", 0.0, 1.0, current_volume, 0.1, key="volume_slider")
            
            if new_volume != current_volume:
                self.audio_manager.set_volume(new_volume)
                
        except Exception as e:
            logger.error(f"Error rendering audio controls: {e}")
    
    def _render_display_options(self) -> None:
        """Render display option controls."""
        try:
            # Show confidence scores
            show_confidence = st.checkbox(
                "Show Confidence Scores", 
                value=self.display_manager.display_confidence,
                key="show_confidence"
            )
            self.display_manager.set_display_confidence(show_confidence)
            
        except Exception as e:
            logger.error(f"Error rendering display options: {e}")
    
    def _render_system_actions(self) -> None:
        """Render system action buttons."""
        try:
            st.markdown("### ⚙️ Actions")
            
            if st.button("🔄 Refresh Database", key="refresh_db"):
                st.session_state.refresh_database = True
                st.experimental_rerun()
            
            if st.button("🧹 Clear Cache", key="clear_cache"):
                self.audio_manager.tts_engine.clear_cache()
                st.success("Cache cleared!")
            
        except Exception as e:
            logger.error(f"Error rendering system actions: {e}")
    
    def _play_person_voice_message(self, profile: PersonProfile) -> None:
        """Play voice message for recognized person."""
        try:
            if not self.audio_manager.is_audio_enabled():
                return
            
            # Get voice message in person's preferred language
            voice_message = profile.get_voice_message()
            
            if voice_message:
                self.audio_manager.play_voice_message(
                    voice_message, 
                    profile.language_preference, 
                    profile.person_id
                )
            else:
                # Use default greeting
                default_greeting = language_manager.format_person_greeting(
                    profile.name, 
                    profile.language_preference
                )
                self.audio_manager.play_voice_message(
                    default_greeting, 
                    profile.language_preference, 
                    profile.person_id
                )
                
        except Exception as e:
            logger.error(f"Error playing voice message: {e}")
    
    def _get_user_friendly_error_message(self, error: Exception) -> str:
        """Convert technical error to user-friendly message."""
        error_str = str(error).lower()
        
        if "camera" in error_str or "video" in error_str:
            return "camera_error"
        elif "recognition" in error_str or "deepface" in error_str:
            return "recognition_error"
        elif "audio" in error_str or "sound" in error_str:
            return "audio_disabled"
        elif "file" in error_str or "directory" in error_str:
            return "setup_required"
        else:
            return "processing"
    
    def _initialize_session_state(self) -> None:
        """Initialize Streamlit session state variables."""
        try:
            if 'initialized' not in st.session_state:
                st.session_state.initialized = True
                st.session_state.last_recognized_person = None
                st.session_state.last_recognition_time = None
                st.session_state.interface_language = language_manager.get_current_language()
                st.session_state.refresh_database = False
                st.session_state.error_count = 0
                
        except Exception as e:
            logger.error(f"Error initializing session state: {e}")
    
    def get_session_state(self, key: str, default=None):
        """Get value from session state."""
        return st.session_state.get(key, default)
    
    def set_session_state(self, key: str, value) -> None:
        """Set value in session state."""
        st.session_state[key] = value
    
    def cleanup(self) -> None:
        """Cleanup UI resources."""
        try:
            if hasattr(self, 'audio_manager'):
                self.audio_manager.cleanup()
            
            logger.info("UI controller cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during UI cleanup: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.cleanup()
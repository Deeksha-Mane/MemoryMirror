"""
Memory Mirror - Real-time Face Recognition System
Main Streamlit Application
"""

import streamlit as st
import cv2
import numpy as np
import time
import logging
from pathlib import Path

# Import our custom components with error handling
try:
    from src.video.capture import VideoCapture
    from src.recognition.detector import FaceDetector
    from src.recognition.recognizer import FaceRecognizer, RecognitionResult
    from src.database.manager import PersonDatabase
    from src.ui.controller import UIController
    from src.audio.manager import AudioManager
    from src.utils.config import config
    from src.utils.logging import setup_logging
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Component import error: {e}")
    COMPONENTS_AVAILABLE = False

# Setup logging
try:
    if COMPONENTS_AVAILABLE:
        setup_logging()
    logger = logging.getLogger(__name__)
except:
    # Fallback logging setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Memory Mirror",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .person-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .person-name {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .person-relationship {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .status-ready {
        background: #28a745;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
    }
    .status-unknown {
        background: #ffc107;
        color: #212529;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
    }
    .error-message {
        background: #dc3545;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class MemoryMirrorApp:
    """Main Memory Mirror application class."""
    
    def __init__(self):
        self.video_capture = None
        self.face_detector = None
        self.face_recognizer = None
        self.person_database = None
        self.ui_controller = None
        self.audio_manager = None
        self.last_recognition_time = {}
        self.recognition_cooldown = 30  # seconds between voice messages (prevents looping)
        
    def initialize_components(self):
        """Initialize all system components."""
        if not COMPONENTS_AVAILABLE:
            st.error("Required components are not available. Please check your installation.")
            return False
            
        try:
            # Initialize video capture first
            self.video_capture = VideoCapture()
            
            # Initialize face detector
            try:
                self.face_detector = FaceDetector()
            except Exception as e:
                logger.warning(f"Face detector initialization failed: {e}")
                self.face_detector = None
            
            # Initialize database first (before face recognizer)
            try:
                self.person_database = PersonDatabase()
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                self.person_database = None
                return False
            
            # Initialize face recognizer with database
            try:
                self.face_recognizer = FaceRecognizer()
                if self.person_database:
                    # Pass the known_faces directory path, not the database object
                    self.face_recognizer.initialize_database("known_faces")
            except Exception as e:
                logger.warning(f"Face recognizer initialization failed: {e}")
                self.face_recognizer = None
            
            # Initialize UI and audio (optional components)
            try:
                self.ui_controller = UIController()
            except Exception as e:
                logger.warning(f"UI controller initialization failed: {e}")
                self.ui_controller = None
                
            try:
                self.audio_manager = AudioManager()
            except Exception as e:
                logger.warning(f"Audio manager initialization failed: {e}")
                self.audio_manager = None
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            st.error(f"System initialization failed: {str(e)}")
            return False
    
    def should_play_message(self, person_id: str) -> bool:
        """Check if enough time has passed to play message again."""
        current_time = time.time()
        last_time = self.last_recognition_time.get(person_id, 0)
        return (current_time - last_time) > self.recognition_cooldown
    
    def process_frame(self, frame):
        """Process a single video frame for face recognition."""
        try:
            # Detect faces
            if not self.face_detector or not hasattr(self.face_detector, 'detect_faces'):
                return None, "error"
                
            faces = self.face_detector.detect_faces(frame)
            
            if not faces:
                return None, "ready"
            
            # If face recognizer is not available, just show detection
            if not self.face_recognizer:
                return None, "unknown"
            
            # Process first detected face
            try:
                face_data = faces[0]
                if hasattr(self.face_detector, 'extract_face_region'):
                    face_region = self.face_detector.extract_face_region(frame, face_data)
                else:
                    # Simple face extraction fallback
                    x, y, w, h = face_data
                    face_region = frame[y:y+h, x:x+w]
                
                # Recognize face
                if hasattr(self.face_recognizer, 'recognize_face'):
                    recognition_result = self.face_recognizer.recognize_face(face_region)
                    
                    if recognition_result and recognition_result.is_known:
                        # Check cooldown before playing message
                        if self.should_play_message(recognition_result.person_id):
                            if hasattr(self.person_database, 'get_person_profile'):
                                person_profile = self.person_database.get_person_profile(recognition_result.person_id)
                                if person_profile and hasattr(person_profile, 'voice_message'):
                                    if self.audio_manager and hasattr(self.audio_manager, 'play_voice_message'):
                                        self.audio_manager.play_voice_message(
                                            person_profile.voice_message,
                                            getattr(person_profile, 'language_preference', 'en')
                                        )
                            self.last_recognition_time[recognition_result.person_id] = time.time()
                        
                        return recognition_result, "recognized"
                    else:
                        return None, "unknown"
                else:
                    return None, "unknown"
                    
            except Exception as e:
                logger.warning(f"Face processing error: {e}")
                return None, "unknown"
                
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None, "error"
    
    def render_person_info(self, recognition_result):
        """Render recognized person information."""
        try:
            if hasattr(self.person_database, 'get_person_profile'):
                person_profile = self.person_database.get_person_profile(recognition_result.person_id)
            else:
                # Fallback to simple person lookup
                person_profile = getattr(self.person_database, 'persons', {}).get(recognition_result.person_id)
            
            if person_profile:
                # Handle both PersonProfile objects and dict data
                name = getattr(person_profile, 'name', person_profile.get('name', 'Unknown')) if hasattr(person_profile, 'name') or isinstance(person_profile, dict) else 'Unknown'
                relationship = getattr(person_profile, 'relationship', person_profile.get('relationship', 'Unknown')) if hasattr(person_profile, 'relationship') or isinstance(person_profile, dict) else 'Unknown'
                
                st.markdown(f"""
                <div class="person-card">
                    <div class="person-name">{name}</div>
                    <div class="person-relationship">{relationship}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display person's photo if available
                photo_path = getattr(person_profile, 'photo_path', person_profile.get('photo_path', '')) if hasattr(person_profile, 'photo_path') or isinstance(person_profile, dict) else ''
                if photo_path and Path(photo_path).exists():
                    st.image(photo_path, width=200)
                    
                # Display voice message with multilingual support
                voice_message = getattr(person_profile, 'voice_message', person_profile.get('voice_message', '')) if hasattr(person_profile, 'voice_message') or isinstance(person_profile, dict) else ''
                language_pref = getattr(person_profile, 'language_preference', person_profile.get('language_preference', 'en')) if hasattr(person_profile, 'language_preference') or isinstance(person_profile, dict) else 'en'
                translations = getattr(person_profile, 'voice_message_translations', person_profile.get('voice_message_translations', {})) if hasattr(person_profile, 'voice_message_translations') or isinstance(person_profile, dict) else {}
                
                if voice_message or translations:
                    # Show primary message
                    display_message = translations.get(language_pref, voice_message) if translations else voice_message
                    lang_names = {'en': 'English', 'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French'}
                    lang_display = lang_names.get(language_pref, language_pref.upper())
                    
                    st.info(f"💬 Message ({lang_display}): {display_message}")
                    
                    # Show audio status
                    if self.audio_manager:
                        st.success("🔊 Voice message played")
                    else:
                        st.warning("🔇 Audio not available")
                    
                    # Show available translations
                    if len(translations) > 1:
                        with st.expander("🌍 Other Languages"):
                            for lang_code, message in translations.items():
                                if lang_code != language_pref:
                                    lang_name = lang_names.get(lang_code, lang_code.upper())
                                    st.write(f"**{lang_name}:** {message}")
                                    
        except Exception as e:
            logger.error(f"Error rendering person info: {e}")
            st.error("Error displaying person information")
    
    def render_status_message(self, status: str):
        """Render status messages based on current state."""
        if status == "ready":
            st.markdown("""
            <div class="status-ready">
                🪞 Ready to recognize...
            </div>
            """, unsafe_allow_html=True)
        elif status == "unknown":
            st.markdown("""
            <div class="status-unknown">
                👤 Unknown person detected
            </div>
            """, unsafe_allow_html=True)
        elif status == "error":
            st.markdown("""
            <div class="error-message">
                ⚠️ Processing error occurred
            </div>
            """, unsafe_allow_html=True)
    
    def run(self):
        """Main application loop."""
        # Header
        st.markdown('<h1 class="main-header">🪞 Memory Mirror</h1>', unsafe_allow_html=True)
        
        # Initialize components if not done
        if not hasattr(st.session_state, 'components_initialized'):
            with st.spinner("Initializing Memory Mirror system..."):
                if self.initialize_components():
                    st.session_state.components_initialized = True
                    st.success("System initialized successfully!")
                else:
                    st.error("Failed to initialize system. Please check your setup.")
                    return
        
        # Create layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Live Camera Feed")
            video_placeholder = st.empty()
        
        with col2:
            st.subheader("Recognition Status")
            status_placeholder = st.empty()
            info_placeholder = st.empty()
        
        # Camera controls
        start_camera = st.button("Start Camera", type="primary")
        stop_camera = st.button("Stop Camera")
        
        if start_camera:
            st.session_state.camera_running = True
        
        if stop_camera:
            st.session_state.camera_running = False
            if self.video_capture:
                self.video_capture.release_camera()
        
        # Main camera loop
        if getattr(st.session_state, 'camera_running', False):
            try:
                if not self.video_capture or not self.video_capture.initialize_camera():
                    st.error("Failed to initialize camera. Please check your webcam connection.")
                    st.session_state.camera_running = False
                    return
                
                # Single frame processing for Streamlit
                frame = self.video_capture.get_frame()
                
                if frame is not None:
                    # Display video feed
                    video_placeholder.image(frame, channels="BGR", use_column_width=True)
                    
                    # Process frame for recognition
                    recognition_result, status = self.process_frame(frame)
                    
                    with status_placeholder.container():
                        if recognition_result and status == "recognized":
                            self.render_person_info(recognition_result)
                        else:
                            self.render_status_message(status)
                    
                    # Auto-refresh for continuous feed
                    time.sleep(0.1)
                    st.rerun()
                else:
                    st.error("Failed to capture frame from camera")
                    st.session_state.camera_running = False
                        
            except Exception as e:
                logger.error(f"Camera loop error: {e}")
                st.error(f"Camera error: {str(e)}")
                st.session_state.camera_running = False
            finally:
                if self.video_capture and not st.session_state.get('camera_running', False):
                    self.video_capture.release_camera()

def main():
    """Main entry point."""
    app = MemoryMirrorApp()
    app.run()

if __name__ == "__main__":
    main()
"""
Memory Mirror - Simplified Working Version
Main Streamlit Application
"""

import streamlit as st
import cv2
import numpy as np
import time
import json
import os
from pathlib import Path
import logging

# Try to import audio libraries
try:
    from gtts import gTTS
    import pygame
    import io
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("Audio libraries not available. Voice messages will be disabled.")

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Memory Mirror",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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

class SimpleVideoCapture:
    """Simple video capture class."""
    
    def __init__(self):
        self.cap = None
        self.is_initialized = False
    
    def initialize_camera(self, device_index=0):
        """Initialize camera."""
        try:
            self.cap = cv2.VideoCapture(device_index)
            if self.cap.isOpened():
                self.is_initialized = True
                return True
            return False
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return False
    
    def get_frame(self):
        """Get frame from camera."""
        if not self.is_initialized or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def release_camera(self):
        """Release camera."""
        if self.cap:
            self.cap.release()
            self.is_initialized = False

class SimpleFaceDetector:
    """Simple face detector using OpenCV."""
    
    def __init__(self):
        try:
            # Load OpenCV face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            self.is_available = True
        except Exception as e:
            logger.error(f"Face detector initialization error: {e}")
            self.is_available = False
    
    def detect_faces(self, frame):
        """Detect faces in frame."""
        if not self.is_available:
            return []
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            return faces
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []

class SimpleAudioManager:
    """Simple audio manager for voice messages."""
    
    def __init__(self):
        self.audio_enabled = AUDIO_AVAILABLE
        self.is_playing = False
        self.current_message = None
        
        if self.audio_enabled:
            try:
                pygame.mixer.init()
                logger.info("Audio system initialized")
            except Exception as e:
                logger.error(f"Audio initialization failed: {e}")
                self.audio_enabled = False
    
    def is_currently_playing(self):
        """Check if audio is currently playing."""
        if not self.audio_enabled:
            return False
        
        try:
            return pygame.mixer.music.get_busy()
        except:
            return False
    
    def play_voice_message(self, text, language='en'):
        """Play voice message using text-to-speech - plays only once."""
        if not self.audio_enabled:
            return False
        
        # Don't play if already playing
        if self.is_currently_playing():
            logger.info("Audio already playing, skipping new message")
            return False
        
        # Don't play the same message again
        if self.current_message == text:
            logger.info("Same message already played recently, skipping")
            return False
        
        try:
            # Generate speech
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to memory buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Play audio once (loops=0 means play once)
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play(loops=0)  # Explicitly set to play once
            
            self.is_playing = True
            self.current_message = text
            
            logger.info(f"Playing voice message once: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error playing voice message: {e}")
            return False
    
    def stop_audio(self):
        """Stop current audio playback."""
        if self.audio_enabled:
            try:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.current_message = None
            except Exception as e:
                logger.error(f"Error stopping audio: {e}")

class SimplePersonDatabase:
    """Simple person database."""
    
    def __init__(self):
        self.persons = {}
        self.settings = {}
        self.load_data()
    
    def load_data(self):
        """Load person data from JSON."""
        try:
            if os.path.exists("data/caregiver_data.json"):
                with open("data/caregiver_data.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.persons = data.get("persons", {})
                    self.settings = data.get("settings", {})
                logger.info(f"Loaded {len(self.persons)} persons from database")
            else:
                logger.warning("No caregiver data file found")
        except Exception as e:
            logger.error(f"Error loading person data: {e}")
    
    def get_person_info(self, person_id):
        """Get person information."""
        return self.persons.get(person_id, None)
    
    def get_voice_message(self, person_id, language=None):
        """Get voice message for person in specified language."""
        person_info = self.get_person_info(person_id)
        if not person_info:
            return None, 'en'
        
        # Use person's preferred language if not specified
        if not language:
            language = person_info.get('language_preference', 'en')
        
        # Try to get message in requested language
        translations = person_info.get('voice_message_translations', {})
        if language in translations:
            return translations[language], language
        
        # Fall back to default voice message
        default_message = person_info.get('voice_message', '')
        if default_message:
            return default_message, person_info.get('language_preference', 'en')
        
        # Final fallback
        return f"Hello {person_info.get('name', 'friend')}!", 'en'

class MemoryMirrorApp:
    """Main Memory Mirror application."""
    
    def __init__(self):
        self.video_capture = SimpleVideoCapture()
        self.face_detector = SimpleFaceDetector()
        self.person_database = SimplePersonDatabase()
        self.audio_manager = SimpleAudioManager()
        self.last_detection_time = 0
        self.last_voice_time = {}
        self.detection_cooldown = 2  # seconds
        self.voice_cooldown = 30  # seconds between voice messages (increased to prevent loops)
    
    def simulate_recognition(self, faces):
        """Simulate face recognition (placeholder)."""
        current_time = time.time()
        
        # Simple simulation - if faces detected and enough time passed
        if len(faces) > 0 and (current_time - self.last_detection_time) > self.detection_cooldown:
            self.last_detection_time = current_time
            
            # Simulate recognizing first person in database
            person_ids = list(self.person_database.persons.keys())
            if person_ids:
                person_id = person_ids[0]  # Return first person as "recognized"
                
                # Play voice message only if enough time has passed AND not currently playing
                if self.should_play_voice_message(person_id) and not self.audio_manager.is_currently_playing():
                    self.play_person_voice_message(person_id)
                
                return person_id
        
        return None
    
    def should_play_voice_message(self, person_id):
        """Check if enough time has passed to play voice message again."""
        current_time = time.time()
        last_time = self.last_voice_time.get(person_id, 0)
        
        # Only play if enough time has passed AND audio is not currently playing
        time_passed = (current_time - last_time) > self.voice_cooldown
        not_playing = not self.audio_manager.is_currently_playing()
        
        return time_passed and not_playing
    
    def play_person_voice_message(self, person_id):
        """Play voice message for recognized person."""
        try:
            message, language = self.person_database.get_voice_message(person_id)
            if message and self.audio_manager.play_voice_message(message, language):
                self.last_voice_time[person_id] = time.time()
                return True
        except Exception as e:
            logger.error(f"Error playing voice message: {e}")
        return False
    
    def render_person_info(self, person_id):
        """Render person information."""
        person_info = self.person_database.get_person_info(person_id)
        
        if person_info:
            # Get person's preferred language
            preferred_lang = person_info.get('language_preference', 'en')
            
            st.markdown(f"""
            <div class="person-card">
                <div class="person-name">{person_info.get('name', 'Unknown')}</div>
                <div class="person-relationship">{person_info.get('relationship', 'Unknown')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display voice message in preferred language
            voice_message, message_lang = self.person_database.get_voice_message(person_id, preferred_lang)
            if voice_message:
                # Show language indicator
                lang_names = {'en': 'English', 'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French'}
                lang_display = lang_names.get(message_lang, message_lang.upper())
                
                st.info(f"💬 Message ({lang_display}): {voice_message}")
                
                # Show audio status
                if AUDIO_AVAILABLE:
                    if self.audio_manager.is_currently_playing():
                        st.success("🔊 Playing voice message...")
                    else:
                        # Check if message was played recently
                        current_time = time.time()
                        last_played = self.last_voice_time.get(person_id, 0)
                        if (current_time - last_played) < 5:  # Within last 5 seconds
                            st.info("✅ Voice message played")
                        else:
                            st.info("🎵 Voice message available")
                else:
                    st.warning("🔇 Audio not available (install gtts and pygame for voice messages)")
            
            # Show available translations
            translations = person_info.get('voice_message_translations', {})
            if len(translations) > 1:
                st.write("**Available in languages:**")
                for lang_code, message in translations.items():
                    lang_name = {'en': 'English', 'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French'}.get(lang_code, lang_code.upper())
                    with st.expander(f"{lang_name} ({lang_code})"):
                        st.write(message)
    
    def render_status(self, status, faces_count=0):
        """Render status message."""
        if status == "ready":
            st.markdown("""
            <div class="status-ready">
                🪞 Ready to recognize...
            </div>
            """, unsafe_allow_html=True)
        elif status == "detecting":
            st.markdown(f"""
            <div class="status-unknown">
                👤 {faces_count} face(s) detected - Processing...
            </div>
            """, unsafe_allow_html=True)
        elif status == "error":
            st.markdown("""
            <div class="error-message">
                ⚠️ Camera error occurred
            </div>
            """, unsafe_allow_html=True)
    
    def run(self):
        """Main application."""
        # Header
        st.markdown('<h1 class="main-header">🪞 Memory Mirror</h1>', unsafe_allow_html=True)
        
        # Info section
        with st.expander("ℹ️ Setup Information", expanded=False):
            st.markdown("""
            **To use this demo:**
            1. Click "Start Camera" to begin
            2. Make sure your webcam is connected
            3. The system will detect faces and simulate recognition
            4. Person information is loaded from `data/caregiver_data.json`
            
            **Features:**
            - 🎵 Voice messages in multiple languages
            - 🌍 Multilingual support (English, Hindi, Spanish, French)
            - 🔊 Text-to-speech audio playback
            
            **Note:** This is a simplified demo version. Face recognition is simulated.
            """)
        
        # Language and Audio Settings
        with st.expander("🌍 Language & Audio Settings", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Audio Status:**")
                if AUDIO_AVAILABLE:
                    st.success("✅ Audio system available")
                    if pygame.mixer.get_init():
                        st.info("🎵 Audio initialized")
                    else:
                        st.warning("⚠️ Audio not initialized")
                else:
                    st.error("❌ Audio not available")
                    st.write("Install: `pip install gtts pygame`")
            
            with col2:
                st.write("**Supported Languages:**")
                st.write("🇺🇸 English (en)")
                st.write("🇮🇳 Hindi (hi)")
                st.write("🇪🇸 Spanish (es)")
                st.write("🇫🇷 French (fr)")
                
                # Audio control buttons
                col_test, col_stop = st.columns(2)
                
                with col_test:
                    if st.button("🔊 Test Voice"):
                        if AUDIO_AVAILABLE:
                            test_message = "Hello! This is a test message from Memory Mirror."
                            if self.audio_manager.play_voice_message(test_message, 'en'):
                                st.success("Playing test message...")
                            else:
                                st.error("Failed to play test message")
                        else:
                            st.error("Audio not available")
                
                with col_stop:
                    if st.button("⏹️ Stop Audio"):
                        if AUDIO_AVAILABLE:
                            self.audio_manager.stop_audio()
                            st.info("Audio stopped")
                        else:
                            st.error("Audio not available")
        
        # Layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📹 Live Camera Feed")
            video_placeholder = st.empty()
        
        with col2:
            st.subheader("🔍 Recognition Status")
            status_placeholder = st.empty()
        
        # Controls
        col_start, col_stop = st.columns(2)
        with col_start:
            start_camera = st.button("🎥 Start Camera", type="primary", use_container_width=True)
        with col_stop:
            stop_camera = st.button("⏹️ Stop Camera", use_container_width=True)
        
        # Initialize session state
        if 'camera_running' not in st.session_state:
            st.session_state.camera_running = False
        
        if start_camera:
            if self.video_capture.initialize_camera():
                st.session_state.camera_running = True
                st.success("Camera started successfully!")
            else:
                st.error("Failed to start camera. Please check your webcam connection.")
        
        if stop_camera:
            st.session_state.camera_running = False
            self.video_capture.release_camera()
            st.info("Camera stopped.")
        
        # Main camera loop
        if st.session_state.camera_running:
            try:
                frame_count = 0
                status = "ready"
                recognized_person = None
                
                # Create a placeholder for continuous updates
                while st.session_state.camera_running:
                    frame = self.video_capture.get_frame()
                    
                    if frame is not None:
                        # Display frame
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                        
                        # Process every 10th frame for performance
                        if frame_count % 10 == 0:
                            faces = self.face_detector.detect_faces(frame)
                            
                            if len(faces) > 0:
                                # Draw rectangles around faces
                                frame_with_faces = frame_rgb.copy()
                                for (x, y, w, h) in faces:
                                    cv2.rectangle(frame_with_faces, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                video_placeholder.image(frame_with_faces, channels="RGB", use_column_width=True)
                                
                                # Simulate recognition
                                recognized_person = self.simulate_recognition(faces)
                                status = "detecting" if not recognized_person else "recognized"
                            else:
                                status = "ready"
                                recognized_person = None
                            
                            # Update status
                            with status_placeholder.container():
                                if recognized_person:
                                    self.render_person_info(recognized_person)
                                else:
                                    self.render_status(status, len(faces))
                        
                        frame_count += 1
                        time.sleep(0.1)  # Control frame rate
                        
                        # Break if camera stopped
                        if not st.session_state.camera_running:
                            break
                    else:
                        st.error("Failed to capture frame")
                        break
                        
            except Exception as e:
                logger.error(f"Camera loop error: {e}")
                st.error(f"Camera error: {str(e)}")
            finally:
                self.video_capture.release_camera()

def main():
    """Main entry point."""
    app = MemoryMirrorApp()
    app.run()

if __name__ == "__main__":
    main()
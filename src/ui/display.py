"""Display management for Memory Mirror Streamlit interface."""

import streamlit as st
import cv2
import numpy as np
import logging
from typing import Optional, Dict, Any
from PIL import Image
import os

from src.database.models import PersonProfile
from src.ui.language import language_manager

logger = logging.getLogger(__name__)

class DisplayManager:
    """Handles UI state and updates for the Streamlit interface."""
    
    def __init__(self):
        self.current_state = "neutral"
        self.last_person_id = None
        self.display_confidence = False
        
        # Initialize Streamlit page config if not already set
        try:
            st.set_page_config(
                page_title="Memory Mirror",
                page_icon="🪞",
                layout="wide",
                initial_sidebar_state="collapsed"
            )
        except:
            pass  # Page config already set
    
    def render_video_feed(self, frame: np.ndarray, placeholder=None) -> None:
        """Render the video feed in Streamlit."""
        try:
            if frame is None:
                return
            
            # Convert BGR to RGB for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            
            # Display in Streamlit
            if placeholder:
                placeholder.image(pil_image, channels="RGB", use_column_width=True)
            else:
                st.image(pil_image, channels="RGB", use_column_width=True)
                
        except Exception as e:
            logger.error(f"Error rendering video feed: {e}")
    
    def render_person_card(self, profile: PersonProfile, confidence: float = 0.0) -> None:
        """Render person information card."""
        try:
            # Get language for this person
            language = profile.language_preference
            language_manager.set_current_language(language)
            
            # Create columns for layout
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display person's photo
                if profile.photo_path and os.path.exists(profile.photo_path):
                    try:
                        image = Image.open(profile.photo_path)
                        st.image(image, width=200, caption=profile.name)
                    except Exception as e:
                        logger.error(f"Error loading person photo: {e}")
                        self._render_default_avatar(profile.name)
                else:
                    self._render_default_avatar(profile.name)
            
            with col2:
                # Display person information
                st.markdown(f"### {profile.name}")
                
                # Relationship
                relationship_label = language_manager.translate_text('relationship', language)
                st.markdown(f"**{relationship_label}:** {profile.relationship}")
                
                # Language
                language_label = language_manager.translate_text('language', language)
                language_name = language_manager.get_language_name(profile.language_preference)
                st.markdown(f"**{language_label}:** {language_name}")
                
                # Confidence (if enabled)
                if self.display_confidence and confidence > 0:
                    confidence_label = language_manager.translate_text('confidence', language)
                    st.markdown(f"**{confidence_label}:** {confidence:.1%}")
                
                # Last seen
                last_seen_label = language_manager.translate_text('last_seen', language)
                st.markdown(f"**{last_seen_label}:** Just now")
            
            # Display personalized message
            voice_message = profile.get_voice_message(language)
            if voice_message:
                st.info(f"💬 {voice_message}")
            
            self.current_state = "recognized"
            self.last_person_id = profile.person_id
            
        except Exception as e:
            logger.error(f"Error rendering person card: {e}")
    
    def render_status_message(self, message: str, language: str = None, 
                            message_type: str = "info") -> None:
        """Render status message with appropriate styling."""
        try:
            if not language:
                language = language_manager.get_current_language()
            
            # Translate message if it's a key
            translated_message = language_manager.translate_text(message, language)
            
            # Display with appropriate styling
            if message_type == "error":
                st.error(f"❌ {translated_message}")
            elif message_type == "warning":
                st.warning(f"⚠️ {translated_message}")
            elif message_type == "success":
                st.success(f"✅ {translated_message}")
            else:
                st.info(f"ℹ️ {translated_message}")
            
            self.current_state = "status"
            
        except Exception as e:
            logger.error(f"Error rendering status message: {e}")
    
    def render_neutral_state(self, language: str = None) -> None:
        """Render the neutral 'Ready to recognize' state."""
        try:
            if not language:
                language = language_manager.get_current_language()
            
            # Center the content
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("### 🪞 Memory Mirror")
                
                # Ready message
                ready_message = language_manager.translate_text('ready_to_recognize', language)
                st.markdown(f"<div style='text-align: center; font-size: 1.2em; color: #666;'>{ready_message}</div>", 
                           unsafe_allow_html=True)
                
                # System status
                system_ready = language_manager.translate_text('system_ready', language)
                st.success(f"✅ {system_ready}")
            
            self.current_state = "neutral"
            self.last_person_id = None
            
        except Exception as e:
            logger.error(f"Error rendering neutral state: {e}")
    
    def render_unknown_person_state(self, language: str = None) -> None:
        """Render the unknown person detected state."""
        try:
            if not language:
                language = language_manager.get_current_language()
            
            # Center the content
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("### 👤 Unknown Person")
                
                # Unknown person message
                unknown_message = language_manager.translate_text('unknown_person', language)
                st.markdown(f"<div style='text-align: center; font-size: 1.2em; color: #ff6b6b;'>{unknown_message}</div>", 
                           unsafe_allow_html=True)
                
                # Suggestion
                setup_message = language_manager.translate_text('setup_required', language)
                st.info(f"💡 {setup_message}")
            
            self.current_state = "unknown"
            self.last_person_id = None
            
        except Exception as e:
            logger.error(f"Error rendering unknown person state: {e}")
    
    def render_loading_state(self, message: str = "loading", language: str = None) -> None:
        """Render loading state with spinner."""
        try:
            if not language:
                language = language_manager.get_current_language()
            
            loading_message = language_manager.translate_text(message, language)
            
            with st.spinner(loading_message):
                st.empty()  # Placeholder for spinner
            
            self.current_state = "loading"
            
        except Exception as e:
            logger.error(f"Error rendering loading state: {e}")
    
    def render_error_state(self, error_message: str, language: str = None) -> None:
        """Render error state with user-friendly message."""
        try:
            if not language:
                language = language_manager.get_current_language()
            
            # Center the content
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("### ❌ System Error")
                
                # Error message
                translated_error = language_manager.translate_text(error_message, language)
                st.error(f"🚨 {translated_error}")
                
                # Troubleshooting suggestions
                st.markdown("**Troubleshooting:**")
                st.markdown("- Check camera connection")
                st.markdown("- Ensure proper lighting")
                st.markdown("- Restart the application")
            
            self.current_state = "error"
            
        except Exception as e:
            logger.error(f"Error rendering error state: {e}")
    
    def apply_theme_styling(self) -> None:
        """Apply custom CSS styling to the Streamlit app."""
        try:
            st.markdown("""
            <style>
            .main {
                padding-top: 2rem;
            }
            
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
                color: white;
                text-align: center;
            }
            
            .stImage {
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            .stInfo, .stSuccess, .stWarning, .stError {
                border-radius: 10px;
                margin: 1rem 0;
            }
            
            .person-card {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .status-message {
                text-align: center;
                font-size: 1.2em;
                margin: 2rem 0;
            }
            
            .video-container {
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            </style>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error applying theme styling: {e}")
    
    def _render_default_avatar(self, name: str) -> None:
        """Render a default avatar when no photo is available."""
        try:
            # Create a simple colored circle with initials
            initials = ''.join([word[0].upper() for word in name.split()[:2]])
            
            st.markdown(f"""
            <div style="
                width: 200px;
                height: 200px;
                border-radius: 50%;
                background: linear-gradient(45deg, #667eea, #764ba2);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 3em;
                font-weight: bold;
                margin: 0 auto;
            ">
                {initials}
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Error rendering default avatar: {e}")
    
    def get_current_state(self) -> str:
        """Get the current display state."""
        return self.current_state
    
    def set_display_confidence(self, show_confidence: bool) -> None:
        """Set whether to display confidence scores."""
        self.display_confidence = show_confidence
    
    def clear_display(self) -> None:
        """Clear the current display."""
        try:
            st.empty()
            self.current_state = "neutral"
            self.last_person_id = None
            
        except Exception as e:
            logger.error(f"Error clearing display: {e}")
    
    def render_sidebar_info(self, stats: Dict[str, Any] = None) -> None:
        """Render sidebar with system information."""
        try:
            with st.sidebar:
                st.markdown("### 🔧 System Info")
                
                if stats:
                    st.markdown(f"**Persons in Database:** {stats.get('total_persons', 0)}")
                    st.markdown(f"**With Photos:** {stats.get('persons_with_images', 0)}")
                    st.markdown(f"**Languages:** {', '.join(stats.get('languages_used', []))}")
                
                st.markdown("### 🎛️ Controls")
                
                # Language selector
                languages = language_manager.get_supported_languages()
                current_lang = language_manager.get_current_language()
                
                selected_lang = st.selectbox(
                    "Interface Language",
                    languages,
                    index=languages.index(current_lang) if current_lang in languages else 0,
                    format_func=language_manager.get_language_name
                )
                
                if selected_lang != current_lang:
                    language_manager.set_current_language(selected_lang)
                    st.experimental_rerun()
                
                # Display confidence toggle
                show_confidence = st.checkbox("Show Confidence Scores", value=self.display_confidence)
                self.set_display_confidence(show_confidence)
                
        except Exception as e:
            logger.error(f"Error rendering sidebar: {e}")
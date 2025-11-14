"""Language support for Memory Mirror application."""

import logging
from typing import Dict, List, Optional
from src.utils.config import config

logger = logging.getLogger(__name__)

class LanguageManager:
    """Manages multilingual content and translations."""
    
    def __init__(self):
        self.supported_languages = config.get('languages.supported', ['en', 'hi', 'es', 'fr'])
        self.default_language = config.get('languages.default', 'en')
        self.current_language = self.default_language
        
        # Load default messages
        self.messages = self._load_default_messages()
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return self.supported_languages.copy()
    
    def set_current_language(self, language: str) -> bool:
        """Set the current language."""
        if language in self.supported_languages:
            self.current_language = language
            logger.info(f"Language set to: {language}")
            return True
        else:
            logger.warning(f"Unsupported language: {language}")
            return False
    
    def get_current_language(self) -> str:
        """Get the current language."""
        return self.current_language
    
    def translate_text(self, text_key: str, language: str = None, **kwargs) -> str:
        """Get translated text for the given key and language."""
        if not language:
            language = self.current_language
        
        try:
            # Get message in requested language
            if language in self.messages and text_key in self.messages[language]:
                message = self.messages[language][text_key]
            # Fall back to default language
            elif self.default_language in self.messages and text_key in self.messages[self.default_language]:
                message = self.messages[self.default_language][text_key]
            # Fall back to key itself
            else:
                message = text_key
            
            # Format message with any provided parameters
            if kwargs:
                try:
                    message = message.format(**kwargs)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Error formatting message '{text_key}': {e}")
            
            return message
            
        except Exception as e:
            logger.error(f"Error translating text '{text_key}': {e}")
            return text_key
    
    def get_default_messages(self, language: str = None) -> Dict[str, str]:
        """Get all default messages for a language."""
        if not language:
            language = self.current_language
        
        return self.messages.get(language, self.messages.get(self.default_language, {}))
    
    def add_custom_message(self, text_key: str, language: str, message: str) -> None:
        """Add a custom message for a specific language."""
        try:
            if language not in self.messages:
                self.messages[language] = {}
            
            self.messages[language][text_key] = message
            logger.info(f"Added custom message '{text_key}' for language '{language}'")
            
        except Exception as e:
            logger.error(f"Error adding custom message: {e}")
    
    def get_language_name(self, language_code: str) -> str:
        """Get the display name for a language code."""
        language_names = {
            'en': 'English',
            'hi': 'हिन्दी (Hindi)',
            'es': 'Español (Spanish)',
            'fr': 'Français (French)',
            'de': 'Deutsch (German)',
            'zh': '中文 (Chinese)',
            'ja': '日本語 (Japanese)',
            'ko': '한국어 (Korean)',
            'ar': 'العربية (Arabic)',
            'ru': 'Русский (Russian)'
        }
        
        return language_names.get(language_code, language_code.upper())
    
    def _load_default_messages(self) -> Dict[str, Dict[str, str]]:
        """Load default messages for all supported languages."""
        messages = {
            'en': {
                'ready_to_recognize': 'Ready to recognize...',
                'unknown_person': 'Unknown person detected',
                'no_camera': 'Camera not available',
                'camera_error': 'Camera error occurred',
                'recognition_error': 'Recognition error occurred',
                'loading': 'Loading...',
                'welcome': 'Welcome!',
                'hello': 'Hello!',
                'goodbye': 'Goodbye!',
                'good_morning': 'Good morning!',
                'good_afternoon': 'Good afternoon!',
                'good_evening': 'Good evening!',
                'name': 'Name',
                'relationship': 'Relationship',
                'language': 'Language',
                'confidence': 'Confidence',
                'last_seen': 'Last seen',
                'audio_disabled': 'Audio disabled',
                'processing': 'Processing...',
                'system_ready': 'Memory Mirror System Ready',
                'person_recognized': 'Person recognized: {name}',
                'default_greeting': 'Hello {name}! Nice to see you!',
                'setup_required': 'Please add photos to the known_faces directory',
                'no_faces_detected': 'No faces detected in camera feed'
            },
            'hi': {
                'ready_to_recognize': 'पहचानने के लिए तैयार...',
                'unknown_person': 'अज्ञात व्यक्ति का पता चला',
                'no_camera': 'कैमरा उपलब्ध नहीं है',
                'camera_error': 'कैमरा त्रुटि हुई',
                'recognition_error': 'पहचान त्रुटि हुई',
                'loading': 'लोड हो रहा है...',
                'welcome': 'स्वागत है!',
                'hello': 'नमस्ते!',
                'goodbye': 'अलविदा!',
                'good_morning': 'सुप्रभात!',
                'good_afternoon': 'नमस्कार!',
                'good_evening': 'शुभ संध्या!',
                'name': 'नाम',
                'relationship': 'रिश्ता',
                'language': 'भाषा',
                'confidence': 'विश्वास',
                'last_seen': 'अंतिम बार देखा गया',
                'audio_disabled': 'ऑडियो अक्षम',
                'processing': 'प्रसंस्करण...',
                'system_ready': 'मेमोरी मिरर सिस्टम तैयार',
                'person_recognized': 'व्यक्ति पहचाना गया: {name}',
                'default_greeting': 'नमस्ते {name}! आपको देखकर खुशी हुई!',
                'setup_required': 'कृपया known_faces निर्देशिका में फोटो जोड़ें',
                'no_faces_detected': 'कैमरा फीड में कोई चेहरा नहीं मिला'
            },
            'es': {
                'ready_to_recognize': 'Listo para reconocer...',
                'unknown_person': 'Persona desconocida detectada',
                'no_camera': 'Cámara no disponible',
                'camera_error': 'Error de cámara ocurrido',
                'recognition_error': 'Error de reconocimiento ocurrido',
                'loading': 'Cargando...',
                'welcome': '¡Bienvenido!',
                'hello': '¡Hola!',
                'goodbye': '¡Adiós!',
                'good_morning': '¡Buenos días!',
                'good_afternoon': '¡Buenas tardes!',
                'good_evening': '¡Buenas noches!',
                'name': 'Nombre',
                'relationship': 'Relación',
                'language': 'Idioma',
                'confidence': 'Confianza',
                'last_seen': 'Visto por última vez',
                'audio_disabled': 'Audio deshabilitado',
                'processing': 'Procesando...',
                'system_ready': 'Sistema Memory Mirror Listo',
                'person_recognized': 'Persona reconocida: {name}',
                'default_greeting': '¡Hola {name}! ¡Qué bueno verte!',
                'setup_required': 'Por favor agregue fotos al directorio known_faces',
                'no_faces_detected': 'No se detectaron caras en la cámara'
            },
            'fr': {
                'ready_to_recognize': 'Prêt à reconnaître...',
                'unknown_person': 'Personne inconnue détectée',
                'no_camera': 'Caméra non disponible',
                'camera_error': 'Erreur de caméra survenue',
                'recognition_error': 'Erreur de reconnaissance survenue',
                'loading': 'Chargement...',
                'welcome': 'Bienvenue!',
                'hello': 'Bonjour!',
                'goodbye': 'Au revoir!',
                'good_morning': 'Bonjour!',
                'good_afternoon': 'Bon après-midi!',
                'good_evening': 'Bonsoir!',
                'name': 'Nom',
                'relationship': 'Relation',
                'language': 'Langue',
                'confidence': 'Confiance',
                'last_seen': 'Vu pour la dernière fois',
                'audio_disabled': 'Audio désactivé',
                'processing': 'Traitement...',
                'system_ready': 'Système Memory Mirror Prêt',
                'person_recognized': 'Personne reconnue: {name}',
                'default_greeting': 'Bonjour {name}! Ravi de vous voir!',
                'setup_required': 'Veuillez ajouter des photos au répertoire known_faces',
                'no_faces_detected': 'Aucun visage détecté dans la caméra'
            }
        }
        
        return messages
    
    def get_greeting_by_time(self, language: str = None) -> str:
        """Get appropriate greeting based on current time."""
        if not language:
            language = self.current_language
        
        try:
            from datetime import datetime
            
            current_hour = datetime.now().hour
            
            if 5 <= current_hour < 12:
                return self.translate_text('good_morning', language)
            elif 12 <= current_hour < 17:
                return self.translate_text('good_afternoon', language)
            elif 17 <= current_hour < 22:
                return self.translate_text('good_evening', language)
            else:
                return self.translate_text('hello', language)
                
        except Exception as e:
            logger.error(f"Error getting time-based greeting: {e}")
            return self.translate_text('hello', language)
    
    def format_person_greeting(self, person_name: str, language: str = None) -> str:
        """Format a personalized greeting for a person."""
        if not language:
            language = self.current_language
        
        try:
            greeting = self.get_greeting_by_time(language)
            return f"{greeting} {person_name}!"
            
        except Exception as e:
            logger.error(f"Error formatting person greeting: {e}")
            return f"Hello {person_name}!"

# Global language manager instance
language_manager = LanguageManager()
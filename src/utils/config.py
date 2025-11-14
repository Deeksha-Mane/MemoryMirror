"""Configuration utilities for Memory Mirror application."""

import json
import os
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """Manages application configuration from JSON files."""
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logging.info(f"Configuration loaded from {self.config_path}")
            else:
                logging.warning(f"Configuration file not found: {self.config_path}")
                self.config = self._get_default_config()
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration values."""
        return {
            "camera": {
                "device_index": 0,
                "resolution": [640, 480],
                "fps": 30
            },
            "recognition": {
                "model_name": "VGG-Face",
                "detector_backend": "opencv",
                "confidence_threshold": 0.6,
                "distance_metric": "cosine"
            },
            "ui": {
                "theme": "light",
                "update_interval_ms": 100,
                "display_confidence": False
            },
            "audio": {
                "tts_engine": "gtts",
                "volume": 0.8,
                "speech_rate": 1.0
            },
            "languages": {
                "supported": ["en", "hi", "es", "fr"],
                "default": "en"
            }
        }

# Global configuration instance
config = ConfigManager()
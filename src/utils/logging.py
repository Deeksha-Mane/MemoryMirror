"""Logging setup for Memory Mirror application."""

import logging
import os
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """Set up logging configuration for the application."""
    
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Set up logging configuration
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
    # Set specific loggers to reduce noise
    logging.getLogger('tensorflow').setLevel(logging.ERROR)
    logging.getLogger('deepface').setLevel(logging.WARNING)
    logging.getLogger('opencv').setLevel(logging.WARNING)
    
    logging.info("Logging initialized")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)
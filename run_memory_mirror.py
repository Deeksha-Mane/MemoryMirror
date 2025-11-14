#!/usr/bin/env python3
"""
Memory Mirror Startup Script
Run this script to start the Memory Mirror application.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    try:
        import streamlit
        import cv2
        import deepface
        import gtts
        import pygame
        import numpy
        import PIL
        import tensorflow
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements with: pip install -r requirements.txt")
        return False

def check_data_structure():
    """Check if required data directories exist."""
    required_dirs = [
        "known_faces",
        "data",
        "config",
        "src"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    # Check for caregiver data
    if not Path("data/caregiver_data.json").exists():
        print("❌ Missing caregiver_data.json file")
        return False
    
    print("✅ Data structure is complete")
    return True

def main():
    """Main startup function."""
    print("🪞 Memory Mirror - Starting up...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check data structure
    if not check_data_structure():
        print("\nTo set up the data structure, make sure you have:")
        print("- known_faces/ directory with subdirectories for each person")
        print("- data/caregiver_data.json with person metadata")
        print("- config/settings.json with application settings")
        sys.exit(1)
    
    print("\n🚀 Starting Memory Mirror application...")
    print("The application will open in your default web browser.")
    print("Press Ctrl+C to stop the application.")
    print("=" * 50)
    
    try:
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Memory Mirror stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
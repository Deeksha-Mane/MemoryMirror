#!/usr/bin/env python3
"""
Memory Mirror - Dependency Installation Script
Handles Python 3.12 compatibility issues
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check Python version and warn about compatibility."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 12:
        print("⚠️  Python 3.12+ detected. Some packages may have compatibility issues.")
        print("   We'll install compatible versions step by step.")
        return "3.12+"
    elif version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible.")
        return "compatible"
    else:
        print("❌ Python 3.8+ is required.")
        return "incompatible"

def install_minimal_requirements():
    """Install minimal requirements that work with Python 3.12."""
    print("\n📦 Installing minimal requirements...")
    
    packages = [
        "streamlit>=1.28.0",
        "opencv-python>=4.8.0", 
        "numpy>=1.24.0",
        "Pillow>=10.0.0"
    ]
    
    success = True
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            success = False
    
    return success

def install_optional_requirements():
    """Install optional requirements with error handling."""
    print("\n🎵 Installing optional audio requirements...")
    
    optional_packages = [
        ("gtts>=2.4.0", "Google Text-to-Speech"),
        ("pygame>=2.5.0", "Audio playback")
    ]
    
    for package, description in optional_packages:
        run_command(f"pip install {package}", f"Installing {description}")

def install_ai_requirements():
    """Install AI/ML requirements with Python 3.12 handling."""
    print("\n🤖 Installing AI/ML requirements...")
    
    python_version = sys.version_info
    
    if python_version.major == 3 and python_version.minor >= 12:
        print("⚠️  Python 3.12+ detected. Installing compatible versions...")
        
        # Try newer versions that support Python 3.12
        ai_packages = [
            ("tensorflow>=2.15.0", "TensorFlow (newer version for Python 3.12)"),
            ("deepface>=0.0.80", "DeepFace (newer version)")
        ]
    else:
        # Use original versions for older Python
        ai_packages = [
            ("tensorflow==2.13.0", "TensorFlow"),
            ("deepface==0.0.79", "DeepFace")
        ]
    
    for package, description in ai_packages:
        success = run_command(f"pip install {package}", f"Installing {description}")
        if not success:
            print(f"   ⚠️  {description} installation failed. The app will work without face recognition.")

def test_installation():
    """Test if key packages can be imported."""
    print("\n🧪 Testing installation...")
    
    test_packages = [
        ("streamlit", "Streamlit web framework"),
        ("cv2", "OpenCV computer vision"),
        ("numpy", "NumPy numerical computing"),
        ("PIL", "Pillow image processing")
    ]
    
    optional_packages = [
        ("gtts", "Google Text-to-Speech"),
        ("pygame", "Pygame audio"),
        ("tensorflow", "TensorFlow"),
        ("deepface", "DeepFace")
    ]
    
    success_count = 0
    total_required = len(test_packages)
    
    print("Required packages:")
    for package, description in test_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} - {description}")
            success_count += 1
        except ImportError:
            print(f"   ❌ {package} - {description}")
    
    print("\nOptional packages:")
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} - {description}")
        except ImportError:
            print(f"   ⚠️  {package} - {description} (optional)")
    
    return success_count == total_required

def main():
    """Main installation process."""
    print("🪞 Memory Mirror - Dependency Installation")
    print("=" * 50)
    
    # Check Python version
    python_compat = check_python_version()
    if python_compat == "incompatible":
        print("❌ Please upgrade to Python 3.8 or higher.")
        return 1
    
    # Upgrade pip first
    print("\n🔧 Upgrading pip...")
    run_command("python -m pip install --upgrade pip", "Upgrading pip")
    
    # Install minimal requirements
    if not install_minimal_requirements():
        print("❌ Failed to install minimal requirements.")
        return 1
    
    # Install optional requirements
    install_optional_requirements()
    
    # Install AI requirements
    install_ai_requirements()
    
    # Test installation
    if test_installation():
        print("\n✅ Installation completed successfully!")
        print("\nNext steps:")
        print("1. Add photos to known_faces/ directories")
        print("2. Run: python test_components.py")
        print("3. Start app: streamlit run app_simple.py")
        return 0
    else:
        print("\n⚠️  Installation completed with some issues.")
        print("You can still run the basic version with: streamlit run app_simple.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
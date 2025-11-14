#!/usr/bin/env python3
"""
Quick installation script for Memory Mirror
Installs only essential packages to get the app running quickly
"""

import subprocess
import sys

def install_package(package):
    """Install a single package."""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("🚀 Quick Install for Memory Mirror")
    print("Installing essential packages only...")
    print("=" * 40)
    
    # Essential packages that usually work with Python 3.12
    essential_packages = [
        "streamlit",
        "opencv-python", 
        "numpy",
        "Pillow"
    ]
    
    success_count = 0
    for package in essential_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installed {success_count}/{len(essential_packages)} essential packages")
    
    if success_count >= 3:  # At least streamlit, opencv, numpy
        print("\n✅ Enough packages installed to run the basic app!")
        print("\nTo test:")
        print("  streamlit run app_simple.py")
        print("\nTo install more features:")
        print("  python install_dependencies.py")
    else:
        print("\n❌ Not enough packages installed. Try:")
        print("  python install_dependencies.py")

if __name__ == "__main__":
    main()
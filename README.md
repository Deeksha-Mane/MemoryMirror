# Memory Mirror - Face Recognition System

A real-time face recognition prototype built with Streamlit, OpenCV, and DeepFace for live demonstration.

## Features

- 🎥 Real-time face detection and recognition
- 🌍 Multilingual support (English, Hindi, Spanish, French)
- 🔊 Personalized voice messages with text-to-speech
- 💾 Local face database management
- 🎨 Professional Streamlit interface
- 🔒 Privacy-focused (all data stored locally)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   For Python 3.12+:
   ```bash
   pip install -r requirements-py312.txt
   pip install tensorflow deepface tf-keras
   ```

2. **Configure your data:**
   ```bash
   copy data\caregiver_data.example.json data\caregiver_data.json
   ```
   Edit `data/caregiver_data.json` with your person information.

3. **Add face images:**
   - Create folders in `known_faces/` for each person
   - Add 3-5 photos of each person (jpg/png format)

4. **Run the application:**
   ```bash
   python run_memory_mirror.py
   ```

📖 **For detailed setup instructions, see [SETUP.md](SETUP.md)**

## Privacy & Security

⚠️ **Important**: This application handles personal data (face images and information).

- All data is stored **locally** on your machine
- Face images are **NOT** included in this repository
- Personal data files are in `.gitignore` by default
- Use `data/caregiver_data.example.json` as a template
- Never commit actual face images or personal data to public repositories

## Quick Demo

To test the application without personal data:
1. Use the example configuration
2. Add sample images to `known_faces/` directories
3. Run the application and click "Start Camera"

## Directory Structure

```
memory-mirror/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── config/settings.json      # Application configuration
├── src/                      # Source code modules
├── known_faces/              # Face database
├── data/caregiver_data.json  # Person metadata
└── assets/                   # Static assets
```

## Configuration

Edit `config/settings.json` to customize:
- Camera settings (resolution, FPS)
- Recognition parameters (threshold, model)
- Audio settings (volume, TTS engine)
- Language preferences
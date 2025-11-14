# Memory Mirror - Face Recognition System

A real-time face recognition prototype built with Streamlit, OpenCV, and DeepFace for live demonstration.

## Features

- Real-time face detection and recognition
- Multilingual support (English, Hindi, Spanish, French)
- Personalized voice messages
- Local face database management
- Professional Streamlit interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add face images:
   - Create folders in `known_faces/` for each person
   - Add multiple photos of each person (jpg/png format)

3. Configure person data:
   - Edit `data/caregiver_data.json` with names, relationships, and messages

4. Run the application:
```bash
python run_memory_mirror.py
```

Or directly with Streamlit:
```bash
streamlit run app.py
```

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
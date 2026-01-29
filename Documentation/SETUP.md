# Memory Mirror Setup Guide

## Initial Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

For Python 3.12+, use:
```bash
pip install -r requirements-py312.txt
pip install tensorflow deepface tf-keras
```

### 2. Configure Person Data

1. Copy the example configuration:
   ```bash
   copy data\caregiver_data.example.json data\caregiver_data.json
   ```
   (On Linux/Mac: `cp data/caregiver_data.example.json data/caregiver_data.json`)

2. Edit `data/caregiver_data.json` with your person information:
   - Update names, relationships, and voice messages
   - Add translations for different languages
   - Adjust settings as needed

### 3. Add Face Images

1. Create a directory for each person in `known_faces/`:
   ```
   known_faces/
   ├── person1/
   │   ├── photo1.jpg
   │   ├── photo2.jpg
   │   └── photo3.jpg
   └── person2/
       ├── photo1.jpg
       └── photo2.jpg
   ```

2. Add multiple photos of each person (3-5 recommended)
3. Use clear, front-facing photos with good lighting
4. Supported formats: JPG, JPEG, PNG, BMP

### 4. Run the Application

```bash
python run_memory_mirror.py
```

Or directly with Streamlit:
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Configuration

Edit `config/settings.json` to customize:
- Camera settings (resolution, FPS, device index)
- Recognition parameters (threshold, model, distance metric)
- Audio settings (volume, TTS engine)
- Language preferences

## Supported Languages

- English (en)
- Hindi (hi)
- Spanish (es)
- French (fr)

## Troubleshooting

### Camera not working
- Check if your webcam is connected
- Try changing `device_index` in `config/settings.json`
- Ensure no other application is using the camera

### Face recognition not working
- Ensure DeepFace and TensorFlow are installed
- Add more photos of each person (3-5 recommended)
- Adjust `recognition_threshold` in settings

### Audio not playing
- Check if pygame is installed
- Verify audio output device is working
- Set `audio_enabled: true` in settings

## Privacy & Security

⚠️ **Important**: This application stores face images and personal data locally.

- Never commit `known_faces/` directory with actual photos to public repositories
- Keep `data/caregiver_data.json` private (it's in .gitignore)
- Use the example files as templates only
- Consider encrypting sensitive data if sharing the project

import os

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Piper TTS Configuration
PIPER_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
PIPER_VOICES = {
    "en_US/amy": {
        "name": "Amy",
        "language": "English (US)",
        "gender": "Female",
        "model_path": os.path.join(PIPER_MODELS_DIR, "en_US-amy-medium.onnx"),
    },
    "en_US/joe": {
        "name": "Joe",
        "language": "English (US)",
        "gender": "Male",
        "model_path": os.path.join(PIPER_MODELS_DIR, "en_US-joe-medium.onnx"),
    },
    "en_GB/semaine": {
        "name": "Semaine",
        "language": "English (UK)",
        "gender": "Female",
        "model_path": os.path.join(PIPER_MODELS_DIR, "en_GB-semaine-medium.onnx"),
    },
    "en_US/alan": {
        "name": "Alan",
        "language": "English (UK)",
        "gender": "Male",
        "model_path": os.path.join(PIPER_MODELS_DIR, "en_GB-alan-medium.onnx"),
    }
}

# Audio Configuration
AUDIO_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
SAMPLE_RATE = 22050
AUDIO_FORMAT = "wav"

# Ensure required directories exist
os.makedirs(PIPER_MODELS_DIR, exist_ok=True)
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Text Processing Configuration
MAX_TEXT_LENGTH = 5000  # Maximum characters for text input
CHUNK_SIZE = 1000  # Size of text chunks for processing

# Summary Generation Configuration
SUMMARY_MAX_TOKENS = 1000
SUMMARY_TEMPERATURE = 0.7

# Script Generation Configuration
SCRIPT_MAX_TOKENS = 2000
SCRIPT_TEMPERATURE = 0.8

# UI Configuration
SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'png', 'jpg', 'jpeg']
SUPPORTED_LANGUAGES = ['en-US', 'en-GB']

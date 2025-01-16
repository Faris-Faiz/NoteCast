import os

# API Configuration
OPENAI_API_KEY = "OPENAI_API_KEY"
OPENROUTER_API_KEY = "OpenRouter_API_KEY"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "use api key"


if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it as an environment variable.")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set. Please set it as an environment variable.")

# Google Cloud TTS Configuration
# Set the path to your Google Cloud service account JSON key
GOOGLE_CLOUD_TTS_CREDENTIALS = "Google Cloud TTS credentials"

# Ensure the Google Cloud TTS credentials environment variable is set
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_TTS_CREDENTIALS

# Piper TTS Configuration (if you plan to use Piper later)
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
    "en_GB/george": {
        "name": "George",
        "language": "English (UK)",
        "gender": "Male",
        "model_path": os.path.join(PIPER_MODELS_DIR, "en_GB-george-medium.onnx"),
    },
    "en_US/beth": {
        "name": "Beth",
        "language": "English (US)",
        "gender": "Female",
        "model_path": os.path.join(PIPER_MODELS_DIR, "en_US-beth-medium.onnx"),
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


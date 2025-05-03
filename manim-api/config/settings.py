import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# AI Services settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# Manim settings
MANIM_BIN = os.getenv("MANIM_BIN", "manim")
MEDIA_DIR = os.getenv("MEDIA_DIR", "media")
FRAMES_DIR = os.path.join(MEDIA_DIR, "frames")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "videos")

# Ensure directories exist
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
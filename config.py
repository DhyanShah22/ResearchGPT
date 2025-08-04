# config.py

import os

# App Config
APP_TITLE = "ResearchGPT 🔬🤖"
APP_ICON = "📚"
DATA_DIR = "data"
VERSION = "2.0.0"
DEVELOPER = "Dhyan Shah"

# Google API Key
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# utils/tts.py

import re
from gtts import gTTS
import os
from config import DATA_DIR

def generate_and_get_audio_path(answer_text):
    clean_answer = re.sub(r"[*_`#>\-]+", "", answer_text)
    tts = gTTS(text=clean_answer, lang='en')
    audio_path = os.path.join(DATA_DIR, "response.mp3")
    tts.save(audio_path)
    return audio_path

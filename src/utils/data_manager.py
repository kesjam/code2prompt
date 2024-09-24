import json
import os

DATA_FILE = 'dictations.json'

def save_dictation(title, transcription, audio_file_path, dictation_type):
    dictations = load_dictations()
    dictations.append({
        'title': title,
        'transcription': transcription,
        'audio_file_path': audio_file_path,
        'type': dictation_type
    })
    with open(DATA_FILE, 'w') as f:
        json.dump(dictations, f)

def load_dictations():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

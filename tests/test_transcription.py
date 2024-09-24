import sys
from dotenv import load_dotenv
from src.api.whisper_api import transcribe_audio  # Ensure correct import

load_dotenv()  # Load environment variables

def test_transcription():
    audio_file = "output.wav"  # Ensure this file exists in the project root
    transcription = transcribe_audio(audio_file)
    if transcription:
        print("Transcription Text:")
        print(transcription)
    else:
        print("Transcription failed.")
        print(f"OpenAI library version: {openai.__version__}")

if __name__ == "__main__":
    test_transcription()
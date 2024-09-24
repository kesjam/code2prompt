import openai
import os
from dotenv import load_dotenv  # Ensure this import is present

load_dotenv()  # Load environment variables

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(audio_file_path):
    print(f"Transcribing audio file: {audio_file_path}")
    print(f"OpenAI library version: {openai.__version__}")  # Verify the version

    try:
        with open(audio_file_path, 'rb') as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        print("Transcription successful")
        print(response.text)
        return response.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

if __name__ == "__main__":
    transcribe_audio("test_recording.wav")  # Use the file we just recorded
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key from the environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(audio_file_path, language="en"):
    """
    Transcribe an audio file using OpenAI's Whisper API.

    Args:
        audio_file_path (str): Path to the audio file to be transcribed.
        language (str, optional): The language of the audio. Defaults to "en" (English).

    Returns:
        str: The transcribed text if successful, None otherwise.

    Raises:
        Exception: If there's an error during the API call or file handling.

    Related:
        - determine_dictation_type: Often called with the result of this function.
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            logging.debug(f"Transcribing audio file: {audio_file_path}")
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
            logging.info("Audio transcription completed successfully")
            return response.text
    except Exception as e:
        logging.error(f"Error transcribing audio: {str(e)}")
        raise

def determine_dictation_type(transcription):
    """
    Determine the type of dictation based on the transcribed text.

    Args:
        transcription (str): The transcribed text to analyze.

    Returns:
        str: The determined dictation type, or "General Dictation" if unable to determine.

    Raises:
        Exception: If there's an error during the API call or processing.

    Related:
        - transcribe_audio: Often provides the input for this function.
    """
    prompt = (
        "Determine the type of dictation for the following text:\n\n"
        f"{transcription}\n\n"
        "Possible types: General Dictation, Meeting Notes, Brainstorming Session, "
        "To-Do List, Email Draft, Journal Entry, Creative Writing, "
        "Technical Documentation, Academic Research Notes"
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that determines the type of dictation based on the content."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in determine_dictation_type: {e}")
        return "General Dictation"
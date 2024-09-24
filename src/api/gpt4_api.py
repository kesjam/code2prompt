import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key from the environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

gpt4_prompt = """
When given a transcription or written text, your task is to improve it by enhancing clarity, coherence, and readability while preserving the original message and intent. Please follow these guidelines:

Content Assessment:

Identify the Type of Communication:  
Determine if the text is a conversation, speech, dictation, email, text message, report, story, etc.

Understand the Context and Purpose:
Analyze the setting (e.g., casual chat, professional meeting, academic lecture).
Determine the relationship between participants (e.g., friends, colleagues, teacher-student).
Identify the main purpose (e.g., inform, request, entertain, persuade).

Tone and Style Adjustment:

Maintain Appropriate Tone:
For casual conversations, keep the language informal but clear.  
For professional or formal texts, use formal language and proper etiquette.
Adjust the tone to match emotional content if present (e.g., sympathetic, enthusiastic).

Preserve Voice and Personality:
Keep the unique speaking or writing style of the original speaker/writer where appropriate.

Structural Improvements:

Grammar and Spelling:
Correct grammatical errors, typos, and misspellings.

Punctuation and Capitalization: 
Ensure proper punctuation and capitalization to enhance readability.

Sentence Structure:
Break up run-on sentences.
Combine fragmented thoughts into complete sentences.

Paragraph Organization:
Group related ideas into paragraphs or sections.
Use headings or bullet points for clarity if suitable.

Content Clarity:

Eliminate Filler Words and Repetitions:
Remove unnecessary words like "um," "uh," "you know," "like."

Clarify Ambiguous Statements:
Rephrase unclear or confusing parts for better understanding.

Maintain Key Information:
Ensure all important details and nuances are preserved.

Formatting:

Use Appropriate Formatting Styles:
Emails: Include a greeting, body, and closing signature.
Text Messages: Keep messages concise; use line breaks for new thoughts.
Reports/Essays: Use headings, subheadings, and bullet points where applicable.

Highlight Important Points:
Bold or italicize critical information if necessary.
Use bullet points or numbering for lists or steps.

Style Guidelines:

Adapt Language for Audience:
Use terminology appropriate for the audience's knowledge level.
Explain technical terms if the audience may be unfamiliar.

Cultural Sensitivity:
Be mindful of cultural references and adjust if needed.
Avoid language that could be offensive or misinterpreted.

Content Enhancement:

Summarization:
If appropriate, provide a brief summary or abstract.

Add Transitions:
Use transitional phrases to improve flow between ideas.

Emphasize Calls to Action:
Clearly state any requests or required actions from the audience.

Special Considerations:

Multilingual Content:
If the text includes multiple languages, ensure correct usage and provide translations if necessary.

Emotional or Sensitive Topics:
Handle with care, maintaining respect and appropriate tone.

Creative or Literary Content:
Preserve stylistic elements like metaphors, analogies, and storytelling techniques.

Final Review:

Proofread:
Double-check for any remaining errors or inconsistencies.

Consistency Check:
Ensure consistency in tense, perspective, and style throughout the text.

Preserve Original Intent:
Confirm that the revised text accurately reflects the original message without altering its meaning.
"""

def clean_up_transcription(transcription, dictation_type):
    try:
        logging.debug(f"Cleaning up transcription for dictation type: {dictation_type}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that cleans up and formats dictations. Also suggest a title for the dictation."},
                {"role": "user", "content": f"Clean up and format the following transcription. Also suggest a short, descriptive title for it:\n\n{transcription}"}
            ]
        )
        logging.info("Transcription cleanup completed successfully")
        cleaned_text = response.choices[0].message.content
        
        # Split the cleaned text into title and content
        lines = cleaned_text.split('\n')
        suggested_title = lines[0].replace('Title:', '').strip()
        
        # Remove any formatting characters from the title
        suggested_title = re.sub(r'[*#_]', '', suggested_title).strip()
        
        cleaned_content = '\n'.join(lines[1:]).strip()
        
        return cleaned_content, suggested_title
    except Exception as e:
        logging.error(f"Error cleaning up transcription: {str(e)}")
        raise

def clean_transcription(transcription, dictation_type):
    """
    Clean up and format a transcription based on the provided dictation type.

    Args:
        transcription (str): The raw transcription text to be cleaned.
        dictation_type (str): The type of dictation (e.g., 'email', 'meeting notes').

    Returns:
        str: The cleaned and formatted transcription.

    Raises:
        Exception: If there's an error during the API call or processing.

    Related:
        - generate_subject_and_summary: Uses the same OpenAI client for processing.
    """
    prompt = (
        f"Clean up and format the following transcription as a {dictation_type} "
        f"based on the guidelines provided:\n\n{gpt4_prompt}\n\nTranscription:\n{transcription}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in clean_transcription: {e}")
        return transcription

def generate_subject_and_summary(transcription, dictation_type):
    """
    Generate a concise subject and summary for a given transcription.

    Args:
        transcription (str): The transcription text to summarize.
        dictation_type (str): The type of dictation (e.g., 'email', 'meeting notes').

    Returns:
        tuple: A tuple containing the subject (str) and summary (str).
               The subject is limited to 5 words and the summary to 50 characters.

    Raises:
        Exception: If there's an error during the API call or processing.

    Related:
        - clean_transcription: Uses the same OpenAI client for processing.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that generates concise subjects and summaries for dictations."
                },
                {
                    "role": "user",
                    "content": (
                        f"Given the following transcription and dictation type, "
                        f"generate a concise subject (max 5 words) and a brief "
                        f"give a summary (max 50 characters). Dictation type: {dictation_type}"
                        f"\n\nTranscription: {transcription}"
                    )
                }
            ]
        )
        result = response.choices[0].message.content.split('\n')
        subject = result[0].replace("Subject: ", "")
        summary = result[1].replace("Summary: ", "")[:50]  # Truncate summary to 50 characters
        return subject, summary
    except Exception as e:
        print(f"Error generating subject and summary: {e}")
        return "New Dictation", "No summary available"

def determine_dictation_type(transcription):
    prompt = (
        "Determine the most likely type of dictation for the following text. "
        "Choose from: \n"
        "- Casual Conversation\n"
        "- Formal Speech\n"
        "- Meeting Notes\n" 
        "- Brainstorming Session\n"
        "- To-Do List\n"
        "- Email Draft\n"
        "- Journal Entry\n"
        "- Creative Writing\n"
        "- Technical Documentation\n"
        "- Academic Research Notes\n"
        "- Text Message\n\n"  # Add "Text Message" as an option
        "Provide your answer in the following format:\n"
        "Dictation Type: [Selected Type]\n\n"
        f"Transcription: {transcription}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that determines the most likely type of dictation based on the content. "
                        "Consider the context, tone, and purpose of the text to make an accurate determination. "
                        "Pay close attention to formatting cues like greetings, sign-offs, and line breaks to distinguish between different types of communication."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip().replace("Dictation Type: ", "")
    except Exception as e:
        print(f"Error in determine_dictation_type: {e}")
        return "General Dictation"


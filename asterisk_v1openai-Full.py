#!/usr/bin/python3

import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydub import AudioSegment
import wave
import os
import io
import time
import logging
from asterisk.agi import AGI

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
SILENCE_THRESHOLD = -30  # Adjust this value based on your requirements
SILENCE_DURATION = 2  # Silence duration in seconds

# Project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Setup logging
log_file_path = os.path.join(PROJECT_DIR, 'openai_assistant.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='a')
logging.info("OpenAI Assistant script started")

def synthesize_text(text: str) -> str:
    """
    Synthesize speech from the provided text using OpenAI's API.

    Args:
        text (str): The text to be synthesized into speech.

    Returns:
        str: The filename of the synthesized audio in WAV format, or None if an error occurs.
    """
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="nova",  # Specify the voice if required
            input=text
        )

        audio_content = response.content

        # Convert to WAV using pydub to ensure correct format
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_content), format="mp3")
        filename = os.path.join(PROJECT_DIR, "response_audio.wav")
        audio_segment.export(filename, format="wav", parameters=["-ac", "1", "-ar", "8000"])

        if not os.path.exists(filename):
            logging.error(f"Error: {filename} was not created.")
            return None

        with open(filename, 'rb') as audio_file:
            audio_content = audio_file.read()

        logging.info(f"{filename} created successfully with format 16-bit PCM at 8kHz")
        return filename
    except Exception as e:
        logging.error(f"Error in synthesize_text: {e}")
        return None

def transcribe_audio(filename: str) -> str:
    """
    Transcribe the provided audio file to text using OpenAI's API.

    Args:
        filename (str): The path to the audio file to be transcribed.

    Returns:
        str: The transcribed text, or an empty string if an error occurs.
    """
    try:
        logging.info(f"Transcribing audio file: {filename}")
        with open(filename, 'rb') as audio_file:
            response = openai.audio.transcriptions.create(model="whisper-1", file=audio_file)
        logging.info(f"Transcription result: {response.text}")
        return response.text
    except Exception as e:
        logging.error(f"Error in transcribe_audio: {e}")
        return ""

def get_openai_response(prompt: str, conversation_history: str) -> str:
    """
    Get a response from OpenAI's language model based on the provided prompt and conversation history.

    Args:
        prompt (str): The prompt text to send to the language model.
        conversation_history (str): The conversation history to provide context for the response.

    Returns:
        str: The response from the language model, or an empty string if an error occurs.
    """
    try:
        logging.info(f"Getting OpenAI response for prompt: {prompt}")
        response = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"{conversation_history}\nUser: {prompt}\nAI:",
            max_tokens=150
        )
        ai_response = response.choices[0].text.strip()
        logging.info(f"OpenAI response: {ai_response}")
        return ai_response
    except Exception as e:
        logging.error(f"Error in get_openai_response: {e}")
        return ""

def send_email(subject: str, body: str, to_email: str) -> None:
    """
    Send an email with the specified subject and body to the given email address.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        to_email (str): The recipient's email address.

    Returns:
        None
    """
    try:
        logging.info(f"Sending email to {to_email} with subject: {subject}")
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, to_email, text)
        server.quit()
        logging.info(f"Email sent to {to_email}")
    except Exception as e:
        logging.error(f"Error in send_email: {e}")

def process_call(agi: AGI) -> None:
    """
    Process an incoming call, interact with the caller, and handle the conversation.

    Args:
        agi (AGI): The Asterisk Gateway Interface object for interacting with the call.

    Returns:
        None
    """
    logging.info("Starting call processing")

    intro_text = "Hi, I'm Alix, TechPath's AI-powered assistant. During our call you will hear a beep, this beep indicates that I am listing for your response.... Can I start with your name and the company that you are calling from?"
    intro_audio = synthesize_text(intro_text)
    if intro_audio is None:
        logging.error("Error: Failed to synthesize introduction audio.")
        agi.hangup()
        return

    logging.info(f"Introduction audio file: {intro_audio}")
    agi.verbose(f"Playing introduction audio: {intro_audio}")

    try:
        agi.stream_file(intro_audio.replace('.wav', ''))
    except Exception as e:
        logging.error(f"Error playing introduction audio: {e}")
        agi.hangup()
        return

    logging.info("Introduction audio played successfully.")

    conversation_history = ""
    conversation_active = True
    while conversation_active:
        record_file = os.path.join(PROJECT_DIR, "call_audio")
        silence_threshold = SILENCE_THRESHOLD
        silence_duration = SILENCE_DURATION * 1000  # Convert seconds to milliseconds

        logging.info("Playing beep tone to indicate start of recording")
        agi.stream_file('beep')

        logging.info("Recording caller's input. Waiting for silence.")
        agi.verbose("Recording caller's input. Waiting for silence.")
        try:
            agi.record_file(record_file, format='wav', escape_digits='', timeout=10000, silence=f"{silence_threshold},{silence_duration}", beep=False)
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error recording caller's input: {e}")
            agi.hangup()
            return

        record_file += ".wav"  # Add the ".wav" extension for the file check
        logging.info(f"Checking for recorded file: {record_file}")  # Log the actual file path and name

        logging.info(f"Recording file path: {record_file}")
        logging.info(f"Recording file exists: {os.path.isfile(record_file)}")
        
        if os.path.exists(record_file):
            logging.info(f"Recording file exists: {record_file}")
            logging.info("Transcribing caller's input")
            transcription_response = transcribe_audio(record_file)

            if transcription_response:
                transcript = transcription_response
                logging.info(f"Transcript: {transcript}")

                conversation_history += f"User: {transcript}\n"

                if "goodbye" in transcript.lower():
                    logging.info("Caller said goodbye. Ending conversation.")
                    conversation_active = False
                    break

                logging.info("Submitting transcript to OpenAI for response")
                openai_response = get_openai_response(transcript, conversation_history)
                conversation_history += f"AI: {openai_response}\n"

                logging.info("Synthesizing OpenAI response")
                response_audio = synthesize_text(openai_response)

                if response_audio:
                    logging.info(f"Playing OpenAI response: {response_audio}")
                    agi.stream_file(response_audio.replace('.wav', ''))
                else:
                    logging.error("Error: Failed to synthesize response audio.")
            else:
                logging.error("Error: Transcription failed.")
        else:
            logging.error("Error: Recording file not found.")

    logging.info("Conversation ended. Sending conversation summary via email.")
    email_body = f"Conversation transcript:\n\n{conversation_history}"
    send_email("Conversation Notes", email_body, "cameron@techpath.com.au")

    goodbye_text = "Thank you for your time. We'll get back to you as soon as possible. Goodbye!"
    goodbye_audio = synthesize_text(goodbye_text)
    if goodbye_audio:
        logging.info(f"Playing goodbye message: {goodbye_audio}")
        agi.stream_file(goodbye_audio.replace('.wav', ''))

    logging.info("Call processing completed.")

def main() -> None:
    """
    Main function to start the OpenAI Assistant.

    Returns:
        None
    """
    logging.info("Starting OpenAI Assistant")
    agi = AGI()
    agi.verbose("AGI object created")
    try:
        agi.answer()
        agi.verbose("Call answered")
        logging.info("Call answered successfully")
    except Exception as e:
        logging.error(f"Error answering call: {e}")
        agi.hangup()
        return

    process_call(agi)
    agi.verbose("Call processing completed")
    logging.info("Call processing completed")
    agi.hangup()
    logging.info("OpenAI Assistant finished")

if __name__ == "__main__":
    main()

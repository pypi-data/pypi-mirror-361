import openai
import os
import sys
import requests
import logging

sys.path.append("./")

from credentials import get_whisper_credentials

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get GPT information
WHISPER_KEY, WHISPER_ENDPOINT, WHISPER_DEPLOYMENT_NAME = get_whisper_credentials()


class Whisper_Deployment:
    def __init__(
            self,
            whisper_key = WHISPER_KEY,
            whisper_endpoint = WHISPER_ENDPOINT,
            whisper_deployment_name = WHISPER_DEPLOYMENT_NAME,
            timeout = 5, 
            max_retries = 3
    ):
        self.whisper_key = whisper_key
        self.whisper_endpoint = whisper_endpoint
        self.whisper_deployment_name = whisper_deployment_name
        self.timeout = timeout
        self.max_retries = max_retries
    
    def transcribe_audio(self, audio_file_path, timeout_value=None, max_retries_value=None, language=None):
        timeout = timeout_value or self.timeout
        max_retries = max_retries_value or self.max_retries

        headers = {
            'api-key': self.whisper_key
        }
        params = {
            'language': language
        }

        # Read the audio file in binary mode
        try:
            with open(audio_file_path, 'rb') as audio_file:
                files = {
                    'file': (os.path.basename(audio_file.name), audio_file, 'audio/mpeg')
                }

                for attempt in range(max_retries):
                    try:
                        response = requests.post(
                            url=self.whisper_endpoint,
                            headers=headers,
                            params=params,
                            files=files,
                            timeout=timeout
                        )
                        if response.status_code == 200:
                            data = response.json()
                            # Ensure response structure is valid
                            if 'text' in data:
                                return data['text']
                            else:
                                raise ValueError("Invalid response format from Whisper.")
                        else:
                            # Log API error details
                            logging.error(f"Request failed with status {response.status_code}: {response.text}")
                            response.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        logging.warning(f"Request failed on attempt {attempt + 1}: {e}")
                        if attempt == max_retries - 1:
                            raise
                        else:
                            continue  # Retry for transient errors

        except FileNotFoundError:
            logging.error(f"Audio file not found: {audio_file_path}")
            raise RuntimeError(f"Audio file not found: {audio_file_path}")

        raise RuntimeError("Max retries exceeded for Whisper transcription.")
        

# Example usage
if __name__ == "__main__":
    whi = Whisper_Deployment()
    
    audio_file = r"C:\Users\Kunde\OneDrive - Enari\__Coding__\llm-toolbox\10.mp3"
    
    msg = whi.transcribe_audio(audio_file, max_retries_value=1, language='de')

    print(msg)
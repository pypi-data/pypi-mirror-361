import openai
import os
import sys
import requests
import logging

sys.path.append("./")

from credentials import get_gpt_credentials

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get GPT information
GPT_KEY, GPT_ENDPOINT, GPT_MODEL = get_gpt_credentials()


class GPT_Deployment:
    def __init__(
            self,
            gpt_key = GPT_KEY,
            gpt_endpoint = GPT_ENDPOINT,
            gpt_deployment_name = GPT_MODEL,
            timeout = 5, 
            max_retries = 3
    ):
        self.gpt_key = gpt_key
        self.gpt_endpoint = gpt_endpoint
        self.gpt_deployment_name = gpt_deployment_name
        self.timeout = timeout
        self.max_retries = max_retries

        # authorize with openai via pi key
        #openai.api_key = get_openai_api_key()
    
    def request_gpt(self, prompt, temp = 0.8, top_p = 0.2, timeout_value = None, max_retries_value = None):
        timeout = timeout_value or self.timeout 
        max_retries = max_retries_value or self.max_retries

        headers = {
            'Content_Type': 'application/json',
            'api-key': self.gpt_key
        }
        payload = {
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': temp,
            'top_p': top_p
        }
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url=self.gpt_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                if response.status_code == 200:
                    data = response.json()
                    # Ensure response structure is valid
                    if 'choices' in data and len(data['choices']) > 0:
                        return data['choices'][0]['message']['content']
                    else:
                        raise ValueError("Invalid response format from GPT.")
                else:
                    # Log API error details
                    logging.error(f"Request failed with status {response.status_code}: {response.text}")
                    response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                else:
                    continue  # Retry for transient errors

        raise RuntimeError("Max retries exceeded for GPT request.")

# Example usage
if __name__ == "__main__":
    gpt = GPT_Deployment()
    msg = gpt.request_gpt('Schreibe ein vierzeiliges Gedicht zu Dreamlight Valley.')
    print(msg)
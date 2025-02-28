import requests
import os
import logging
import json
from errors import ProviderError

class BaseProvider:
    def __init__(self, config):
        self.name = config['name']
        self.endpoint = config['endpoint']
        self.token = os.getenv(f"{self.name.upper()}_API_KEY", config['token'])
        self.cost_per_1k_tokens = config['cost_per_1k_tokens']
        self.priority = config['priority']
        self.model = config.get('model', 'default')
        self.temperature = config.get('temperature', 0.7)

    def call_model(self, prompt):
        raise NotImplementedError("Subclasses should implement this method.")

class TogetherProvider(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        logging.info(f"Initialized Together provider ({self.name}) with model: {self.model}")

    def call_model(self, prompt):
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": 1000
            }

            logging.info(f"Calling Together API ({self.name}) with model {self.model}")
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code != 200:
                error_msg = f"Together API error for {self.name}: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise ProviderError(error_msg)

            try:
                response_data = response.json()
                logging.debug(f"Together API response: {response_data}")
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON response from Together ({self.name}): {str(e)}"
                logging.error(error_msg)
                raise ProviderError(error_msg)

            # Together API response structure check
            if not response_data.get('output') or not response_data['output'].get('choices'):
                error_msg = f"Empty or invalid response from Together API ({self.name}): {response_data}"
                logging.error(error_msg)
                raise ProviderError(error_msg)

            choices = response_data['output']['choices']
            if not choices or not isinstance(choices, list) or len(choices) == 0:
                error_msg = f"No choices in Together API response ({self.name})"
                logging.error(error_msg)
                raise ProviderError(error_msg)

            try:
                generated_text = choices[0]['text']
                logging.info(f"Successfully generated response using Together {self.name} ({self.model})")
                return generated_text
            except (KeyError, IndexError) as e:
                error_msg = f"Unexpected response format from Together API ({self.name}): {str(e)}"
                logging.error(error_msg)
                raise ProviderError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to Together API ({self.name}): {str(e)}"
            logging.error(error_msg)
            raise ProviderError(error_msg)
        except Exception as e:
            error_msg = f"Error in Together provider ({self.name}): {str(e)}"
            logging.error(error_msg)
            raise ProviderError(error_msg)

class GroqProvider(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        logging.info(f"Initialized Groq provider ({self.name}) with model: {self.model}")

    def call_model(self, prompt):
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": 1000
            }

            logging.info(f"Calling Groq API ({self.name}) with model {self.model}")
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code != 200:
                error_msg = f"Groq API error for {self.name}: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise ProviderError(error_msg)

            try:
                response_data = response.json()
                logging.debug(f"Groq API response: {response_data}")
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON response from Groq ({self.name}): {str(e)}"
                logging.error(error_msg)
                raise ProviderError(error_msg)

            if not response_data.get('choices'):
                error_msg = f"Empty response from Groq API ({self.name}): {response_data}"
                logging.error(error_msg)
                raise ProviderError(error_msg)

            choices = response_data['choices']
            if not choices or not isinstance(choices, list) or len(choices) == 0:
                error_msg = f"No choices in Groq API response ({self.name})"
                logging.error(error_msg)
                raise ProviderError(error_msg)

            try:
                generated_text = choices[0]['message']['content']
                logging.info(f"Successfully generated response using Groq {self.name} ({self.model})")
                return generated_text
            except (KeyError, IndexError) as e:
                error_msg = f"Unexpected response format from Groq API ({self.name}): {str(e)}"
                logging.error(error_msg)
                raise ProviderError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to Groq API ({self.name}): {str(e)}"
            logging.error(error_msg)
            raise ProviderError(error_msg)
        except Exception as e:
            error_msg = f"Error in Groq provider ({self.name}): {str(e)}"
            logging.error(error_msg)
            raise ProviderError(error_msg)
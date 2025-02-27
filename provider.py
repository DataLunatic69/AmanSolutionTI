import requests
import time
import logging
from errors import ProviderError

class BaseProvider:
    def __init__(self, config):
        self.name = config['name']
        self.endpoint = config['endpoint']
        self.token = config['token']
        self.cost_per_1k_tokens = config['cost_per_1k_tokens']
        self.priority = config['priority']

    def call_model(self, prompt):
        raise NotImplementedError("Subclasses should implement this method.")


class OllamaProvider(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def call_model(self, prompt):
        response = requests.post(self.endpoint, json={"prompt": prompt}, headers=self.headers)
        if response.status_code != 200:
            raise ProviderError("Ollama request failed.")
        return response.json()['response']


class GroqProvider(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def call_model(self, prompt):
        response = requests.post(self.endpoint, json={"prompt": prompt}, headers=self.headers)
        if response.status_code != 200:
            raise ProviderError("Groq request failed.")
        return response.json()['response']

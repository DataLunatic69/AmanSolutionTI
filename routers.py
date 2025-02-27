import time
import random
import logging
from provider import OllamaProvider, GroqProvider
from errors import ProviderError

class ModelRouter:
    def __init__(self, config_file="config.yaml"):
        self.config = self.load_config(config_file)
        self.providers = self.initialize_providers()

    def load_config(self, config_file):
        import yaml
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        return config['providers']

    def initialize_providers(self):
        providers = []
        for provider in self.config:
            if provider['name'] == 'ollama':
                providers.append(OllamaProvider(provider))
            elif provider['name'] == 'groq':
                providers.append(GroqProvider(provider))
        # Sort by priority
        return sorted(providers, key=lambda x: x.priority)

    def invoke(self, prompt):
        for provider in self.providers:
            try:
                return provider.call_model(prompt)
            except ProviderError as e:
                logging.error(f"Error invoking provider {provider.name}: {e}")
                continue 
        raise ProviderError("All providers failed.")


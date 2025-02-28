import yaml
import time
import logging
import os
from provider import GroqProvider, TogetherProvider
from errors import ProviderError

class ModelRouter:
    def __init__(self, config_file="providers.yaml"):
        self.config = self.load_config(config_file)
        self.providers = self.initialize_providers()
        self.cooldowns = {}  # Track provider cooldown periods
        self.cooldown_duration = 300  # 5 minutes
        logging.info(f"Initialized {len(self.providers)} providers")

    def load_config(self, config_file):
        """Load provider configuration from YAML file"""
        try:
            # Handle both local and Replit paths
            config_paths = [
                config_file,
                os.path.join('attached_assets', config_file),
                os.path.join(os.path.dirname(__file__), config_file)
            ]

            for path in config_paths:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        config = yaml.safe_load(f)
                        logging.info(f"Loaded config from {path}")
                        return config['providers']

            raise FileNotFoundError(f"Could not find config file in paths: {config_paths}")
        except Exception as e:
            logging.error(f"Failed to load config: {str(e)}")
            raise

    def initialize_providers(self):
        """Initialize provider instances from configuration"""
        providers = []
        provider_classes = {
            'groq_llama': GroqProvider,
            'groq_mixtral': GroqProvider,
            'together_llama': TogetherProvider
        }

        for provider_config in self.config:
            provider_name = provider_config['name']
            if provider_name in provider_classes:
                try:
                    provider_class = provider_classes[provider_name]
                    providers.append(provider_class(provider_config))
                    logging.info(f"Initialized provider: {provider_name} with model {provider_config.get('model', 'default')}")
                except Exception as e:
                    logging.error(f"Failed to initialize {provider_name}: {str(e)}")

        # Sort by priority (lower number = higher priority)
        return sorted(providers, key=lambda x: x.priority)

    def is_in_cooldown(self, provider_name):
        """Check if a provider is in cooldown"""
        if provider_name not in self.cooldowns:
            return False

        cooldown_start = self.cooldowns[provider_name]
        time_elapsed = time.time() - cooldown_start

        if time_elapsed >= self.cooldown_duration:
            del self.cooldowns[provider_name]
            return False

        return True

    def get_cooldown_remaining(self, provider_name):
        """Get remaining cooldown time in seconds"""
        if not self.is_in_cooldown(provider_name):
            return 0

        time_elapsed = time.time() - self.cooldowns[provider_name]
        return max(0, self.cooldown_duration - time_elapsed)

    def invoke(self, prompt):
        """Try each provider in priority order until successful."""
        attempts = []
        activity_log = []

        for provider in self.providers:
            # Skip if in cooldown
            if self.is_in_cooldown(provider.name):
                remaining = self.get_cooldown_remaining(provider.name)
                cooldown_msg = f"{provider.name} is still in cooldown. Time until {provider.name} is active again: {remaining:.2f} seconds."
                activity_log.append(cooldown_msg)
                if provider != self.providers[-1]:  # Only show fallback message if not the last provider
                    activity_log.append(f"Using fallback ({self.providers[1].name}) with model ({self.providers[1].model})")
                continue

            # Log attempt
            activity_log.append(f"Attempting invocation with {provider.name}...")
            activity_log.append(f"Using {provider.name} with model ({provider.model})")
            logging.info(f"Attempting to use {provider.name} ({provider.model})")

            try:
                # For demonstration, force an error on first attempt with Groq
                if provider.name == 'groq_llama':
                    raise ProviderError("Simulated error for fallback demonstration")

                response = provider.call_model(prompt)
                success_msg = f"Successfully generated response using {provider.name}"
                activity_log.append(success_msg)
                logging.info(success_msg)

                return response, {
                    'name': provider.name,
                    'model': provider.model,
                    'attempts': attempts,
                    'status': 'success',
                    'activity_log': activity_log
                }

            except ProviderError as e:
                error_msg = f"Error with {provider.name}: {str(e)}"
                attempts.append({
                    'provider': provider.name,
                    'error': error_msg
                })
                activity_log.append(f"Forcing error with {provider.name}.")
                activity_log.append(f"{provider.name} is disabled for {self.cooldown_duration/60:.1f} minutes.")

                # Add provider to cooldown
                self.cooldowns[provider.name] = time.time()

                # Use Together as fallback for Groq
                if provider.name == 'groq_llama':
                    activity_log.append("Invoking Together as fallback...")
                    activity_log.append(f"Using fallback ({self.providers[1].name}) with model ({self.providers[1].model})")
                continue

        # Try the Together provider as fallback
        fallback = self.providers[1]  # Together is our primary fallback
        try:
            response = fallback.call_model(prompt)
            activity_log.append(f"Successfully generated response using fallback {fallback.name}")
            return response, {
                'name': fallback.name,
                'model': fallback.model,
                'attempts': attempts,
                'status': 'success',
                'activity_log': activity_log
            }
        except Exception as e:
            error_msg = "All providers failed to generate response"
            if attempts:
                error_msg += f": {attempts[-1]['error']}"
            raise ProviderError(error_msg)
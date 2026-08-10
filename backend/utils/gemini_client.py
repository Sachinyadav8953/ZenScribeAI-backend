import os
import logging
from google import genai
from config import settings

logger = logging.getLogger(__name__)

class ModelsProxy:
    def __init__(self, wrapper):
        self.wrapper = wrapper

    def __getattr__(self, name):
        # Dynamically forward methods of client.models
        target_attr = getattr(self.wrapper.get_active_client().models, name)
        if callable(target_attr):
            def wrapped_method(*args, **kwargs):
                return self.wrapper.execute_with_rotation(target_attr, *args, **kwargs)
            return wrapped_method
        return target_attr

class GeminiClientWrapper:
    def __init__(self):
        self.api_keys = []
        self.clients = []
        self.current_index = 0
        self.load_keys()

    def load_keys(self):
        # 1. Check GEMINI_API_KEYS env var, then GEMINI_API_KEY, then settings
        keys_str = os.environ.get("GEMINI_API_KEYS") or os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        
        if keys_str:
            # Split by comma and strip spaces
            self.api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        
        if not self.api_keys:
            logger.warning("No Gemini API keys found. Initialization might fail.")
            self.api_keys = [""]

        self.clients = []
        for key in self.api_keys:
            try:
                self.clients.append(genai.Client(api_key=key))
            except Exception as e:
                logger.error(f"Failed to initialize genai.Client with key prefix {key[:6]}...: {e}")

        self.current_index = 0
        logger.info(f"Loaded {len(self.clients)} Gemini API clients for rotation/failover.")

    def get_active_client(self):
        if not self.clients:
            raise ValueError("No Gemini clients initialized.")
        return self.clients[self.current_index]

    def rotate_key(self):
        if len(self.clients) <= 1:
            logger.warning("Only 1 client configured. Rotation skipped.")
            return
        self.current_index = (self.current_index + 1) % len(self.clients)
        logger.info(f"Rotated to Gemini API key index {self.current_index} (Prefix: {self.api_keys[self.current_index][:6]}...)")

    def execute_with_rotation(self, func, *args, **kwargs):
        attempts = len(self.clients)
        last_error = None

        for attempt in range(attempts):
            client = self.get_active_client()
            method_name = func.__name__
            parent_service = getattr(client, "models")
            bound_method = getattr(parent_service, method_name)

            try:
                return bound_method(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.error(
                    f"Gemini API request failed on key index {self.current_index} "
                    f"(Prefix: {self.api_keys[self.current_index][:6]}...): {e}"
                )
                self.rotate_key()

        # If all keys failed, raise the final exception
        if last_error is not None:
            raise last_error
        else:
            raise Exception("Gemini rotation execution failed with unknown error")

    @property
    def models(self):
        return ModelsProxy(self)

    def __getattr__(self, name):
        return getattr(self.get_active_client(), name)

# Global client singleton
client = GeminiClientWrapper()

def get_gemini_client() -> GeminiClientWrapper:
    return client
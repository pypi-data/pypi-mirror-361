import importlib
import sys
from typing import Any, Dict, Optional, Callable

class LLMProvider:
    """
    Abstract base class for all LLM providers.
    """
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.kwargs = kwargs

    def is_available(self) -> bool:
        """Return True if the provider and its dependencies are available."""
        raise NotImplementedError

    def ensure_ready(self) -> bool:
        """
        Ensure the provider is ready to use (dependencies installed, model downloaded, etc).
        Returns True if ready, False otherwise.
        """
        raise NotImplementedError

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM given a prompt."""
        raise NotImplementedError

    def info(self) -> str:
        """Return a string describing the provider and its configuration."""
        return f"Provider: {self.__class__.__name__}, Model: {self.model}"


class OpenAIProvider(LLMProvider):
    def is_available(self) -> bool:
        return importlib.util.find_spec("openai") is not None

    def ensure_ready(self) -> bool:
        if not self.is_available():
            print("[AuraTrace] The 'openai' package is not installed. Please install it to use OpenAI models.")
            return False
        if not self.api_key:
            print("[AuraTrace] No OpenAI API key provided. Set it via environment or pass to the provider.")
            return False
        return True

    def generate(self, prompt: str, **kwargs) -> str:
        import openai
        openai.api_key = self.api_key
        model = self.model or "gpt-3.5-turbo"
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content


class HuggingFaceProvider(LLMProvider):
    def is_available(self) -> bool:
        return importlib.util.find_spec("transformers") is not None

    def ensure_ready(self) -> bool:
        if not self.is_available():
            print("[AuraTrace] The 'transformers' package is not installed. Please install it to use Hugging Face models.")
            return False
        return True

    def generate(self, prompt: str, **kwargs) -> str:
        from transformers import pipeline
        model = self.model or "mistralai/Mistral-7B-Instruct-v0.2"
        pipe = pipeline("text-generation", model=model, **self.kwargs)
        result = pipe(prompt, max_new_tokens=256)
        return result[0]["generated_text"]


class CustomAPIProvider(LLMProvider):
    def is_available(self) -> bool:
        return True  # Assume always available (user must provide endpoint)

    def ensure_ready(self) -> bool:
        if not self.kwargs.get("endpoint"):
            print("[AuraTrace] No custom API endpoint provided for LLM.")
            return False
        return True

    def generate(self, prompt: str, **kwargs) -> str:
        import requests
        endpoint = self.kwargs["endpoint"]
        headers = self.kwargs.get("headers", {})
        data = {"prompt": prompt, **kwargs}
        response = requests.post(endpoint, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get("response", "")


class LocalModelProvider(LLMProvider):
    def is_available(self) -> bool:
        return importlib.util.find_spec("transformers") is not None

    def ensure_ready(self) -> bool:
        if not self.is_available():
            print("[AuraTrace] The 'transformers' package is not installed. Please install it to use local models.")
            return False
        if not self.model:
            print("[AuraTrace] No local model specified.")
            return False
        return True

    def generate(self, prompt: str, **kwargs) -> str:
        from transformers import pipeline
        pipe = pipeline("text-generation", model=self.model, **self.kwargs)
        result = pipe(prompt, max_new_tokens=256)
        return result[0]["generated_text"]


class UserSuppliedProvider(LLMProvider):
    def __init__(self, generate_fn: Callable[[str], str], **kwargs):
        super().__init__(**kwargs)
        self.generate_fn = generate_fn

    def is_available(self) -> bool:
        return callable(self.generate_fn)

    def ensure_ready(self) -> bool:
        return self.is_available()

    def generate(self, prompt: str, **kwargs) -> str:
        return self.generate_fn(prompt) 
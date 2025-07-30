import os

from .google import GoogleGenAIClient
from .openai import OpenAIChatClient
from .xai import xAIChatClient


def get_chat_client(
    provider: str,
    model: str,
):
    """
    Returns a chat client based on the provider and model.

    Args:
        provider (str): The name of the provider (e.g., 'xai', 'google').
        model (str): The name of the model to use.

    Returns:
        Chat client instance for the specified provider and model.
    """
    PROVIDER_KEYS = {
        "xai": "XAI_API_KEY",
        "google": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
    }

    provider = provider.strip().lower()
    api_key = os.getenv(PROVIDER_KEYS.get(provider, ""), None)

    if provider not in PROVIDER_KEYS:
        print(
            f"[Error] Unsupported provider '{provider}'. Supported providers: {', '.join(PROVIDER_KEYS.keys())}."
        )
        raise ValueError(f"Unsupported provider: {provider}")

    if api_key is None:
        print(
            f"[Error] API key for provider '{provider}' is not set. Please set the environment variable '{PROVIDER_KEYS[provider]}'."
        )
        raise ValueError(f"API key is not set for provider: {provider}")

    if provider == "google":
        return GoogleGenAIClient(api_key=api_key, model=model)
    if provider == "openai":
        return OpenAIChatClient(api_key=api_key, model=model)
    if provider == "xai":
        return xAIChatClient(api_key=api_key, model=model)

    raise ValueError(f"Unknown provider: {provider}")

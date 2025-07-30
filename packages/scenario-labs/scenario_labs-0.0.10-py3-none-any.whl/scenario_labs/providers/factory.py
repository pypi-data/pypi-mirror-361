import os
from .xai import xAIChatClient
from .google import GoogleGenAIClient
from .openai import OpenAIChatClient


def get_chat_client(
    provider: str,
    model: str,
    temperature: float = 0.7,
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
        "google_vertex": "GOOGLE_VERTEX_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "cerebras": "CEREBRAS_API_KEY",
        "groq": "GROQ_API_KEY",
        "vercel": "VERCEL_API_KEY",
    }

    provider = provider.strip().lower()
    api_key = os.getenv(PROVIDER_KEYS.get(provider, ""), None)

    if provider not in PROVIDER_KEYS:
        supported = ", ".join(PROVIDER_KEYS.keys())
        raise ValueError(
            f"[Error] Unsupported provider '{provider}'. Supported providers: {supported}."
        )

    if api_key is None:
        raise ValueError(
            f"[Error] API key for provider '{provider}' is not set. "
            f"Please set the environment variable '{PROVIDER_KEYS[provider]}'."
        )

    if provider == "google":
        return GoogleGenAIClient(api_key=api_key, model=model, temperature=temperature)
    if provider == "openai":
        return OpenAIChatClient(api_key=api_key, model=model, temperature=temperature)
    if provider == "xai":
        return xAIChatClient(api_key=api_key, model=model, temperature=temperature)

    raise ValueError(f"Unknown provider: {provider}")

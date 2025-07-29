from typing import Any, Dict

from google import genai
from google.genai.types import GenerateContentConfig

from scenario_labs.client.base import ChatClient


class GoogleGenAIClient(ChatClient):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.client = genai.Client(api_key=api_key)

        self.session = None
        self.model = model

    def initialize(self, system_prompt: str):
        self.session = self.client.chats.create(
            model=self.model,
            config=GenerateContentConfig(system_instruction=[system_prompt]),
        )

    def chat(self, message: str) -> Dict[str, Any]:
        if self.session is None:
            raise ValueError("Chat session is not initialized.")

        response = self.session.send_message(message)
        return response.text

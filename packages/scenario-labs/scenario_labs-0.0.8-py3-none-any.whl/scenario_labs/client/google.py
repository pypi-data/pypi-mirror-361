from google import genai
from google.genai.types import GenerateContentConfig

from scenario_labs.client.base import ChatClient


class GoogleGenAIClient(ChatClient):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.client = genai.Client(api_key=api_key)

        self.session = None
        self.model = model

    def initialize(self, system_prompt: str):
        """
        Initializes the chat model with a system prompt.

        Args:
            system_prompt (str): The system prompt to initialize the chat model with.
        """
        self.session = self.client.chats.create(
            model=self.model,
            config=GenerateContentConfig(system_instruction=[system_prompt]),
        )

    def chat(self, message: str) -> str:
        """
        Sends a message to the chat model and returns the response.

        Args:
            message (str): The message to send to the chat model.

        Returns:
            str: The response from the chat model.
        """
        if self.session is None:
            raise ValueError("Chat session is not initialized.")

        response = self.session.send_message(message)
        return response.text


# References
#  - https://ai.google.dev/gemini-api/docs/openai
# - https://github.com/googleapis/python-genai?tab=readme-ov-file#send-message-synchronous-non-streaming

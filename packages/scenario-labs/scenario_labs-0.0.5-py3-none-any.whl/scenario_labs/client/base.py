from abc import ABC, abstractmethod


class ChatClient(ABC):
    model: str
    client: str

    @abstractmethod
    def chat(self, message: str) -> str:
        """
        Sends a message to the chat model and returns the response.

        Args:
            message (str): The message to send to the chat model.

        Returns:
            str: The response from the chat model.
        """
        pass

    @abstractmethod
    def initialize(self, system_prompt: str):
        """
        Initializes the chat model with a system prompt.

        Args:
            system_prompt (str): The system prompt to initialize the chat model with.
        """
        pass


# TODO - How widely used is the OpenAI standard?
#        https://ai.google.dev/gemini-api/docs/openai
#      - Google chat API
#        https://github.com/googleapis/python-genai?tab=readme-ov-file#send-message-synchronous-non-streaming

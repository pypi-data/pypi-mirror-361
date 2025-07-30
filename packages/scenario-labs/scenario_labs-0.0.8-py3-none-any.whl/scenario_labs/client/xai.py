import xai_sdk

from scenario_labs.client.base import ChatClient


class xAIChatClient(ChatClient):
    def __init__(self, api_key: str, model: str = "grok-3"):
        self.client = xai_sdk.Client(api_key=api_key)
        self.session = None
        self.model = model

    def initialize(self, system_prompt: str):
        """
        Initializes the chat model with a system prompt.

        Args:
            system_prompt (str): The system prompt to initialize the chat model with.
        """
        self.session = self.client.chat.create(
            model=self.model,
            messages=[xai_sdk.chat.system(system_prompt)],
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

        self.session.append(xai_sdk.chat.user(message))
        response = self.session.sample()
        self.session.append(response)

        return response.content

import openai
from scenario_labs.providers.base import ChatClient


class OpenAIChatClient(ChatClient):
    def __init__(self, api_key: str, model: str = "gpt-4o", temperature: float = 0.7):
        openai.api_key = api_key

        self.model = model
        self.temperature = temperature

        self.session = None
        self.messages = []

    def initialize(self, system_prompt: str):
        """
        Initializes the chat model with a system prompt.

        Args:
            system_prompt (str): The system prompt to initialize the chat model with.
        """
        self.session = openai.OpenAI()
        self.messages = [{"role": "system", "content": system_prompt}]

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

        self.messages.append({"role": "user", "content": message})

        response = self.session.chat.completions.create(
            model=self.model, messages=self.messages, temperature=self.temperature
        )

        self.messages.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )

        return response.choices[0].message.content


# References
#  - https://github.com/openai/openai-python

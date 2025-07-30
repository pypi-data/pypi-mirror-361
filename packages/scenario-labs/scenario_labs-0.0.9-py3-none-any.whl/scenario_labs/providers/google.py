import openai
from scenario_labs.providers.base import ChatClient


class GoogleGenAIClient(ChatClient):
    def __init__(
        self, api_key: str, model: str = "gemini-1.5-flash", temperature: float = 0.7
    ):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        self.model = model
        self.temperature = temperature

        self.session = None
        self.messages = []

        # self.tools = tools or {}
        # self.tool_definitions = [
        #     {"type": "function", "function": schema}
        #     for _, schema in self.tools.values()
        # ]

    def initialize(self, system_prompt: str):
        """
        Initializes the chat model with a system prompt.

        Args:
            system_prompt (str): The system prompt to initialize the chat model with.
        """
        self.session = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

        self.messages.append({"role": "system", "content": system_prompt})

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
#  - https://ai.google.dev/gemini-api/docs/openai
#  - https://github.com/googleapis/python-genai?tab=readme-ov-file#send-message-synchronous-non-streaming
#  - https://platform.openai.com/docs/guides/text?api-mode=responses
#  - https://gist.github.com/duyixian1234/7272241b789d4091a2537a2f887b5dd6

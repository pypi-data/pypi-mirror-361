import openai

from scenario_labs.client.base import ChatClient


class OpenAIChatClient(ChatClient):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        openai.api_key = api_key
        self.model = model
        self.session = None
        self.chat_history = []

    def initialize(self, system_prompt: str):
        self.session = openai.OpenAI()
        self.chat_history = [{"role": "system", "content": system_prompt}]

    def chat(self, message: str) -> str:
        if self.session is None:
            raise ValueError("Chat session is not initialized.")

        self.chat_history.append({"role": "user", "content": message})

        response = self.session.chat.completions.create(
            model=self.model,
            messages=self.chat_history,
        )

        reply = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": reply})

        return reply


# References
#  - https://github.com/openai/openai-python

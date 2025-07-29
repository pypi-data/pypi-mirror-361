from typing import Any, Dict

import xai_sdk

from scenario_labs.client.base import ChatClient


class xAIChatClient(ChatClient):
    def __init__(self, api_key: str, model: str = "grok-3"):
        self.client = xai_sdk.Client(api_key=api_key)
        self.session = None
        self.model = model

    def initialize(self, system_prompt: str):
        self.session = self.client.chat.create(
            model=self.model,
            messages=[xai_sdk.chat.system(system_prompt)],
            # [{"role": "system", "content": initial_prompt}]  <=== ??
        )

    def chat(self, message: str) -> Dict[str, Any]:
        if self.session is None:
            raise ValueError("Chat session is not initialized.")

        # xai_sdk expects a list of strings or some structured payload
        self.session.append(xai_sdk.chat.user(message))
        response = self.session.sample()
        self.session.append(response)

        return response.content

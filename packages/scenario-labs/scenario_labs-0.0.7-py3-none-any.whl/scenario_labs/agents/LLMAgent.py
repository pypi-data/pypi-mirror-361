class LLMAgent:
    def __init__(
        self, agent_id: str, role: str, system_prompt: str, initial_prompt: str, session
    ):
        self.agent_id = agent_id
        self.role = role
        self.session = session
        self.initial_prompt = initial_prompt
        self.system_prompt = system_prompt

        self.chat_history = []

        self.session.initialize("\n".join([system_prompt, initial_prompt]))

    def to_log(self):
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "system_prompt": self.system_prompt,
            "initial_prompt": self.initial_prompt,
            "chat_history": self.chat_history,
        }

    def respond(self, message: str) -> str:
        """
        Generates a response based on the provided message.
        Args:
            message (str): The message to respond to.
        Returns:
            str: The agent's response.
        """
        # prompt = f"{self.agent_id} ({self.role}): {message}"
        response = self.session.chat(message)

        return response

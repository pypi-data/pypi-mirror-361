import re
from typing import Any, Dict, List, Optional
from itertools import cycle
from scenario_labs.logging.conversation_logger import ConversationLogger


class ConversationSimulation:
    def __init__(
        self,
        simulation_name: str,
        agents: Dict[str, Any],
        log_directory: Optional[str] = "logs",
        log_format: str = "markdown",
        log_level: str = "info",
        console_output: bool = True,
        max_turns: int = 3,
        max_depth: int = 1,
    ):
        self.simulation_name = simulation_name
        self.agents = agents
        self.max_turns = max_turns
        self.max_depth = max_depth
        self.chat_history = []

        self.logger = ConversationLogger(
            simulation_name=simulation_name,
            log_dir=log_directory,
            log_format=log_format,
            log_level=log_level,
            console_output=console_output,
        )

    def parse_agent_messages(self, text: str, from_id: str) -> List[Dict[str, str]]:
        messages = []
        for match in re.findall(ConversationLogger.MESSAGE_PATTERN, text):
            if ":" in match:
                to_id, msg = map(str.strip, match.split(":", 1))
                if to_id and msg:
                    messages.append(
                        {"from_id": from_id, "to_id": to_id, "message": msg}
                    )
        return messages

    def _handle_message_chain(
        self, message: Dict[str, str], turn: int, current_depth: int
    ):
        if current_depth >= self.max_depth:
            return

        to_agent = self.agents.get(message["to_id"])
        if not to_agent:
            return

        prompt = f"${{{message['from_id']}: {message['message']}}}$"
        response = to_agent.respond(prompt)

        entry = {
            "turn": turn,
            "from_id": message["from_id"],
            "to_id": message["to_id"],
            "message": message["message"],
            "response": response,
            "depth": current_depth,
        }
        self.logger.log_entry(entry, turn, self.chat_history)

        # Parse new messages from the reply and recurse
        new_messages = self.parse_agent_messages(response, message["to_id"])

        for new_msg in new_messages:
            self._handle_message_chain(new_msg, turn, current_depth + 1)

    def run(self):
        agent_cycle = cycle(self.agents.values())

        for turn in range(1, self.max_turns + 1):
            agent = next(agent_cycle)
            thinking_prompt = f"Agent {agent.agent_id} ({agent.role}) is thinking..."
            primary_response = agent.respond(thinking_prompt)

            entry = {
                "turn": turn,
                "from_id": agent.agent_id,
                "to_id": None,
                "message": primary_response,
                "depth": 0,
            }
            self.logger.log_entry(entry, turn, self.chat_history)

            messages = self.parse_agent_messages(primary_response, agent.agent_id)

            for message in messages:
                self._handle_message_chain(message, turn, current_depth=1)

        self.logger.save_log(self.chat_history, self.max_turns)
        return self

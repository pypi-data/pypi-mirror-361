import re
import json
from datetime import datetime
from itertools import cycle
from pathlib import Path
from typing import Dict, List, Optional, Any


class ConversationSimulation:
    MESSAGE_PATTERN = r"<agent_reply>(.*?)</agent_reply>"

    def __init__(
        self,
        simulation_name: str,
        agents: Dict[str, Any],
        log_directory: Optional[str] = "logs",
        log_format: str = "markdown",
        log_level: str = "info",
        console_output: bool = True,
        max_turns: int = 12,
        max_depth: int = 2,
    ):
        """
        Initialize the simulation.

        Args:
            simulation_name (str): Name of the simulation.
            agents (dict): A dictionary mapping agent IDs to LLMAgent instances.
            log_directory (Optional[str]): Directory to store logs.
            log_format (str): Format for logs ('markdown' or 'json').
            log_level (str): Logging level ('debug', 'info', 'error').
            console_output (bool): Whether to print logs to console.
            max_turns (int): The number of turns to run the simulation.
        """
        self.simulation_name = simulation_name
        self.agents = agents
        self.max_turns = max_turns
        self.max_depth = max_depth
        self.log_dir = Path(log_directory) if log_directory else None
        self.log_format = log_format.lower()
        self.log_level = log_level.lower()
        self.console_output = console_output
        self.chat_history = []

    @staticmethod
    def format_message(text: str) -> str:
        """Format message by converting agent reply tags to Markdown bold."""
        return re.sub(ConversationSimulation.MESSAGE_PATTERN, r"**\1**", text)

    def parse_agent_messages(self, text: str, from_id: str) -> List[Dict[str, str]]:
        """
        Parses messages in the format <agent_reply>to_id: message</agent_reply>.

        Args:
            text (str): Agent response text.
            from_id (str): Agent sending the message.

        Returns:
            List of parsed messages with 'from_id', 'to_id', and 'message'.
        """
        messages = []
        for match in re.findall(self.MESSAGE_PATTERN, text):
            if ":" in match:
                to_id, msg = map(str.strip, match.split(":", 1))
                if to_id and msg:
                    messages.append(
                        {"from_id": from_id, "to_id": to_id, "message": msg}
                    )
        return messages

    def _log_entry_str(self, entry: Dict[str, Any]) -> str:
        """Returns a formatted Markdown string for a chat entry."""
        turn = entry.get("turn", "?")
        timestamp = entry.get("timestamp", "")
        from_id = entry.get("from_id", "")
        to_id = entry.get("to_id", "N/A")
        message = self.format_message(entry.get("message", ""))
        response = (
            self.format_message(entry.get("response", ""))
            if "response" in entry
            else ""
        )

        lines = [
            f"## Turn {turn} ({timestamp})",
            f"- **From:** {from_id}",
            f"- **To:** {to_id}",
            f"- **Message:** {message}",
        ]
        if response:
            lines.append(f"- **Response:** {response}")
        lines.append("\n---\n")
        return "\n".join(lines)

    def log_entry(self, entry: Dict[str, Any], turn: int) -> None:
        """
        Logs a single entry with timestamp.
        """
        timestamp = datetime.now().isoformat()
        entry["timestamp"] = timestamp
        self.chat_history.append(entry)

        if self.console_output and self.log_level in ("debug", "info"):
            print(self._format_log_entry(entry, turn))

    def _format_log_entry(self, entry: Dict[str, Any], turn: int) -> str:
        if self.log_format == "json":
            return json.dumps(entry, indent=2)
        else:  # markdown
            return self._log_entry_str(entry)

    def save_log(self) -> None:
        if not self.log_dir:
            return
        self.log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "md" if self.log_format == "markdown" else "json"
        filename = f"{self.simulation_name.lower().replace(' ', '_')}_log_{self.max_turns}_{timestamp}.{ext}"
        log_file = self.log_dir / filename

        content = ""
        if self.log_format == "markdown":
            content = f"# {self.simulation_name} Log\n\n"
            for entry in self.chat_history:
                content += self._log_entry_str(entry) + "\n"
        else:
            content = json.dumps(self.chat_history, indent=2)

        with log_file.open("w", encoding="utf-8") as f:
            f.write(content)

        if self.console_output:
            print(f"\nLog saved to: {log_file.resolve()}")

    def run(self):
        """
        Runs the turn-based simulation between agents.
        """
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
            }
            self.log_entry(entry, turn)

            # Parse and dispatch inter-agent messages
            for msg in self.parse_agent_messages(
                primary_response, from_id=agent.agent_id
            ):
                to_agent = self.agents.get(msg["to_id"])
                if to_agent:
                    message_text = f"${{{msg['from_id']}: {msg['message']}}}$"
                    reply = to_agent.respond(message_text)
                    sub_entry = {
                        "turn": turn,
                        "from_id": msg["from_id"],
                        "to_id": msg["to_id"],
                        "message": msg["message"],
                        "response": reply,
                    }
                    self.log_entry(sub_entry, turn)

        self.save_log()
        return self

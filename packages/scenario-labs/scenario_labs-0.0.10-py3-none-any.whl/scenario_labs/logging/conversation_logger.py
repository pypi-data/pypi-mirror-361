import re
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime


class ConversationLogger:
    MESSAGE_PATTERN = r"<agent_reply>(.*?)</agent_reply>"

    def __init__(
        self,
        simulation_name: str,
        log_dir: Optional[str] = "logs",
        log_format: str = "markdown",
        log_level: str = "info",
        console_output: bool = True,
    ):
        self.simulation_name = simulation_name
        self.log_dir = Path(log_dir) if log_dir else None
        self.log_format = log_format.lower()
        self.log_level = log_level.lower()
        self.console_output = console_output

    @staticmethod
    def format_message(text: str) -> str:
        return re.sub(ConversationLogger.MESSAGE_PATTERN, r"**\1**", text)

    def _log_entry_str(self, entry: Dict[str, Any]) -> str:
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
        depth = entry.get("depth", 0)

        lines = [
            f"### Turn {turn} (Depth {depth}) - {timestamp}",
            f"- **From:** {from_id}",
            f"- **To:** {to_id}",
            f"- **Message:** {message}",
        ]
        if response:
            lines.append(f"- **Response:** {response}")
        lines.append(f"\n---\n")
        return "\n".join(lines)

    def _format_log_entry(self, entry: Dict[str, Any]) -> str:
        if self.log_format == "json":
            return json.dumps(entry, indent=2)
        return self._log_entry_str(entry)

    def log_entry(
        self, entry: Dict[str, Any], turn: int, chat_history: List[Dict[str, Any]]
    ) -> None:
        timestamp = datetime.now().isoformat()
        entry["timestamp"] = timestamp
        chat_history.append(entry)

        if self.console_output and self.log_level in ("debug", "info"):
            print(self._format_log_entry(entry))

    def save_log(self, chat_history: List[Dict[str, Any]], max_turns: int) -> None:
        if not self.log_dir:
            return
        self.log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "md" if self.log_format == "markdown" else "json"
        filename = f"{self.simulation_name.lower().replace(' ', '_')}_log_{max_turns}_{timestamp}.{ext}"
        log_file = self.log_dir / filename

        content = ""
        if self.log_format == "markdown":
            content = f"# {self.simulation_name} Log\n\n"
            for entry in chat_history:
                content += self._log_entry_str(entry) + "\n"
        else:
            content = json.dumps(chat_history, indent=2)

        with log_file.open("w", encoding="utf-8") as f:
            f.write(content)

        if self.console_output:
            print(f"\nLog saved to: {log_file.resolve()}")

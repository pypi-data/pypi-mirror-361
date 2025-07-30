import json
from pathlib import Path
from datetime import datetime


class OneShotLogger:
    def __init__(self, log_directory: str, file_name: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        file_name = file_name.lower().replace(" ", "_")
        file_name = file_name.replace(".md", "")
        file_name = f"{file_name}_{timestamp}.md"

        self.log_directory = Path(log_directory)
        self.log_file = self.log_directory / file_name
        self.json_file = self.log_directory / file_name.replace(".md", ".json")

    def log(self, evaluation_data: dict):
        """
        Writes the evaluation data to a Markdown file and a JSON file.

        Args:
            evaluation_data (dict): The data from the one-shot evaluation to log.
        """
        lines = []

        # Metadata header
        lines.append(
            f"# Simulation Report: {evaluation_data.get('simulation_name', 'N/A')}\n"
        )
        lines.append(f"**Model**: `{evaluation_data.get('model', 'N/A')}`\n")
        lines.append(f"**Provider**: `{evaluation_data.get('provider', 'N/A')}`\n")
        lines.append(
            f"**Log Directory**: `{evaluation_data.get('log_directory', 'N/A')}`\n"
        )

        # System Prompt section
        lines.append("## System Prompt\n")
        system_prompt = evaluation_data.get("system_prompt", "").strip()
        if system_prompt:
            lines.append("```text")
            lines.append(system_prompt)
            lines.append("```\n")

        # Evaluation Samples
        lines.append("## Evaluation\n")
        for i, exchange in enumerate(evaluation_data.get("responses", []), start=1):
            user_msg = exchange.get("user", "").strip()
            assistant_msg = exchange.get("assistant", "").strip()

            lines.append(f"### Example {i}\n")
            lines.append(f"**User:**\t{user_msg}\n")
            lines.append(f"**Assistant:**\t{assistant_msg}\n")
            lines.append(f"---\n")

        if not self.log_directory.exists():
            self.log_directory.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists() or not self.json_file.exists():
            self.log_file.touch()
            self.json_file.touch()

        # Write Markdown file
        self.log_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"[INFO] Markdown file written to: {self.log_file}")

        # Write JSON file
        self.json_file.write_text(
            json.dumps(evaluation_data, indent=4), encoding="utf-8"
        )
        print(f"[INFO] JSON file written to: {self.json_file}")

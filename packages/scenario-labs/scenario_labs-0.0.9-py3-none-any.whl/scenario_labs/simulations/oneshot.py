import scenario_labs
from typing import Any, Dict


class OneShotSimulation:
    """
    Class to handle one-shot simulations (evaluation).
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = False

        log_directory = config.get("log_directory", False)

        if log_directory:
            self.logger = scenario_labs.logging.oneshot_logger.OneShotLogger(
                log_directory=log_directory,
                file_name=config.get("name", "one_shot_simulation") + ".md",
            )

        self.evaluation_log = {
            "simulation_name": config.get("name", "one_shot_simulation"),
            "model": config.get("model", "grok-3").strip().lower(),
            "provider": config.get("provider", "xai").strip().lower(),
            "system_prompt": config.get("system_prompt", ""),
            "responses": [],
        }

    def run(self):
        """
        Run the one-shot simulation based on the provided configuration.
        """
        agent = self.config["agents"][0]
        agent_prompts = agent["prompts"]

        for prompt in agent_prompts:
            model = agent.get("model", self.evaluation_log["model"])
            provider = agent.get("provider", self.evaluation_log["provider"])

            if (
                model != self.evaluation_log["model"]
                or provider != self.evaluation_log["provider"]
            ):
                self.evaluation_log["model"] = model
                self.evaluation_log["provider"] = provider

            session = scenario_labs.providers.factory.get_chat_client(
                provider=provider,
                model=model,
            )
            session.initialize(self.evaluation_log["system_prompt"])

            response = session.chat(prompt)

            self.evaluation_log["responses"].append(
                {"user": prompt, "assistant": response}
            )

        if self.logger:
            self.logger.log(self.evaluation_log)

        print("[Info] One-shot simulation completed.")

        return self.evaluation_log

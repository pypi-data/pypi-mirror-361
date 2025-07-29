import argparse
from pathlib import Path
from typing import Any, Dict

import yaml


import scenario_labs


def run_simulation(simulation_config: Dict[str, Any]):
    """
    Runs the LLM-based Conversational Simulation using the provided configuration.

    Args:
        simulation_config (Dict[str, Any]): The configuration dictionary containing simulation parameters.
    """
    agents = {}
    simulation_name = simulation_config["name"]
    max_turns = simulation_config["max_turns"]
    log_directory = simulation_config["log_directory"]

    model = simulation_config.get("model", "grok-3").strip().lower()
    provider = simulation_config.get("provider", "xai").strip().lower()

    for agent in simulation_config.get("agents", []):
        if "id" not in agent or "role" not in agent:
            print("[Warning] Skipping agent with missing 'id' or 'role'.")
            continue

        model = agent.get("model", model)
        provider = agent.get("provider", provider)

        session = scenario_labs.client.factory.get_chat_client(
            provider=provider,
            model=model,
        )

        agents[agent["id"]] = scenario_labs.agents.LLMAgent.LLMAgent(
            agent_id=agent["id"],
            role=agent["role"],
            system_prompt=simulation_config.get("system_prompt", ""),
            initial_prompt=agent["initial_prompt"],
            session=session,
        )

        print(f"[Info] Agent created: {agent['id']} ({agent['role']})")

    if not agents:
        raise ValueError(
            "[Error] No valid agents found in the configuration. Please check the 'agents' section."
        )

    simulation = scenario_labs.simulations.conversation.ConversationSimulation(
        simulation_name, agents, log_directory=log_directory, max_turns=max_turns
    )
    return simulation.run()


def main():
    parser = argparse.ArgumentParser(
        description="Run the LLM-based Conversational Simulation."
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("starbound_config.yaml"),
        help="Path to the simulation configuration YAML file (default: starbound_config.yaml)",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    config_text = config_path.read_text(encoding="utf-8")
    config_data = yaml.safe_load(config_text)

    return run_simulation(config_data["simulation_config"])


if __name__ == "__main__":
    main()

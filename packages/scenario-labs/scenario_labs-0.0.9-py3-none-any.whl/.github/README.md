<p align="center">

[![CI][ci-badge]][ci-url]
[![Release][release-badge]][release-url]
[![PyPI Status Badge][pypi-badge]][pypi-url]

</p>

[ci-badge]: https://github.com/christopherwoodall/scenario-labs/actions/workflows/lint.yaml/badge.svg?branch=main
[ci-url]: https://github.com/christopherwoodall/scenario-labs/actions/workflows/lint.yml
[pypi-badge]: https://badge.fury.io/py/scenario-labs.svg
[pypi-url]: https://pypi.org/project/scenario-labs/
[release-badge]: https://github.com/christopherwoodall/scenario-labs/actions/workflows/release.yml/badge.svg
[release-url]: https://github.com/christopherwoodall/scenario-labs/actions/workflows/release.yml


# Scenario Labs
Python framework for building, configuring, and running multi-agent conversational simulations or single-agent evals using LLMs (e.g., OpenAI, Google, xAI). It supports:

* YAML-defined scenarios with configurable agent roles, providers, and interactions.
* Parallelized simulation execution.
* Rich logging and structured data for analysis and downstream tooling.

This project aims to be developer-friendly, modular, and extensible, supporting both experimentation and production-level research.


## Getting Started
[Set the enviromental variables](https://ai.google.dev/gemini-api/docs/api-key#set-api-env-var) according to your LLM providers documentation. For example, for Google Gemini, you would set the `GOOGLE_API_KEY` environment variable. For xAI, you would set the `XAI_API_KEY` environment variable.


```bash
git clone https://github.com/christopherwoodall/scenario-labs Labs.git
cd scenario-labs
pip install -e ".[developer]"

scenario-labs
```

You can also run simulations in parallel with the following command:

```bash
for i in {1..9}; do scenario-labs & done; wait
```


## Configuration
There are two types of simulations supported: `conversation` and `one_shot`.

**Conversation** simulations allow for multi-turn interactions where context is maintained across turns.

**One-shot** simulations are designed for a single round of interaction without ongoing context.

Simulation behavior is configured via YAML files (e.g., `starbound_config.yaml`). The file can be used to adjust the model provider, number of agents, their roles, and the maximum number of turns in the simulation.

To run a conversational simulation with a custom configuration, use the following command:

```bash
scenario-labs --config simulations/starbound_config.yaml
```

An example one-shot configuration example is provided in `simulations/one_shot_config.yaml`. You can run a one-shot simulation with the following command:

```bash
scenario-labs --config simulations/one_shot_config.yaml
```


## Examples
You can find past chat logs in the [simulations directory](https://github.com/christopherwoodall/scenario-labs/tree/main/simulations).

![](https://raw.githubusercontent.com/christopherwoodall/scenario-labs/refs/heads/main/.github/docs/agents-example.png)


## Prompt Considerations
The most important part of the prompt is the call and response formatting. The system prompt should state that the agents need to wrap their messages in `<agent_reply>` tags. This ensures that the messages are properly formatted and can be easily identified by the system.

The following is a good way of achieving this:

```
All messages must begin with your character's name followed by a colon. For example: 
"Lily Chen: I hope you're having a great day!"

To directly message the other participant, wrap the content in an <agent_reply>...</agent_reply> tag. 
Inside the tag, write the character name, a colon, then the message. For example: 
"<agent_reply>Lily Chen: Have you ever tried crypto investing?</agent_reply>"

The following agents are involved:
- "Lily Chen"
- "Michael"
```

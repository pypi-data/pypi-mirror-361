<p align="center">

[![CI][ci-badge]][ci-url]
[![🕊️ Release Workflow][release-badge]][release-url]
[![PyPI Status Badge][pypi-badge]][pypi-url]

</p>

[ci-badge]: https://github.com/christopherwoodall/scenario-labs/actions/workflows/lint.yaml/badge.svg?branch=main
[ci-url]: https://github.com/christopherwoodall/scenario-labs/actions/workflows/lint.yml
[pypi-badge]: https://badge.fury.io/py/scenario-labs.svg
[pypi-url]: https://pypi.org/project/scenario-labs/
[release-badge]: https://github.com/christopherwoodall/scenario-labs/actions/workflows/release.yml/badge.svg
[release-url]: https://github.com/christopherwoodall/scenario-labs/actions/workflows/release.yml


# Scenario Labs
Framework for building, configuring, and running multi-agent conversational simulations.


## Examples
You can find past chat logs in the [logs directory](https://github.com/christopherwoodall/scenario-labs/tree/main/logs).

![](https://raw.githubusercontent.com/christopherwoodall/scenario-labs/refs/heads/main/.github/docs/agents-example.png)


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
The simulation's behavior, including the participating agents and the Large Language Models (LLMs) they use, is configured via a YAML file (e.g., `starbound_config.yaml`). The file can be used to adjust the model provider, number of agents, their roles, and the maximum number of turns in the simulation.

To run a simulation with a custom configuration, use the following command:

```bash
scenario-labs --config configs/starbound_config.yaml
```


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

# Nexa Python SDK

A modern, Pythonic SDK for the Nexa API. Effortlessly integrate Nexa's advanced voice and agent automation into your applications.

[![PyPI version](https://img.shields.io/pypi/v/nexa-sdk.svg)](https://pypi.org/project/nexa-sdk/)
[![License](https://img.shields.io/pypi/l/nexa-sdk.svg)](LICENSE)

---

## Overview

The Nexa Python SDK provides a simple, intuitive interface for interacting with the Nexa API. It supports agent management, call automation, and more, using modern Python best practices.

---

## Installation

Install from PyPI:
```bash
pip install nexa-sdk
```

Or from source:
```bash
pip install .
```

---

## Authentication

Authenticate using your Nexa API key (JWT token). The SDK uses this token for both Bearer and cookie authentication. The API base URL is set internally; you do not need to configure it.

---

## Quick Start

```python
from nexa_ai import NexaClient

# Initialize the client with your API key (JWT token)
nexa_client = NexaClient("your_api_key")

# List agents
agents = nexa_client.agent.list_agents()
print(agents)

# Make a call (implement your own parameters as needed)
# call = nexa_client.call.create_call(data, org_id)
# print(call)
```

---

## Usage

### Agents

```python
# List all agents
agents = nexa_client.agent.list_agents()

# Get a specific agent (provide agent_id and org_id)
# agent = nexa_client.agent.get_agent(agent_id, org_id)

# Create a new agent
# agent = nexa_client.agent.create_agent(data, org_id)
```

### Calls

```python
# List all calls (provide org_id)
calls = nexa_client.call.list_calls(org_id="your_org_id")

# Get a specific call
# call = nexa_client.call.get_call(call_id)

# Create a new call
# call = nexa_client.call.create_call(data, org_id)
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. 
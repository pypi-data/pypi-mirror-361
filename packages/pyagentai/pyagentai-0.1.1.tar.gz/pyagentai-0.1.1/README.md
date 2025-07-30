# pyagentai

[![PyPI version](https://img.shields.io/pypi/v/pyagentai.svg)](https://pypi.org/project/pyagentai/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyagentai.svg)](https://pypi.org/project/pyagentai/)
[![License](https://img.shields.io/github/license/meepolabs/pyagentai.svg)](https://github.com/meepolabs/pyagentai/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/pyagentai/badge/?version=latest)](https://pyagentai.readthedocs.io/en/latest/?badge=latest)

A Python library for seamless integration with [agent.ai](https://agent.ai/) APIs.

## Overview

`pyagentai` is a Python package that provides a client for interacting with the agent.ai platform. It enables developers to:

-   Easily connect to the agent.ai API.
-   Discover and interact with agents available on the platform.
-   Integrate agent.ai services into their own Python applications.

## Installation

```bash
pip install pyagentai
```

Or with Poetry:

```bash
poetry add pyagentai
```

## Quick Example

Here's a quick example of how to use the client to find available agents:

```python
from pyagentai import AgentAIClient
import asyncio

async def main():
    # Initialize the client, optionally providing an API key.
    # The client can also be configured using environment variables.
    ag = AgentAIClient(api_key="your_agentai_api_key")

    try:
        # Find the first 10 available agents
        agents = await ag.find_agents(limit=10)
        for agent in agents:
            print(f"- {agent.name}")
    finally:
        # Close the client connection
        await ag.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

For detailed documentation, visit [pyagentai.readthedocs.io](https://pyagentai.readthedocs.io).

The documentation includes:
- Getting Started Guide
- API Reference
- Examples and Tutorials
- FAQ

## Contributing

We welcome contributions! Please check out our [contributing guidelines](CONTRIBUTING.md) for details on:
- Setting up your development environment
- Running tests
- Submitting pull requests

## License

This project is licensed under the [GNU General Public License v3.0 (GPLv3)](LICENSE).

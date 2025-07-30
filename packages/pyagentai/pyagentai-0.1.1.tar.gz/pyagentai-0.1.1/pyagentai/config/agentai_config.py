import os

import yaml
from pydantic import BaseModel, Field

from .agentai_endpoints import AgentAIEndpoints


class AgentAIConfig(BaseModel):
    """Configuration for the agent.ai client."""

    api_url: str = Field(
        default=os.getenv("AGENTAI_API_URL", "https://api-lr.agent.ai/v1"),
        description="Base URL for the agent.ai API",
    )
    api_key: str = Field(
        default=os.getenv("AGENTAI_API_KEY", "sk-agentai-api-key"),
        description="API key for authenticating with agent.ai",
    )
    web_url: str = Field(
        default=os.getenv("AGENTAI_WEB_URL", "https://api.agent.ai/api"),
        description="Web URL for the agent.ai web app",
    )
    timeout: float = Field(
        default=60.0, description="Timeout in seconds for API requests"
    )
    endpoints: AgentAIEndpoints = Field(
        default_factory=lambda: AgentAIEndpoints(),
        description="API endpoints configuration",
    )

    @classmethod
    def from_yaml(cls, path: str) -> "AgentAIConfig":
        """Load configuration from a YAML file."""
        with open(path, encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)

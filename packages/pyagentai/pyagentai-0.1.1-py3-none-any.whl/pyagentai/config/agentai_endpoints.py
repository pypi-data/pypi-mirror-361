"""Configuration for agent.ai API endpoints."""

from pydantic import BaseModel, Field

from pyagentai.types.url_endpoint import (
    Endpoint,
    EndpointParameter,
    ParameterType,
    RequestMethod,
    UrlType,
)


class AgentAIEndpoints(BaseModel):
    """Endpoints for agent.ai API."""

    find_agents: Endpoint = Field(
        default=Endpoint(
            url="/action/find_agents",
            url_type=UrlType.API,
            method=RequestMethod.POST,
            description=(
                "Search and discover agents based on various "
                "criteria including status, tags, and search terms."
            ),
            requires_auth=True,
            response_content_type="application/json",
            request_content_type="application/json",
            body_parameters=[
                EndpointParameter(
                    name="status",
                    param_type=ParameterType.STRING,
                    required=False,
                    description="Filter agents by their visibility status.",
                    allowed_values=["any", "public", "private"],
                    validate_parameter=True,
                ),
                EndpointParameter(
                    name="slug",
                    param_type=ParameterType.STRING,
                    required=False,
                    description="Filter agents by their human readable slug.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="query",
                    param_type=ParameterType.STRING,
                    required=False,
                    description=(
                        "Text to search for in agent names and descriptions."
                    ),
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="tag",
                    param_type=ParameterType.STRING,
                    required=False,
                    description="Filter agents by specific tag.",
                    validate_parameter=False,
                ),
                EndpointParameter(
                    name="intent",
                    param_type=ParameterType.STRING,
                    required=False,
                    description=(
                        "Natural language description of the task "
                        "you want the agent to perform. This helps "
                        "find agents that match your use case."
                    ),
                    validate_parameter=False,
                ),
            ],
        ),
    )

from pyagentai.client import AgentAIClient
from pyagentai.types.agent_info import AgentInfo


@AgentAIClient.register
async def find_agents(
    self: AgentAIClient,
    status: str | None = None,
    slug: str | None = None,
    query: str | None = None,
    tag: str | None = None,
    intent: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AgentInfo]:
    """Search and discover agents based on various criteria including status,
    tags, and search terms.

    Args:
        status: Filter agents by their visibility status.
        slug: Agent human readable slug.
        query: Text to search for in agent names and descriptions.
        tag: Filter agents by specific tag.
        intent: Natural language description of the task you want the agent
            to perform. This helps find agents that match your use case.
        limit: Maximum number of agents to return.
        offset: Offset for pagination.

    Returns:
        List of available agents with their summarized information.
    """
    endpoint = self.config.endpoints.find_agents
    data = {}

    if status is not None:
        status = status.strip().lower()
        data["status"] = status

    if slug is not None:
        data["slug"] = slug

    if query is not None:
        data["query"] = query

    if tag is not None:
        data["tag"] = tag

    if intent is not None:
        data["intent"] = intent

    response = await self._make_request(
        endpoint=endpoint,
        data=data,
    )
    response_data = response.json()

    # Extract agents from response
    agents_data: list[dict] = response_data.get("response", [])
    agents = [
        AgentInfo.model_validate(agent_data) for agent_data in agents_data
    ]

    # Apply pagination in memory
    start_idx = min(offset, len(agents))
    end_idx = min(start_idx + limit, len(agents))
    paginated_agents = agents[start_idx:end_idx]
    await self._logger.info(
        f"Returning {len(paginated_agents)} agents "
        f"(offset: {offset}, limit: {limit})"
    )

    return paginated_agents

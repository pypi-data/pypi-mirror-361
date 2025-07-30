from pydantic import BaseModel, Field


class FunctionProperty(BaseModel):
    """A property of a function parameter."""

    type: str = Field(description="The data type of the property.")  # noqa: A003
    description: str = Field(description="A description of the property.")
    enum: list[str] | None = Field(
        None, description="A list of allowed values for the property."
    )


class FunctionParameters(BaseModel):
    """Parameters for a function."""

    type: str = Field(  # noqa: A003
        description="The type of the parameters object, usually 'object'."
    )
    properties: dict[str, FunctionProperty] = Field(
        description="A dictionary of properties for the function."
    )
    required: list[str] = Field(
        description="A list of required property names."
    )
    additional_properties: bool = Field(
        alias="additionalProperties",
        description="Whether additional properties are allowed.",
    )


class FunctionInfo(BaseModel):
    """The function information for invoking an agent."""

    name: str = Field(description="The name of the function.")
    description: str = Field(description="A description of the function.")
    parameters: FunctionParameters = Field(
        description="The parameters for the function."
    )


class InvokeAgentInput(BaseModel):
    """The input specification for invoking the agent."""

    type: str = Field(description="The type of input, usually 'function'.")  # noqa: A003
    function: FunctionInfo = Field(
        description="The function information for invoking an agent."
    )


class AgentInfo(BaseModel):
    """Information about an agent."""

    agent_id: str = Field(description="The unique identifier for the agent.")
    agent_id_human: str | None = Field(
        default="", description="A human-readable identifier for the agent."
    )
    name: str = Field(default="", description="The name of the agent.")
    invoke_agent_input: InvokeAgentInput = Field(
        description="The input specification for invoking the agent."
    )
    description: str | None = Field(
        default="", description="A description of the agent."
    )
    tags: list[str | None] = Field(
        default=[], description="A list of tags associated with the agent."
    )
    price: int | None = Field(
        default=0, description="The price to use the agent."
    )
    approximate_time: int | None = Field(
        default=0,
        description="The approximate time in seconds for the agent to run.",
    )
    type: str | None = Field(  # noqa: A003
        default="", description="The type of the agent (e.g., studio)."
    )
    reviews_count: int | None = Field(
        default=0, description="The number of reviews for the agent."
    )
    reviews_score: float | None = Field(
        default=0.0, description="The average score of reviews for the agent."
    )

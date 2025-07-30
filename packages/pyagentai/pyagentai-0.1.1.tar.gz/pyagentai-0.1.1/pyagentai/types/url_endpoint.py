"""Types for URL endpoints."""
from enum import Enum

from pydantic import BaseModel, Field


class RequestMethod(str, Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class UrlType(str, Enum):
    """Types of URLs."""

    WEB = "web"
    API = "api"


class ParameterType(str, Enum):
    """Types of parameters."""

    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    FILE = "file"


class EndpointParameter(BaseModel):
    """Parameter for an endpoint."""

    name: str = Field(description="Name of the parameter")
    param_type: ParameterType = Field(description="Data type of the parameter")
    required: bool = Field(
        default=False, description="Whether the parameter is mandatory"
    )
    description: str = Field(
        default="", description="Description of the parameter"
    )
    allowed_values: list[str | int | bool | None] = Field(
        default=[], description="Allowed values for the parameter"
    )
    validate_parameter: bool = Field(
        default=True,
        description=(
            "Whether to validate the parameter against the allowed " "values"
        ),
    )


class Endpoint(BaseModel):
    """Metadata for an agent.ai endpoint."""

    url: str = Field(description="The endpoint URL path")
    url_type: UrlType = Field(
        description="Whether this endpoint is for the web or API"
    )
    method: RequestMethod = Field(description="HTTP method for this endpoint")
    description: str = Field(
        default="", description="Description of the endpoint"
    )
    query_parameters: list[EndpointParameter] = Field(
        default_factory=list, description="Query parameters for the endpoint"
    )
    body_parameters: list[EndpointParameter] = Field(
        default_factory=list, description="Body parameters for the endpoint"
    )
    request_content_type: str = Field(
        default="application/json", description="Content type for the request"
    )
    response_content_type: str = Field(
        default="application/json", description="Content type for the response"
    )
    requires_auth: bool = Field(
        default=True,
        description="Whether this endpoint requires authentication",
    )
    path_parameters: list[EndpointParameter] = Field(
        default_factory=list, description="Path parameters for the endpoint"
    )

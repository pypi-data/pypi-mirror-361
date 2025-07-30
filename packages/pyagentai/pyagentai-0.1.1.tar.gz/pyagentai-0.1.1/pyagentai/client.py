"""Client for interacting with agent.ai API."""

import asyncio
from typing import Any

import httpx
import structlog

from pyagentai.config.agentai_config import AgentAIConfig
from pyagentai.types.url_endpoint import (
    Endpoint,
    EndpointParameter,
    ParameterType,
    UrlType,
)
from pyagentai.utils.method_registrar_mixin import _MethodRegistrarMixin


class AgentAIClient(_MethodRegistrarMixin):
    """Client for the agent.ai API.

    This client handles authentication and communication with the agent.ai API.

    Attributes:
        config: The configuration for the client.
    """

    def __init__(
        self,
        api_key: str | None = None,
        config: AgentAIConfig | None = None,
    ) -> None:
        """Initialize the agent.ai API client.

        Args:
            api_key: The API key for authenticating with agent.ai.
                If provided, overrides the key in the config.
            config: The configuration for the client.
                If not provided, a default configuration is used.
        """
        self._logger = structlog.get_logger("pyagentai")
        if config is None:
            config = AgentAIConfig()
        self.config = config

        if api_key:
            self.config.api_key = api_key

        self._http_client: httpx.AsyncClient | None = None
        self._agent_cache: dict[str, dict[str, Any]] = {}
        self._event_loop = asyncio.get_event_loop()
        self._initialize_client()

    def _initialize_client(self) -> httpx.AsyncClient:
        """Initialize the HTTP client.

        Returns:
            The initialized HTTP client.
        """
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                headers={
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout,
                http2=True,
            )
            self._event_loop.create_task(
                self._logger.debug("HTTP client initialized")
            )
        return self._http_client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client is not None and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

        await self._logger.debug("HTTP client closed")

    async def _validate_parameter(
        self, param: EndpointParameter, value: Any
    ) -> Any:
        """
        Validate a parameter with the Endpoint config

        Args:
            param: The parameter to validate.
            value: The value to validate.

        Returns:
            The validated value.

        Raises:
            ValueError: If the value is invalid.

        """
        # allowed-value validation
        if param.validate_parameter and value not in param.allowed_values:
            raise ValueError(
                f"Invalid value for {param.name}: '{value}'. "
                f"Allowed: {param.allowed_values}"
            )

        # data type validation
        type_map = {
            ParameterType.STRING: str,
            ParameterType.INTEGER: int,
            ParameterType.BOOLEAN: bool,
            ParameterType.OBJECT: dict,
            ParameterType.ARRAY: list,
            ParameterType.FILE: str,  # Assuming file is a path string
        }
        expected_type = type_map.get(param.param_type)

        # isinstance(True, int) is True, so handle bool separately
        if param.param_type == ParameterType.INTEGER and isinstance(
            value, bool
        ):
            error_message = (
                f"Invalid type for '{param.name}'. "
                f"Expected integer, got boolean."
            )
            await self._logger.error(error_message)
            raise ValueError(error_message)

        if expected_type and not isinstance(value, expected_type):
            error_message = (
                f"Invalid type for '{param.name}'. "
                f"Expected {param.param_type.value}, "
                f"got {type(value).__name__}."
            )
            await self._logger.error(error_message)
            raise ValueError(error_message)

        return value

    async def _make_request(
        self, endpoint: Endpoint, data: dict[str, Any] | None = None
    ) -> httpx.Response:
        """Make a request to the agent.ai API.

        Args:
            endpoint: The API endpoint to call.
            data: Data to build the request body and query parameters.

        Returns:
            The httpx response object.

        Raises:
            ValueError: If the request fails.
        """
        if data is None:
            data = {}

        client = self._initialize_client()

        # Determine base URL based on endpoint type
        if endpoint.url_type == UrlType.WEB:
            base_url = self.config.web_url
        else:
            base_url = self.config.api_url

        url = f"{base_url}{endpoint.url}"
        query_params: dict[str, Any] = {}
        body_params: dict[str, Any] = {}

        # Parse query and body parameters from data
        for param in endpoint.query_parameters:
            value = data.get(param.name, None)
            if value is None:
                if not param.required:
                    continue
                raise ValueError(f"Parameter '{param.name}' is required.")

            value = await self._validate_parameter(param, value)
            query_params[param.name] = value

        for param in endpoint.body_parameters:
            value = data.get(param.name, None)
            if value is None:
                if not param.required:
                    continue
                raise ValueError(f"Parameter '{param.name}' is required.")

            value = await self._validate_parameter(param, value)
            body_params[param.name] = value

        # Parse headers from endpoint
        headers: dict[str, str] = {}
        headers["Content-Type"] = endpoint.request_content_type
        headers["Accept"] = endpoint.response_content_type

        if endpoint.requires_auth:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        try:
            await self._logger.info(
                f"Making {endpoint.method} request to {url}"
            )
            response = await client.request(
                method=endpoint.method.value,
                url=url,
                params=query_params,
                json=body_params,
                headers=headers,
            )
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP error {e.response.status_code}"
            try:
                error_json = e.response.json()
                error_detail = f"{error_detail}: {error_json}"
            except Exception as exc:  # noqa: W0718
                error_detail = f"Error parsing response: {str(exc)}"
            await self._logger.error(f"API request failed: {error_detail}")
            raise ValueError(f"API request failed: {error_detail}") from e

        except httpx.TimeoutException as e:
            await self._logger.error(f"API request timed out: {str(e)}")
            raise ValueError("API request timed out") from e

        except httpx.HTTPError as e:
            await self._logger.error(f"HTTP error: {str(e)}")
            raise ValueError(f"HTTP error: {str(e)}") from e

        except Exception as e:
            await self._logger.error(f"Unexpected error: {str(e)}")
            raise ValueError(f"Unexpected error: {str(e)}") from e


# This import will trigger the registration of decorated methods.
# It MUST be at the bottom of the file to avoid circular import errors.
from pyagentai import api_methods  # noqa: E402 F401

import inspect
import json
import logging
import os
from collections.abc import Callable
from contextlib import suppress
from contextvars import ContextVar
from functools import wraps
from typing import (
    Any,
    TypeVar,
    get_type_hints,
)

import httpx

from veris_ai.utils import convert_to_type

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Context variable to store session_id for each call
_session_id_context: ContextVar[str | None] = ContextVar("veris_session_id", default=None)


class VerisSDK:
    """Class for mocking tool calls."""

    def __init__(self) -> None:
        """Initialize the ToolMock class."""
        self._mcp = None

    @property
    def session_id(self) -> str | None:
        """Get the session_id from context variable."""
        return _session_id_context.get()

    def set_session_id(self, session_id: str) -> None:
        """Set the session_id in context variable."""
        _session_id_context.set(session_id)
        logger.info(f"Session ID set to {session_id}")

    def clear_session_id(self) -> None:
        """Clear the session_id from context variable."""
        _session_id_context.set(None)
        logger.info("Session ID cleared")

    @property
    def fastapi_mcp(self) -> Any | None:  # noqa: ANN401
        """Get the FastAPI MCP server."""
        return self._mcp

    def set_fastapi_mcp(self, **params_dict: Any) -> None:  # noqa: ANN401
        """Set the FastAPI MCP server."""
        from fastapi import Depends, Request  # noqa: PLC0415
        from fastapi.security import OAuth2PasswordBearer  # noqa: PLC0415
        from fastapi_mcp import (  # type: ignore[import-untyped] # noqa: PLC0415
            AuthConfig,
            FastApiMCP,
        )

        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

        async def authenticate_request(
            _: Request,
            token: str = Depends(oauth2_scheme),  # noqa: ARG001
        ) -> None:
            self.set_session_id(token)

        # Create auth config with dependencies
        auth_config = AuthConfig(
            dependencies=[Depends(authenticate_request)],
        )

        # Merge the provided params with our auth config
        if "auth_config" in params_dict:
            # Merge the provided auth config with our dependencies
            provided_auth_config = params_dict.pop("auth_config")
            if provided_auth_config.dependencies:
                auth_config.dependencies.extend(provided_auth_config.dependencies)
            # Copy other auth config properties if they exist
            for field, value in provided_auth_config.model_dump(exclude_none=True).items():
                if field != "dependencies" and hasattr(auth_config, field):
                    setattr(auth_config, field, value)

        # Create the FastApiMCP instance with merged parameters
        self._mcp = FastApiMCP(
            auth_config=auth_config,
            **params_dict,
        )

    def mock(self, func: Callable) -> Callable:
        """Decorator for mocking tool calls."""
        endpoint = os.getenv("VERIS_MOCK_ENDPOINT_URL")
        if not endpoint:
            error_msg = "VERIS_MOCK_ENDPOINT_URL environment variable is not set"
            raise ValueError(error_msg)
        # Default timeout of 30 seconds
        timeout = float(os.getenv("VERIS_MOCK_TIMEOUT", "30.0"))

        @wraps(func)
        async def wrapper(
            *args: tuple[object, ...],
            **kwargs: dict[str, object],
        ) -> object:
            # Check if we're in simulation mode
            env_mode = os.getenv("ENV", "").lower()
            if env_mode != "simulation":
                # If not in simulation mode, execute the original function
                return await func(*args, **kwargs)
            logger.info(f"Simulating function: {func.__name__}")
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)

            # Extract return type object (not just the name)
            return_type_obj = type_hints.pop("return", Any)

            # Create parameter info
            params_info = {}
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for param_name, param_value in bound_args.arguments.items():
                params_info[param_name] = {
                    "value": param_value,
                    "type": type_hints.get(param_name, Any).__name__,
                }

            # Get function docstring
            docstring = inspect.getdoc(func) or ""
            # Prepare payload
            payload = {
                "session_id": self.session_id,
                "tool_call": {
                    "function_name": func.__name__,
                    "parameters": params_info,
                    "return_type": return_type_obj.__name__,
                    "docstring": docstring,
                },
            }

            # Send request to endpoint with timeout
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                mock_result = response.json()["result"]
                logger.info(f"Mock response: {mock_result}")

            # Parse the mock result if it's a string
            if isinstance(mock_result, str):
                with suppress(json.JSONDecodeError):
                    mock_result = json.loads(mock_result)

            # Convert the mock result to the expected return type
            return convert_to_type(mock_result, return_type_obj)

        return wrapper


veris = VerisSDK()

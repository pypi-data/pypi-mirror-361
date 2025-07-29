import json
import multiprocessing
import socket
import time
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest
import uvicorn
from mcp import ClientSession, ListToolsResult
from mcp.client.sse import sse_client
from mcp.types import CallToolResult

from veris_ai import veris

from .fixtures.simple_app import make_simple_fastapi_app

HOST = "127.0.0.1"
SERVER_NAME = "Test MCP Server"


def run_server_with_mock(server_port: int) -> None:
    """Run server with mocked HTTP client for veris."""
    # Configure the server
    fastapi = make_simple_fastapi_app()
    veris.set_fastapi_mcp(
        fastapi=fastapi,
        name=SERVER_NAME,
        description="Test description",
    )
    assert veris.fastapi_mcp is not None
    veris.fastapi_mcp.mount()

    # Create a mock client that will be used by veris
    class MockAsyncClient:
        def __init__(self, **kwargs):
            self.timeout = kwargs.get("timeout")

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def post(self, _url, json=None, **_kwargs):
            # Log the request
            with Path("/tmp/veris_mock_payloads.log").open("a") as f:
                import json as json_module

                f.write(json_module.dumps(json) + "\n")
                f.flush()

            # Create mock response
            class MockResponse:
                def __init__(self, data):
                    self._data = data

                async def raise_for_status(self):
                    pass

                def json(self):
                    return self._data

            return MockResponse(
                {
                    "result": {
                        "id": json["tool_call"]["parameters"]["item_id"]["value"],
                        "name": f"Item {json['tool_call']['parameters']['item_id']['value']}",
                        "price": json["tool_call"]["parameters"]["item_id"]["value"] * 10.0,
                        "tags": [f"tag{json['tool_call']['parameters']['item_id']['value']}"],
                        "description": f"Item {json['tool_call']['parameters']['item_id']['value']} description",
                    },
                },
            )

    # Patch httpx.AsyncClient in the veris_ai.tool_mock module
    with patch("veris_ai.tool_mock.httpx.AsyncClient", MockAsyncClient):
        # Start the server
        server = uvicorn.Server(
            config=uvicorn.Config(app=fastapi, host=HOST, port=server_port, log_level="error"),
        )
        server.run()


@pytest.fixture
def server_port_mocked() -> int:
    with socket.socket() as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]


@pytest.fixture
def server_url_mocked(server_port_mocked: int) -> str:
    return f"http://{HOST}:{server_port_mocked}"


@pytest.fixture()
def server_mocked(server_port_mocked: int, simulation_env: None) -> Generator[None, None, None]:
    # Clear the log file
    try:
        with Path("/tmp/veris_mock_payloads.log").open("w") as f:
            f.write("")
    except:
        pass

    proc = multiprocessing.Process(
        target=run_server_with_mock,
        kwargs={"server_port": server_port_mocked},
        daemon=True,
    )
    proc.start()

    # Wait for server to be running
    max_attempts = 20
    attempt = 0
    while attempt < max_attempts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, server_port_mocked))
                break
        except ConnectionRefusedError:
            time.sleep(0.1)
            attempt += 1
    else:
        msg = f"Server failed to start after {max_attempts} attempts"
        raise RuntimeError(msg)
    yield

    # Signal the server to stop
    try:
        proc.terminate()
        proc.join(timeout=2)
    except (OSError, AttributeError):
        pass

    if proc.is_alive():
        proc.kill()
        proc.join(timeout=2)
        if proc.is_alive():
            msg = "server process failed to terminate"
            raise RuntimeError(msg)


@pytest.mark.asyncio
async def test_sse_tool_call_mocked(server_mocked: None, server_url_mocked: str) -> None:
    """Test SSE tool call with mocked HTTP endpoint."""
    session_id = "test-session-id"

    async with (
        sse_client(
            server_url_mocked + "/mcp",
            headers={"Authorization": f"Bearer {session_id}"},
        ) as streams,
        ClientSession(*streams) as session,
    ):
        await session.initialize()

        tools_list_result = await session.list_tools()
        assert isinstance(tools_list_result, ListToolsResult)
        assert len(tools_list_result.tools) > 0

        tool_call_result = await session.call_tool("get_item", {"item_id": 1})
        assert isinstance(tool_call_result, CallToolResult)
        assert not tool_call_result.isError
        assert tool_call_result.content is not None
        assert len(tool_call_result.content) > 0

        # Read the captured payloads
        with Path("/tmp/veris_mock_payloads.log").open("r") as f:
            payloads = f.readlines()

        assert len(payloads) > 0, "No payloads were captured"

        # Parse and verify the payload
        payload_str = payloads[0].strip()
        payload = json.loads(payload_str)

        # Verify the session_id was passed correctly
        assert payload["session_id"] == session_id
        assert payload["tool_call"]["function_name"] == "get_item"
        assert payload["tool_call"]["parameters"]["item_id"]["value"] == 1

        print(f"SUCCESS: Verified session_id '{session_id}' was sent in payload")
        print(f"SUCCESS: Full captured payload: {json.dumps(payload, indent=2)}")

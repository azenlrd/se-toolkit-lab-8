"""MCP server for observability tools (VictoriaLogs and VictoriaTraces)."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

from mcp_obs.observability import ObservabilityClient


def _text(data: Any) -> list[TextContent]:
    """Convert data to MCP text response."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    elif isinstance(data, (list, tuple)):
        payload = [item.model_dump() if isinstance(item, BaseModel) else item for item in data]
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, default=str))]


# Tool specifications
class LogsSearchParams(BaseModel):
    query: str = Field(..., description="LogsQL query string (e.g., 'service.name:\"backend\" severity:ERROR')")
    limit: int = Field(default=10, description="Maximum number of log entries to return")
    time_range: str = Field(default="10m", description="Time range for the query (e.g., '10m', '1h', '1d')")


class LogsErrorCountParams(BaseModel):
    time_range: str = Field(default="1h", description="Time window to count errors (e.g., '10m', '1h')")
    service: str | None = Field(default=None, description="Filter by service name (optional)")


class TracesListParams(BaseModel):
    service: str = Field(..., description="Service name to search traces for")
    limit: int = Field(default=5, description="Maximum number of traces to return")


class TracesGetParams(BaseModel):
    trace_id: str = Field(..., description="Trace ID to fetch")


async def handle_logs_search(client: ObservabilityClient, args: LogsSearchParams) -> Any:
    """Search logs using VictoriaLogs API."""
    return await client.logs_search(args.query, args.limit, args.time_range)


async def handle_logs_error_count(client: ObservabilityClient, args: LogsErrorCountParams) -> Any:
    """Count errors per service over a time window."""
    return await client.logs_error_count(args.time_range, args.service)


async def handle_traces_list(client: ObservabilityClient, args: TracesListParams) -> Any:
    """List recent traces for a service."""
    return await client.traces_list(args.service, args.limit)


async def handle_traces_get(client: ObservabilityClient, args: TracesGetParams) -> Any:
    """Fetch a specific trace by ID."""
    return await client.traces_get(args.trace_id)


TOOL_SPECS = [
    ("logs_search", LogsSearchParams, handle_logs_search),
    ("logs_error_count", LogsErrorCountParams, handle_logs_error_count),
    ("traces_list", TracesListParams, handle_traces_list),
    ("traces_get", TracesGetParams, handle_traces_get),
]

TOOLS_BY_NAME = {name: (params, handler) for name, params, handler in TOOL_SPECS}


def create_server(client: ObservabilityClient) -> Server:
    """Create the MCP observability server."""
    server = Server("observability")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        tools = []
        for name, params_model, _ in TOOL_SPECS:
            tool = Tool(
                name=name,
                description=params_model.__doc__ or f"Tool: {name}",
                inputSchema=params_model.model_json_schema(),
            )
            tools.append(tool)
        return tools

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[TextContent]:
        """Call an observability tool."""
        if name not in TOOLS_BY_NAME:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        params_model, handler = TOOLS_BY_NAME[name]
        try:
            args = params_model.model_validate(arguments or {})
            result = await handler(client, args)
            return _text(result)
        except Exception as exc:
            return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    """Run the MCP observability server."""
    # VictoriaLogs and VictoriaTraces URLs from environment or defaults
    import os
    victorialogs_url = os.environ.get("VICTORIALOGS_URL", "http://victorialogs:9428")
    victoriatraces_url = os.environ.get("VICTORIATRACES_URL", "http://victoriatraces:10428")
    
    client = ObservabilityClient(victorialogs_url, victoriatraces_url)
    server = create_server(client)
    
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())

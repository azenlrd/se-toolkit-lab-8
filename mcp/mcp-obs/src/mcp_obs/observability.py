"""VictoriaLogs and VictoriaTraces HTTP API client."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """A single log entry from VictoriaLogs."""
    msg: str = Field(default="", alias="_msg")
    time: str = Field(default="", alias="_time")
    stream: dict = Field(default_factory=dict, alias="_stream")
    severity: str = Field(default="")
    service_name: str = Field(default="", alias="service.name")
    event: str = Field(default="")
    trace_id: str = Field(default="", alias="trace_id")
    span_id: str = Field(default="", alias="span_id")
    error: str = Field(default="")


class TraceData(BaseModel):
    """Trace data from VictoriaTraces."""
    trace_id: str = Field(default="")
    spans: list[dict] = Field(default_factory=list)
    processes: dict = Field(default_factory=dict)


class ObservabilityClient:
    """Client for VictoriaLogs and VictoriaTraces HTTP APIs."""

    def __init__(self, victorialogs_url: str, victoriatraces_url: str) -> None:
        self.victorialogs_url = victorialogs_url.rstrip("/")
        self.victoriatraces_url = victoriatraces_url.rstrip("/")

    async def logs_search(
        self, query: str, limit: int = 10, time_range: str = "10m"
    ) -> list[LogEntry]:
        """
        Search logs using VictoriaLogs LogsQL query.
        
        Args:
            query: LogsQL query string (e.g., 'service.name:"backend" severity:ERROR')
            limit: Maximum number of entries to return
            time_range: Time range for the query (e.g., '10m', '1h')
        
        Returns:
            List of log entries matching the query
        """
        # Prepend time range to query if not already present
        if "_time:" not in query:
            full_query = f"_time:{time_range} {query}"
        else:
            full_query = query
        
        url = f"{self.victorialogs_url}/select/logsql/query"
        params = {"query": full_query, "limit": str(limit)}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            
            # VictoriaLogs returns newline-delimited JSON
            entries = []
            for line in response.text.strip().split("\n"):
                if line.strip():
                    try:
                        data = response.json() if not line else __import__("json").loads(line)
                        entries.append(LogEntry(**data))
                    except Exception:
                        # If parsing fails, return raw data
                        return [{"raw": line}]
            
            # Handle case where response is a single JSON object
            if not entries and response.text.strip():
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        entries.append(LogEntry(**data))
                    elif isinstance(data, list):
                        entries = [LogEntry(**item) for item in data]
                except Exception:
                    return [{"raw": response.text}]
            
            return entries

    async def logs_error_count(
        self, time_range: str = "1h", service: str | None = None
    ) -> dict[str, int]:
        """
        Count errors per service over a time window.
        
        Args:
            time_range: Time window to count errors (e.g., '10m', '1h')
            service: Optional service name filter
        
        Returns:
            Dictionary mapping service names to error counts
        """
        query = f"_time:{time_range} severity:ERROR"
        if service:
            query += f' service.name:"{service}"'
        
        entries = await self.logs_search(query, limit=1000, time_range=time_range)
        
        # Count errors by service
        error_counts: dict[str, int] = {}
        for entry in entries:
            svc = entry.service_name or "unknown"
            error_counts[svc] = error_counts.get(svc, 0) + 1
        
        return {"time_range": time_range, "total_errors": sum(error_counts.values()), "by_service": error_counts}

    async def traces_list(
        self, service: str, limit: int = 5
    ) -> list[TraceData]:
        """
        List recent traces for a service.
        
        Args:
            service: Service name to search traces for
            limit: Maximum number of traces to return
        
        Returns:
            List of trace summaries
        """
        url = f"{self.victoriatraces_url}/select/jaeger/api/traces"
        params = {"service": service, "limit": str(limit)}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        traces = []
        for trace_data in data.get("data", []):
            trace = TraceData(
                trace_id=trace_data.get("traceID", ""),
                spans=trace_data.get("spans", []),
                processes=trace_data.get("processes", {}),
            )
            traces.append(trace)
        
        return traces

    async def traces_get(self, trace_id: str) -> TraceData:
        """
        Fetch a specific trace by ID.
        
        Args:
            trace_id: Trace ID to fetch
        
        Returns:
            Full trace data with all spans
        """
        url = f"{self.victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        # VictoriaTraces returns a list of traces
        trace_list = data.get("data", [])
        if not trace_list:
            return TraceData(trace_id=trace_id, spans=[], processes={})
        
        trace_data = trace_list[0]
        return TraceData(
            trace_id=trace_data.get("traceID", trace_id),
            spans=trace_data.get("spans", []),
            processes=trace_data.get("processes", {}),
        )

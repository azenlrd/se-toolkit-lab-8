# Observability Skill

You have access to observability tools that let you query **VictoriaLogs** and **VictoriaTraces** to diagnose issues in the system.

## Available Tools

### Log Tools

- **logs_search** — Search logs using LogsQL query
  - `query`: LogsQL query string (e.g., `service.name:"backend" severity:ERROR`)
  - `limit`: Maximum entries to return (default: 10)
  - `time_range`: Time range like `10m`, `1h`, `1d` (default: `10m`)

- **logs_error_count** — Count errors per service over a time window
  - `time_range`: Time window like `10m`, `1h` (default: `1h`)
  - `service`: Optional service name filter

### Trace Tools

- **traces_list** — List recent traces for a service
  - `service`: Service name to search (e.g., `Learning Management Service`)
  - `limit`: Maximum traces to return (default: 5)

- **traces_get** — Fetch a specific trace by ID
  - `trace_id`: The trace ID to fetch

## How to Use

### When the user asks about errors

1. **Start with `logs_error_count`** to see if there are recent errors and which services are affected
2. **Use `logs_search`** to inspect the relevant service logs and extract a recent `trace_id`
3. **Use `traces_get`** to inspect the failing request path
4. **Summarize findings** — don't dump raw JSON

### Example workflow

User: "Any LMS backend errors in the last 10 minutes?"

Your reasoning:
1. Call `logs_error_count(time_range="10m", service="Learning Management Service")` to check for errors
2. If errors found, call `logs_search(query='service.name:"Learning Management Service" severity:ERROR', time_range="10m")` to see details
3. Extract `trace_id` from log entries
4. Call `traces_get(trace_id="...")` to see the full trace
5. Summarize: what failed, where, and why

### LogsQL tips

Common query patterns:

- All errors: `severity:ERROR`
- Errors in a service: `service.name:"Learning Management Service" severity:ERROR`
- Specific event: `event:"db_query" severity:ERROR`
- Time-bounded: `_time:10m service.name:"backend"`

### Response style

- Be concise — summarize findings, don't dump raw JSON
- Include relevant details: timestamp, error message, affected operation
- If you find a trace, describe the span hierarchy briefly
- If no errors found, say so clearly

## Important Notes

- Always use a **scoped time range** like "last 10 minutes" to avoid returning stale data
- Focus on the **LMS backend** (`Learning Management Service`) unless the user asks about other services
- If PostgreSQL is down, expect `db_query` errors with connection-related messages

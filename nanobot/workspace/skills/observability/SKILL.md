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

- **traces_get` — Fetch a specific trace by ID
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

### When the user asks "What went wrong?" or "Check system health"

This is a **one-shot investigation** request. Follow this flow:

1. **Check for recent errors** with `logs_error_count(time_range="10m")`
2. **Search for specific error logs** with `logs_search(query='severity:ERROR', time_range="10m", limit=10)`
3. **Extract a trace_id** from the error logs
4. **Fetch the full trace** with `traces_get(trace_id="...")`
5. **Provide a single coherent summary** that includes:
   - **Log evidence**: Quote the specific error message from logs
   - **Trace evidence**: Describe the failing span from the trace
   - **Root cause**: Name the affected service and the failing operation
   - **Impact**: Explain what the user would experience

**Important:** Look for discrepancies between:
- What the logs/traces show (real database/backend failure)
- What the HTTP response reported (may be misleading like `404 Items not found`)

The planted bug may cause the backend to misreport database failures as `404` errors.

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

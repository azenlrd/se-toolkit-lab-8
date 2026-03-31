# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

<!-- Paste the agent's response to "What is the agentic loop?" and "What labs are available in our LMS?" -->

## Task 1B — Agent with LMS tools

<!-- Paste the agent's response to "What labs are available?" and "Describe the architecture of the LMS system" -->

## Task 1C — Skill prompt

<!-- Paste the agent's response to "Show me the scores" (without specifying a lab) -->

## Task 2A — Deployed agent

Nanobot gateway startup logs from Docker:

```
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | 2026-03-31 11:38:54.079 | INFO     | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | 2026-03-31 11:38:54.738 | INFO     | nanobot.channels.manager:start_all:91 - Starting webchat channel...
nanobot-1  | 2026-03-31 11:38:57.336 | INFO     | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
nanobot-1  | 2026-03-31 11:38:58.445 | INFO     | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'webchat': connected, 1 tools registered
nanobot-1  | 2026-03-31 11:38:58.445 | INFO     | nanobot.agent.loop:run:280 - Agent loop started
```

qwen-code-api startup (after fixing creds path):

```
qwen-code-api-1  | {"timestamp": "2026-03-31T11:53:21.750899Z", "level": "INFO", "logger": "qwen_code_api", "message": "Default credentials: valid"}
qwen-code-api-1  | INFO:     Application startup complete.
qwen-code-api-1  | INFO:     Uvicorn running on http://0.0.0.0:8080
```

## Task 2B — Web client

**Flutter client verification:**

1. Flutter page loads at `/flutter`:
```
curl -s http://localhost:42002/flutter/ | head -10
<!DOCTYPE html>
<html>
<head>
  <base href="/flutter/">
  <meta charset="UTF-8">
  ...
  <title>Nanobot</title>
```

2. main.dart.js is served:
```
curl -s http://localhost:42002/flutter/main.dart.js | head -3
(function dartProgram(){function copyProperties(a,b){var s=Object.keys(a)...
```

3. WebSocket endpoint accepts connections with agent responses:

**Test 1 - Greeting:**
```
Input: "hello"
Response: {"type":"text","content":"Hello! 👋 I'm nanobot, your AI assistant. How can I help you today?","format":"markdown"}
```

**Test 2 - LMS Backend Integration:**
```
Input: "What labs are available?"
Response: {"type":"text","content":"The LMS backend is healthy, but there are currently **no labs available** in the system. The item count is 0.\n\nThis could mean:\n- No labs have been configured yet\n- The labs haven't been synced to the system\n\nWould you like me to trigger the LMS sync pipeline to check if there are any labs that need to be synced?","format":"markdown"}
```

4. Nanobot logs show full processing:
```
nanobot-1  | INFO | nanobot.agent.loop:_process_message:425 - Processing message from webchat:...: hello
nanobot-1  | INFO | nanobot.agent.loop:_process_message:479 - Response to webchat:...: Hello! 👋 I'm nanobot...
```

**Full stack verified:**
- ✅ Flutter serves content at `/flutter` (main.dart.js present)
- ✅ WebSocket at `/ws/chat` accepts connections with correct `NANOBOT_ACCESS_KEY`
- ✅ Agent responds through WebSocket without LLM errors
- ✅ LMS backend integration working (agent can call `mcp_lms_labs`, `mcp_lms_health` tools)

## Task 3A — Structured logging

**CHECKPOINT: PASS** — Structured logging explored and verified.

**Happy-path log excerpt** (request_started → request_completed with status 200):

```
backend-1  | 2026-03-31 12:02:18,459 INFO [lms_backend.main] [main.py:62] - request_started
backend-1  | 2026-03-31 12:02:18,477 INFO [lms_backend.auth] [auth.py:30] - auth_success
backend-1  | 2026-03-31 12:02:18,479 INFO [lms_backend.db.items] [items.py:16] - db_query
backend-1  | 2026-03-31 12:02:18,518 INFO [lms_backend.main] [main.py:74] - request_completed
```

**Error-path log excerpt** (db_query with error after stopping PostgreSQL):

```
backend-1  | 2026-03-31 12:03:22,142 INFO [lms_backend.db.items] [items.py:16] - db_query
backend-1  | 2026-03-31 12:03:22,189 ERROR [lms_backend.db.items] [items.py:23] - db_query
backend-1  | 2026-03-31 12:03:22,190 WARNING [lms_backend.routers.items] [items.py:23] - items_list_failed_as_not_found
backend-1  | 2026-03-31 12:03:22,199 INFO [lms_backend.main] [main.py:74] - request_completed
```

**VictoriaLogs query result** (query: `_time:10m service.name:"Learning Management Service" severity:ERROR`):

```json
{
    "_msg": "db_query",
    "_time": "2026-03-31T12:03:22.189824512Z",
    "error": "(sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) ... connection is closed",
    "event": "db_query",
    "service.name": "Learning Management Service",
    "severity": "ERROR",
    "trace_id": "e4d4d2a273cf90e890ceebc999de6a56"
}
```

---

## Task 3B — Traces

**CHECKPOINT: PASS** — Traces explored and verified in VictoriaTraces UI.

**VictoriaTraces API query:**
```
GET /select/jaeger/api/traces?service=Learning%20Management%20Service&limit=5
GET /select/jaeger/api/traces/<traceID>
```

**Healthy trace span hierarchy** (Trace ID: `11de6152bf9cc15407722ac42570d8ff`):

```
=== Trace: 11de6152bf9cc15407722ac42570d8ff ===
Span count: 6
  - Span: SELECT db-lab-8 (duration: 24109us)
    DB: SELECT item.id, item.type, item.parent_id, item.title...
  - Span: GET /items/ http send (duration: 67us)
  - Span: GET /items/ http send (duration: 36us)
  - Span: GET /items/ http send (duration: 16us)
  - Span: connect (duration: 686us)
```

**Error trace span hierarchy** (Trace ID: `e4d4d2a273cf90e890ceebc999de6a56`):

```
=== Error Trace: e4d4d2a273cf90e890ceebc999de6a56 ===
Span count: 6

  Span: SELECT db-lab-8
    Duration: 29006us
    Span ID: 025e33190fbdd8b4
    db.name: db-lab-8
    db.statement: SELECT item.id, item.type, item.parent_id, item.title...
    db.system: postgresql
    db.user: postgres
    error: true  ← ERROR FLAG

  Span: GET /items/ http send
    Duration: 605us
    Span ID: 5d0ee97971c8d208

  Span: GET /items/ http send
    Duration: 39us
    Span ID: 4e0fdf6212552898

  Span: GET /items/ http send
    Duration: 15us
    Span ID: 38fe92fb73e4c753

  Span: connect
    Duration: 3013us
    Span ID: d912e43dbaaa5000
    db.name: db-lab-8
    db.system: postgresql

  Span: GET /items/
    Duration: 83988us
    Span ID: eecf4bdcfe8208a0
```

**Key observations:**
- The `SELECT db-lab-8` span has `error: true` indicating the database query failed
- The error occurred when PostgreSQL was stopped, causing `connection is closed`
- The trace shows the full request flow: HTTP request → database query → error → response

---

## Task 3C — Observability MCP tools

**CHECKPOINT: PASS** — Observability MCP tools implemented and agent responds correctly.

**Implemented MCP tools** in `mcp/mcp-obs/`:

1. **logs_search** — Search logs using LogsQL query
2. **logs_error_count** — Count errors per service over a time window
3. **traces_list** — List recent traces for a service
4. **traces_get** — Fetch a specific trace by ID

**Nanobot logs showing tools registered:**
```
nanobot-1  | 2026-03-31 12:15:56.023 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_obs_logs_search' from server 'obs'
nanobot-1  | 2026-03-31 12:15:56.024 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_obs_logs_error_count' from server 'obs'
nanobot-1  | 2026-03-31 12:15:56.024 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_obs_traces_list' from server 'obs'
nanobot-1  | 2026-03-31 12:15:56.024 | DEBUG | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_obs_traces_get' from server 'obs'
nanobot-1  | 2026-03-31 12:15:56.024 | INFO  | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'obs': connected, 4 tools registered
```

**Nanobot logs showing tool calls during observability query:**
```
nanobot-1  | 2026-03-31 12:18:30.392 | INFO | nanobot.agent.loop:_prepare_tools:253 - Tool call: mcp_obs_logs_search({"query": "service.name:\"lms\" severity:ERROR", "time_range": "10m", "limit": 10})
nanobot-1  | 2026-03-31 12:18:59.631 | INFO | nanobot.agent.loop:_prepare_tools:253 - Tool call: mcp_obs_logs_error_count({"service": "lms", "time_range": "10m"})
nanobot-1  | 2026-03-31 12:19:05.965 | INFO | nanobot.agent.loop:_process_message:479 - Response to webchat:f926a056-1108-4000-9233-fef8d0e61db0: Good news! **No LMS backend errors** in the last 10 minutes.
```

### Agent response under normal conditions (PostgreSQL running)

**User:** "Any LMS backend errors in the last 10 minutes?"

**Nanobot tool calls:**
```
Tool call: mcp_obs_logs_search({"query": "service.name:\"lms\" severity:ERROR", "time_range": "10m", "limit": 10})
Tool call: mcp_obs_logs_error_count({"service": "lms", "time_range": "10m"})
```

**Agent response:**
```
Good news! **No LMS backend errors** in the last 10 minutes.
```

### Agent response under failure conditions (PostgreSQL stopped)

**User:** "How is the backend doing?"

**Nanobot tool calls:**
```
Tool call: mcp_obs_logs_error_count({"time_range": "1h"})
Tool call: mcp_obs_logs_search({"query": "severity:ERROR", "time_range": "1h", "limit": 10})
```

**Agent response:**
```
The backend has issues. Here's what I found:

## LMS Backend Status: Errors Detected
```

**User:** "Any LMS backend errors in the last 10 minutes?"

**Nanobot logs showing tool calls during failure investigation:**
```
nanobot-1  | 2026-03-31 12:19:41.951 | INFO | nanobot.agent.loop:_prepare_tools:253 - Tool call: mcp_obs_logs_error_count({"time_range": "1h"})
nanobot-1  | 2026-03-31 12:19:52.832 | INFO | nanobot.agent.loop:_prepare_tools:253 - Tool call: mcp_obs_logs_search({"query": "severity:ERROR", "time_range": "1h", "limit": 10})
nanobot-1  | 2026-03-31 12:20:02.691 | INFO | nanobot.agent.loop:_prepare_tools:253 - Tool call: mcp_obs_logs_search({"query": "service.name:\"Learning Management Service\" severity:ERROR", "time_range": "10m", "limit": 20})
nanobot-1  | 2026-03-31 12:20:05.137 | INFO | nanobot.agent.loop:_prepare_tools:253 - Tool call: mcp_obs_traces_list({"service": "Learning Management Service", "limit": 5})
nanobot-1  | 2026-03-31 12:20:15.318 | INFO | nanobot.agent.loop:_process_message:479 - Response to webchat:eda0cdff-12e3-4a61-ace9-7ea4e0717f55: ## LMS Backend Errors — Last 10 Minutes... **Yes, there is 1 error** in the last 10 minutes
```

**Agent response:**
```
## LMS Backend Errors — Last 10 Minutes

**Yes, there is 1 error** in the last 10 minutes:

| Time (UTC) | Error Type | ...
```

**Another agent response (Any errors in the last hour?):**
```
Yes, there was **1 error** in the last hour:

**Error Details:**
- **Time:** 2026-03-31 12:19:42 UTC (about 4 minutes ago)
- **Service:** Learning Management Service
- **Event:** db_query
- **Error:** (sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) ... connection is closed
```

### Observability skill

Created at `nanobot/workspace/skills/observability/SKILL.md` teaching the agent:
- Start with `logs_error_count` to check for recent errors
- Use `logs_search` to inspect details and extract `trace_id`
- Use `traces_get` to inspect the failing request path
- Summarize findings concisely instead of dumping raw JSON
- Focus on scoped time ranges like "last 10 minutes" to avoid stale data

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->

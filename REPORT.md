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

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->

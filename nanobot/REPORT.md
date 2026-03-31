# Lab 8 Report

## Task 1A — Bare agent

### Question: "What is the agentic loop?"

**Response:**
The **agentic loop** is the fundamental cycle that autonomous AI agents follow to accomplish tasks. It typically consists of these core stages:

**The Loop**

1. **Perceive** — Gather information from the environment (user input, files, APIs, sensors, etc.)
2. **Reason/Plan** — Analyze the situation, determine goals, and decide on actions
3. **Act** — Execute chosen actions using available tools (file operations, API calls, code execution, etc.)
4. **Observe** — Receive feedback from the actions taken (outputs, errors, state changes)
5. **Reflect/Adapt** — Evaluate results, learn from outcomes, and adjust the plan if needed

Then the loop repeats until the goal is achieved or the task is terminated.

**Key Characteristics**

- **Iterative** — Agents don't just respond once; they cycle through multiple iterations
- **Goal-directed** — Each iteration moves toward accomplishing an objective
- **Feedback-driven** — Results from actions inform subsequent decisions
- **Autonomous** — The agent decides what to do next without constant human guidance

**Example**

For a task like "fix the bug in this code":

1. Perceive: Read the code file and error message
2. Reason: Identify the likely cause of the bug
3. Act: Edit the file to fix the issue
4. Observe: Run tests to see if the fix works
5. Reflect: If tests pass, done. If not, diagnose why and loop back

This loop is what distinguishes agents from simple chatbots—agents can take multi-step actions and adapt based on outcomes.

---

### Question: "What labs are available in our LMS?"

**Response:**
Based on the workspace structure, here are the **available labs** in this LMS:

**Required Labs**

1. **Task 1** — Set Up the Agent (install nanobot, configure Qwen API, add MCP tools, write skill prompt)
2. **Task 2** — Deploy and Connect a Web Client (Dockerize nanobot, add WebSocket channel + Flutter chat UI)
3. **Task 3** — Give the Agent New Eyes (explore observability data, write log/trace MCP tools)
4. **Task 4** — Diagnose a Failure and Make the Agent Proactive (investigate a failure, schedule health checks, fix a planted bug)

**Optional Labs**

1. **Task 1** — Add a Telegram Bot Client (same agent, different interface)

---

This is Lab 8 — "The Agent is the Interface" where you build a nanobot AI agent as a natural-language interface for the LMS system. The agent can query the LMS backend, access observability data (logs/traces), and proactively report system health.

**Note:** The bare agent inspects local repo files and gives a plausible answer based on docs, but it cannot query real LMS data yet.

---

## Task 1B — Agent with LMS tools

### Question: "What labs are available?"

**Response:**
Here are the available labs:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

The LMS is now healthy with 56 items.

---

### Question: "Is the LMS backend healthy?"

**Response:**
Yes, the LMS backend is healthy! It reports:

- **Status**: healthy
- **Item count**: 56 items
- **Errors**: none

---

### Question: "Which lab has the lowest pass rate?"

**Response:**
Based on the completion rates:

| Lab    | Completion Rate | Passed | Total |
|--------|-----------------|--------|-------|
| Lab 01 | 100.0%          | 258    | 258   |
| Lab 02 | 89.1%           | 131    | 147   |
| Lab 03 | 89.1%           | 156    | 175   |
| Lab 04 | 97.2%           | 239    | 246   |
| Lab 05 | 98.8%           | 247    | 250   |
| Lab 06 | 98.4%           | 242    | 246   |
| Lab 07 | 99.6%           | 238    | 239   |
| Lab 08 | 0.0%            | 0      | 0     |

Lab 02 and Lab 03 are tied for the lowest pass rate among labs with submissions, both at 89.1%.

Note: Lab 08 shows 0.0% because it has no submissions yet (0 passed out of 0 total), so it's not a meaningful comparison.

---

## Task 1C — Skill prompt

### Question: "Show me the scores" (without specifying a lab)

**Response:**
There are 8 labs available. Which lab would you like to see the scores for? Here are the options:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. Lab 08 — lab-08

Or would you like me to show pass rates for all labs?

---

**Skill file created:** `workspace/skills/lms/SKILL.md`

The skill prompt teaches the agent:
- Which `lms_*` tools are available and when to use each one
- To call `lms_labs` first when a lab parameter is needed but not provided
- To ask the user to choose a lab when multiple are available
- To format numeric results nicely (percentages, counts)
- To keep responses concise and offer follow-up actions

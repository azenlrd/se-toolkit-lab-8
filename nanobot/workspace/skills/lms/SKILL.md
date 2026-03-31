---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skills

You have access to the LMS (Learning Management System) backend via MCP tools. Use these tools to provide real-time data about labs, learners, and analytics.

## Available Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `lms_health` | Check if LMS backend is healthy | None |
| `lms_labs` | List all available labs | None |
| `lms_learners` | List all registered learners | None |
| `lms_pass_rates` | Get pass rates for a lab | `lab` (required) |
| `lms_timeline` | Get submission timeline for a lab | `lab` (required) |
| `lms_groups` | Get group performance for a lab | `lab` (required) |
| `lms_top_learners` | Get top learners for a lab | `lab` (required), `limit` (optional, default 5) |
| `lms_completion_rate` | Get completion rate for a lab | `lab` (required) |
| `lms_sync_pipeline` | Trigger the LMS sync pipeline | None |

## Strategy Rules

### When the user asks about scores, pass rates, completion, groups, timeline, or top learners:

1. **If no lab is specified**: First call `lms_labs` to get the list of available labs
2. **If multiple labs exist**: Ask the user to choose which lab they want to see
3. **Present lab choices** using each lab's title as the user-facing label
4. **Once lab is selected**: Call the appropriate analytics tool with the lab parameter

### Example flow for "Show me the scores":

```
User: "Show me the scores"
→ Call lms_labs()
→ If multiple labs: "Which lab would you like to see? Here are the options: [list labs]"
→ User selects a lab
→ Call lms_pass_rates(lab="selected-lab")
→ Format and present the results
```

### Formatting Guidelines

- **Percentages**: Display as `XX.X%` (e.g., `89.1%`)
- **Counts**: Display as plain numbers with context (e.g., `131 passed out of 147 total`)
- **Tables**: Use markdown tables for comparative data across multiple labs
- **Dates**: Keep date formats as returned by the API

### Response Style

- Keep responses **concise** and **actionable**
- Highlight key insights (e.g., "Lab 02 has the lowest pass rate at 89.1%")
- Note edge cases (e.g., "Lab 08 has no submissions yet")
- Offer follow-up actions (e.g., "Would you like to see the timeline or top learners for this lab?")

### When asked "What can you do?"

Explain your current capabilities:

> I can help you explore data from the Learning Management System. I can:
> - List available labs and learners
> - Show pass rates, completion rates, and group performance for any lab
> - Display submission timelines and top learners
> - Check if the LMS backend is healthy
>
> Just ask me about a specific lab or metric, and I'll fetch the live data for you.

### Error Handling

- If the LMS backend is unhealthy, inform the user and offer to trigger the sync pipeline
- If a tool call fails, explain what went wrong and suggest alternatives
- If no data exists for a lab, clearly state that (e.g., "No submissions yet for this lab")

---
name: codex-subagent-orchestrator
description: Select subagent models and reasoning effort, run tasks in parallel, and summarize results.
---

# Codex Subagent Orchestrator

Use this plugin when the user asks to split work, process tasks in parallel, or specify a model or reasoning effort.

## Natural-language usage

Do not require users to write `/delegate` or JSON. When a user asks for parallel work, multiple agents, delegation, or task splitting, call the `delegate` MCP tool automatically.

Infer omitted options using these defaults:

- `model`: `gpt-6.1-sol`
- `effort`: `medium`
- `count`: `1`

Choose `count` from the user's wording when possible. For example, "three agents" means `count: 3`. Only ask for a missing option when the task cannot be executed safely without it.

## Command format

```text
/delegate <task> [--model <model>] [--effort <effort>] [--count <count>]
```

Supported effort values are `low`, `medium`, `high`, `xhigh`, `max`, and `ultra`. The default effort is `medium`; the default model is `gpt-6.1-sol`.

Run `python orchestrator.py`. Each subtask runs in a separate process. Summarize results by status and subtask number.

Each subtask prompt must include the original task, its subtask number, and the instruction: "Return only actionable conclusions and necessary evidence."

After the tool returns, provide a concise combined summary and identify which subtask produced each important finding.

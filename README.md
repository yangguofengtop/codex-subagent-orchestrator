# Codex Subagent Orchestrator

A lightweight MVP for running parallel subagents with configurable models and reasoning effort. `SKILL.md` defines the Codex workflow, `mcp_server.py` exposes an MCP tool, and `orchestrator.py` launches and collects subprocess results.

## Configuration

Set the command template environment variable. It must include `{model}`, `{effort}`, and `{prompt}` placeholders:

```powershell
$env:CODEX_SUBAGENT_COMMAND = 'codex exec --ephemeral --skip-git-repo-check --model {model} -c reasoning_effort="{effort}" "{prompt}"'
```

This template works with the current Codex CLI. Adjust it according to `codex exec --help` if your CLI version differs. Then run:

```powershell
python .\orchestrator.py "Analyze this project's test gaps" --model gpt-6.1-sol --effort high --count 3
```

Results are printed in subtask order. The process exits with code `1` if any subtask fails.

## Use with Codex

Use this directory as a local Skill or copy its contents to your Codex plugin directory. The natural-language entry point is `/delegate`; its parameters match the script.

Configure `mcp_server.py` as an stdio server in your MCP client. It exposes the `delegate` tool with `task`, `model`, `effort`, and `count` arguments.

## Development

```powershell
python -m py_compile orchestrator.py mcp_server.py
python -m unittest discover -s tests -v
```

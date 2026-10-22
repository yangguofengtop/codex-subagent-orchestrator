# Codex Subagent Orchestrator

一个轻量 MVP：由 `SKILL.md` 定义 Codex 的使用方式，`mcp_server.py` 暴露 MCP 工具，`orchestrator.py` 并行启动多个子进程，并为每个子进程传入模型和推理强度。

## 配置

设置命令模板环境变量。模板必须包含 `{model}`、`{effort}`、`{prompt}`：

```powershell
$env:CODEX_SUBAGENT_COMMAND = 'codex exec --ephemeral --skip-git-repo-check --model {model} -c reasoning_effort="{effort}" "{prompt}"'
```

该模板适用于当前 Codex CLI；若 CLI 版本不同，按其 `codex exec --help` 调整。然后运行：

```powershell
python .\orchestrator.py "分析这个项目的测试缺口" --model gpt-6.1-sol --effort high --count 3
```

输出按子任务编号排列；任一子任务失败时进程返回码为 `1`。

## 接入 Codex

将本目录作为本地 Skill 使用，或把目录内容复制到你的 Codex 插件目录。自然语言入口约定为 `/delegate`，参数与脚本一致。

MCP 客户端将 `mcp_server.py` 配置为 stdio server；它提供 `delegate` 工具，参数为 `task`、`model`、`effort`、`count`。

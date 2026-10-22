---
name: codex-subagent-orchestrator
description: 按任务选择子智能体模型和推理强度，并行执行后汇总结果。
---

# Codex 子智能体编排器

当用户要求拆分任务、并行处理或指定模型/强度时，使用本插件。

## 指令格式

```text
/delegate <任务> [--model <模型>] [--effort <强度>] [--count <数量>]
```

强度支持 `low`、`medium`、`high`、`xhigh`、`max`、`ultra`。未指定时使用 `medium`，模型未指定时使用 `gpt-6.1-sol`。

调用 `python orchestrator.py`，每个子任务使用独立进程执行，完成后按成功、失败和输出顺序汇总。

子任务提示词必须包含原始任务、子任务编号和“只返回可执行结论及必要证据”。

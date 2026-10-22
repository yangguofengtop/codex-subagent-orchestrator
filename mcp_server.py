#!/usr/bin/env python3
"""Minimal MCP stdio adapter exposing the orchestrator as one tool."""
import asyncio
import contextlib
import io
import json
import sys

from orchestrator import main_async, argparse


def reply(request_id, result=None, error=None):
    body = {"jsonrpc": "2.0", "id": request_id}
    body["error" if error else "result"] = error or result
    sys.stdout.write(json.dumps(body, ensure_ascii=False) + "\n")
    sys.stdout.flush()


async def serve():
    for line in sys.stdin:
        request = json.loads(line)
        method = request.get("method")
        if method == "initialize":
            reply(request.get("id"), {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "codex-subagent-orchestrator", "version": "0.1.0"}})
        elif method == "tools/list":
            reply(request.get("id"), {"tools": [{"name": "delegate", "description": "按模型和推理强度并行启动子智能体", "inputSchema": {"type": "object", "required": ["task"], "properties": {"task": {"type": "string"}, "model": {"type": "string"}, "effort": {"type": "string", "enum": ["low", "medium", "high", "xhigh", "max", "ultra"]}, "count": {"type": "integer", "minimum": 1, "maximum": 32}}}}]})
        elif method == "tools/call":
            args = request.get("params", {}).get("arguments", {})
            ns = argparse.Namespace(task=args["task"], model=args.get("model", "gpt-6.1-sol"), effort=args.get("effort", "medium"), count=args.get("count", 1), timeout=args.get("timeout", 900))
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                code = await main_async(ns)
            reply(request.get("id"), {"content": [{"type": "text", "text": captured.getvalue() or f"delegate finished with exit code {code}"}]})
        elif method != "notifications/initialized":
            reply(request.get("id"), error={"code": -32601, "message": f"Unknown method: {method}"})


if __name__ == "__main__":
    asyncio.run(serve())

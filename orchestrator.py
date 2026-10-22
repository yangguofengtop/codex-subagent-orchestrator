#!/usr/bin/env python3
"""Dependency-free subprocess orchestrator for Codex-compatible CLIs."""
from __future__ import annotations
import argparse, asyncio, os, shlex, sys
from dataclasses import dataclass

EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
MAX_COUNT = 32

@dataclass
class Result:
    index: int
    output: str = ""
    error: str = ""

def build_command(model: str, effort: str, prompt: str) -> list[str]:
    template = os.environ.get("CODEX_SUBAGENT_COMMAND")
    if not template:
        raise RuntimeError("Set CODEX_SUBAGENT_COMMAND with {model}, {effort}, and {prompt} placeholders.")
    try:
        rendered = template.format(model=model, effort=effort, prompt=prompt)
    except KeyError as exc:
        raise RuntimeError(f"CODEX_SUBAGENT_COMMAND has unknown placeholder: {exc.args[0]}") from exc
    return shlex.split(rendered, posix=True)

async def run_one(index: int, prompt: str, model: str, effort: str, timeout: float) -> Result:
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(*build_command(model, effort, prompt), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        if proc.returncode:
            return Result(index, error=stderr.decode(errors="replace").strip() or f"exit {proc.returncode}")
        return Result(index, output=stdout.decode(errors="replace").strip())
    except asyncio.TimeoutError:
        if proc is not None:
            proc.kill(); await proc.wait()
        return Result(index, error=f"timeout after {timeout:g}s")
    except Exception as exc:
        return Result(index, error=str(exc))

async def main_async(args: argparse.Namespace) -> int:
    prompts = [f"Subtask {i + 1}/{args.count}: {args.task}\nReturn only actionable conclusions and necessary evidence." for i in range(args.count)]
    results = await asyncio.gather(*(run_one(i, prompt, args.model, args.effort, args.timeout) for i, prompt in enumerate(prompts)))
    for result in results:
        print(f"[{result.index + 1}] {'OK' if not result.error else 'FAILED'}")
        print(result.output if not result.error else result.error)
    return 1 if any(result.error for result in results) else 0

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run parallel Codex subagents.")
    parser.add_argument("task")
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--effort", choices=sorted(EFFORTS), default="medium")
    parser.add_argument("--count", type=int, choices=range(1, MAX_COUNT + 1), default=1)
    parser.add_argument("--timeout", type=float, default=900)
    args = parser.parse_args(argv)
    if args.timeout <= 0: parser.error("--timeout must be greater than 0")
    return args

if __name__ == "__main__":
    try: raise SystemExit(asyncio.run(main_async(parse_args())))
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr); raise SystemExit(2)

def main() -> int:
    return asyncio.run(main_async(parse_args()))

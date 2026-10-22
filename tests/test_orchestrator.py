import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import orchestrator


class OrchestratorTests(unittest.TestCase):
  def test_build_command_uses_all_values(self):
    old = __import__('os').environ.get("CODEX_SUBAGENT_COMMAND")
    __import__('os').environ["CODEX_SUBAGENT_COMMAND"] = "echo {model} {effort} {prompt}"
    self.assertEqual(orchestrator.build_command("m", "high", "hello world"), ["echo", "m", "high", "hello world"])
    if old is None: __import__('os').environ.pop("CODEX_SUBAGENT_COMMAND", None)
    else: __import__('os').environ["CODEX_SUBAGENT_COMMAND"] = old


  def test_missing_template_fails(self):
    old = __import__('os').environ.pop("CODEX_SUBAGENT_COMMAND", None)
    try:
        orchestrator.build_command("m", "low", "p")
    except RuntimeError as exc:
        assert "CODEX_SUBAGENT_COMMAND" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")
    finally:
        if old is not None: __import__('os').environ["CODEX_SUBAGENT_COMMAND"] = old


  def test_parallel_success(self):
    __import__('os').environ["CODEX_SUBAGENT_COMMAND"] = f'"{sys.executable}" -c "print(123)"'
    args = orchestrator.parse_args(["task", "--count", "2", "--timeout", "5"])
    self.assertEqual(asyncio.run(orchestrator.main_async(args)), 0)


  def test_timeout(self):
    __import__('os').environ["CODEX_SUBAGENT_COMMAND"] = f'"{sys.executable}" -c "import time; time.sleep(1)"'
    args = orchestrator.parse_args(["task", "--timeout", "0.01"])
    self.assertEqual(asyncio.run(orchestrator.main_async(args)), 1)

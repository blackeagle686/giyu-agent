import asyncio

from giyu.cognition.brains.command_translator import CommandRuleEngine
from giyu.runtime.pty_executor import PTYExecutor
from giyu.backend.auth import validate_clearance_token


def test_pty_executor_echo():
    executor = PTYExecutor()
    res = asyncio.run(executor.execute("echo hello", timeout_ms=5000))
    assert res["exit_code"] == 0
    assert "hello" in res["output"]


def test_rule_engine_matches_basic_intent():
    engine = CommandRuleEngine()
    out = engine.match_intent("show files in this directory")
    assert out["status"] == "allow_match"
    assert "ls" in out["command"]


def test_clearance_token_validation_default_false():
    assert validate_clearance_token("") is False

"""Smoke test for intention parser skeleton."""

from src.core.intention_parser import IntentionParser


def test_parse_returns_placeholder_intention() -> None:
    parser = IntentionParser()
    intention = parser.parse("hello")
    assert intention.style == "unknown"


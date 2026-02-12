"""Smoke tests for Phase 1 physics validator."""

from src.core.physics_validator import PhysicsValidator
from src.llm_plugins.kimi_client import KimiClient


def test_validation_detects_basic_conflict(monkeypatch) -> None:
    monkeypatch.setattr(
        KimiClient,
        "validate_physics",
        lambda self, prompt_text: {
            "ok": False,
            "issues": ["检测到矛盾：大风环境下主体静止。"],
        },
    )
    validator = PhysicsValidator()
    result = validator.validate("大风中角色静止不动。")
    assert result.ok is False
    assert len(result.issues) > 0


"""Smoke tests for Phase 1 physics validator."""

from src.core.physics_validator import PhysicsValidator


def test_validation_detects_basic_conflict() -> None:
    validator = PhysicsValidator()
    result = validator.validate("大风中角色静止不动。")
    assert result.ok is False
    assert len(result.issues) > 0


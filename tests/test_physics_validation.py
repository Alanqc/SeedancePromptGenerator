"""Smoke test for physics validator skeleton."""

from src.core.physics_validator import PhysicsValidator


def test_validation_defaults_to_ok() -> None:
    validator = PhysicsValidator()
    result = validator.validate("placeholder")
    assert result.ok is True


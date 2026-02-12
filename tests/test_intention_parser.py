"""Smoke tests for Phase 1 intention parser."""

from src.core.intention_parser import IntentionParser
from src.llm_plugins.kimi_client import KimiClient


def test_parse_extracts_style_and_camera_hint(monkeypatch) -> None:
    monkeypatch.setattr(
        KimiClient,
        "parse_intention",
        lambda self, text, image_paths: {
            "style": "cyberpunk_cinematic",
            "mood": "neutral",
            "lighting": "natural",
            "camera_hint": "85mm",
            "needs_precise_params": True,
            "technical_hints": ["rain_particles"],
            "subject": "角色",
            "raw_input": text,
        },
    )
    parser = IntentionParser()
    intention = parser.parse("赛博朋克雨夜场景，85mm镜头。")
    assert intention.style == "cyberpunk_cinematic"
    assert intention.camera_hint == "85mm"
    assert intention.needs_precise_params is True


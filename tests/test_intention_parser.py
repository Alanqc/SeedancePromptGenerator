"""Smoke tests for Phase 1 intention parser."""

from src.core.intention_parser import IntentionParser


def test_parse_extracts_style_and_camera_hint() -> None:
    parser = IntentionParser()
    intention = parser.parse("赛博朋克雨夜场景，85mm镜头。")
    assert intention.style == "cyberpunk_cinematic"
    assert intention.camera_hint == "85mm"
    assert intention.needs_precise_params is True


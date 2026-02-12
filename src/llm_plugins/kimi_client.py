"""Kimi client implementation with real API support."""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_client import BaseClient


class KimiAPIError(RuntimeError):
    """Raised when Kimi API request fails."""


class KimiClient(BaseClient):
    """Kimi client for real API calls only."""

    def __init__(self) -> None:
        private_config = self._load_private_kimi_config()
        self.base_url = (
            os.getenv("KIMI_BASE_URL")
            or private_config.get("base_url")
            or "https://api.moonshot.cn/v1"
        ).rstrip("/")
        self.api_key = self._resolve_api_key(private_config)
        self.model = os.getenv("KIMI_MODEL") or private_config.get("model") or "kimi-k2.5"
        self.timeout_seconds = int(os.getenv("KIMI_TIMEOUT_SECONDS", "60"))

    def parse_intention(self, text: str, image_paths: List[str]) -> Dict[str, Any]:
        _ = image_paths
        raw = self._chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是视频生成意图解析器。"
                        "请把用户输入转成 JSON，字段必须包含："
                        "style,mood,lighting,camera_hint,needs_precise_params,"
                        "technical_hints,subject,raw_input。"
                        "technical_hints 必须是字符串数组。"
                        "仅输出 JSON，不要输出额外文字。"
                    ),
                },
                {"role": "user", "content": f"用户输入：{text}"},
            ],
            response_format={"type": "json_object"},
        )
        payload = self._safe_json_load(raw)
        return {
            "style": str(payload.get("style", "cinematic_general")),
            "mood": str(payload.get("mood", "neutral")),
            "lighting": str(payload.get("lighting", "natural")),
            "camera_hint": str(payload.get("camera_hint", "")),
            "needs_precise_params": bool(payload.get("needs_precise_params", False)),
            "technical_hints": list(payload.get("technical_hints", [])),
            "subject": str(payload.get("subject", "角色")),
            "raw_input": str(payload.get("raw_input", text)),
        }

    def generate_prompt(self, intention_payload: Dict[str, Any]) -> str:
        return self._chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是视频提示词工程师。"
                        "请基于用户意图输出结构化 Prompt，必须包含以下段落标题："
                        "[Subject & Movement] [Camera Work] [Physics] "
                        "[Lighting] [Audio] [Temporal]。"
                        "输出必须为中文。"
                        "Temporal 段必须明确总时长，且只能在 5-15 秒范围内。"
                        "只输出最终 Prompt 文本。"
                    ),
                },
                {
                    "role": "user",
                    "content": "根据下面意图生成 Prompt：\n"
                    + json.dumps(intention_payload, ensure_ascii=False),
                },
            ]
        )

    def validate_physics(self, prompt_text: str) -> Dict[str, Any]:
        raw = self._chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是视频物理一致性审查器。"
                        "检查输入 Prompt 是否存在物理矛盾。"
                        "输出 JSON，字段必须包含 ok(布尔) 和 issues(字符串数组)。"
                        "只输出 JSON。"
                    ),
                },
                {"role": "user", "content": prompt_text},
            ],
            response_format={"type": "json_object"},
        )
        payload = self._safe_json_load(raw)
        return {
            "ok": bool(payload.get("ok", True)),
            "issues": list(payload.get("issues", [])),
        }

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        _ = image_path
        return {"summary": "image analysis not implemented in current flow"}

    def _resolve_api_key(self, private_config: Dict[str, str]) -> Optional[str]:
        env_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
        if env_key:
            return env_key

        raw_key = private_config.get("api_key", "").strip()
        if not raw_key:
            return None

        env_ref = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", raw_key)
        if env_ref:
            return os.getenv(env_ref.group(1))
        return raw_key

    def _load_private_kimi_config(self) -> Dict[str, str]:
        config_path = Path(__file__).resolve().parents[2] / "private" / "config.yaml"
        if not config_path.exists():
            return {}

        lines = config_path.read_text(encoding="utf-8").splitlines()
        in_kimi = False
        kimi_indent = -1
        result: Dict[str, str] = {}

        for line in lines:
            content = line.split("#", 1)[0].rstrip()
            if not content.strip():
                continue

            indent = len(content) - len(content.lstrip(" "))
            stripped = content.strip()
            if stripped == "kimi:":
                in_kimi = True
                kimi_indent = indent
                continue
            if in_kimi and indent <= kimi_indent:
                in_kimi = False
            if not in_kimi or ":" not in stripped:
                continue

            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key in {"api_key", "model", "base_url"}:
                result[key] = value

        return result

    def _chat_completion(
        self,
        messages: List[Dict[str, Any]],
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not self.api_key:
            raise KimiAPIError("未检测到 Kimi API Key。请设置 KIMI_API_KEY 或 MOONSHOT_API_KEY。")

        payload: Dict[str, Any] = {"model": self.model, "messages": messages}
        if response_format is not None:
            payload["response_format"] = response_format
        if self.model == "kimi-k2.5":
            payload["thinking"] = {"type": "disabled"}

        req = urllib.request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise KimiAPIError(f"Kimi API 请求失败，HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise KimiAPIError(f"Kimi API 网络错误: {exc}") from exc

        choices = data.get("choices", [])
        if not choices:
            raise KimiAPIError(f"Kimi API 返回异常：{data}")
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            text_parts: List[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(str(part.get("text", "")))
            return "".join(text_parts).strip()
        raise KimiAPIError(f"Kimi API 未返回可解析内容：{data}")

    def _safe_json_load(self, raw: str) -> Dict[str, Any]:
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise KimiAPIError(f"无法解析 JSON 输出: {raw}")
        try:
            obj = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise KimiAPIError(f"无法解析 JSON 输出: {raw}") from exc
        if not isinstance(obj, dict):
            raise KimiAPIError(f"JSON 输出不是对象: {raw}")
        return obj


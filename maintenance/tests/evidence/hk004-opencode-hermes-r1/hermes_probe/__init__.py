"""Isolated Hermes lifecycle marker; not a product plugin."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


def _summary(text: Any) -> dict[str, Any]:
    value = text if isinstance(text, str) else ""
    return {
        "chars": len(value),
        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "has_d0": "HA_D0" in value,
        "has_d1": "HA_D1" in value,
    }


def _record(event: str, **fields: Any) -> None:
    raw = os.environ.get("COW_HERMES_PROBE_DIR")
    if not raw:
        return
    root = Path(raw).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    with (root / "events.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps({"event": event, **fields}, ensure_ascii=False) + "\n")


def register(ctx: Any) -> None:
    raw_skill_root = os.environ.get("COW_HERMES_SKILL_ROOT")
    if raw_skill_root:
        skill_md = Path(raw_skill_root).expanduser().resolve() / "SKILL.md"
        ctx.register_skill(
            "chinese-official-writing",
            skill_md,
            "Current-checkout Chinese official-writing Skill used by the isolated probe.",
        )

    def transform(response_text: str, session_id: str = "", **kwargs: Any) -> str | None:
        del kwargs
        _record("transform_llm_output", session_id=session_id, response=_summary(response_text))
        if os.environ.get("COW_HERMES_PROBE_MODE") == "marker" and "HA_D0" in response_text:
            return "HA_D1"
        return None

    def after(session_id: str = "", assistant_response: str = "", **kwargs: Any) -> None:
        del kwargs
        _record("post_llm_call", session_id=session_id, response=_summary(assistant_response))

    ctx.register_hook("transform_llm_output", transform)
    ctx.register_hook("post_llm_call", after)

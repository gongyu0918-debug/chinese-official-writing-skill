from __future__ import annotations

from pathlib import Path

import harness


harness.OUT = Path(
    r"F:\Workspaces\chinese-official-writing-skill\output"
    r"\anti-ai-continuous-negation-anywhere-v1543-holdout-real"
)
harness.RUNTIME = Path(
    r"C:\Users\admin\Documents\Codex"
    r"\anti-ai-continuous-negation-anywhere-v1543-holdout-real"
)
harness.MODELS = {
    "luna": "gpt-5.6-luna",
    "qwen": "alibaba-token-plan/qwen3.8-max",
}
harness.PAIR_ORDER = {
    ("luna", 1): ["baseline", "candidate"],
    ("luna", 2): ["candidate", "baseline"],
    ("qwen", 1): ["candidate", "baseline"],
    ("qwen", 2): ["baseline", "candidate"],
}


if __name__ == "__main__":
    raise SystemExit(harness.main())

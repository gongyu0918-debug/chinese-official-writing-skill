"""Build plain Skill fixtures once per test process; never restore tracked mirrors."""
from __future__ import annotations

import atexit
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory

from maintenance.tools.sync_adapters import build_packages


@lru_cache(maxsize=1)
def generated_packages() -> Path:
    temporary = TemporaryDirectory(prefix="cow-packages-")
    atexit.register(temporary.cleanup)
    root = Path(temporary.name) / "packages"
    build_packages(root)
    return root

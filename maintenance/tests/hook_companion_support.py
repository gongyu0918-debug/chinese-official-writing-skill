from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
ASSEMBLER_PATH = ROOT / "maintenance" / "tools" / "assemble_hook_companion.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSEMBLER = load_module("cow_hook_companion_assembler", ASSEMBLER_PATH)


class HookCompanionTestMixin:
    """Build throwaway companions; no test writes into the tracked product tree."""

    def setUpHookCompanions(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.companion_temp = Path(temporary.name)
        self.companion_roots = {}
        for host in ("codex", "codebuddy", "claude-code"):
            target = self.companion_temp / host
            ASSEMBLER.assemble(host, target)
            self.companion_roots[host] = target

from __future__ import annotations

from pathlib import Path
import re
import unittest
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"
MARKDOWN_LINK_RE = re.compile(
    r'''!?\[[^\]]*\]\((?P<target><[^>]+>|[^)\s]+)(?:\s+["'].*?["'])?\)'''
)


class RepositoryReachabilityTests(unittest.TestCase):
    def test_every_canonical_reference_and_script_has_an_entrypoint(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        hook_guide = (SKILL_ROOT / "hooks/README.md").read_text(encoding="utf-8")
        entrypoints = skill + "\n" + hook_guide

        for folder in ("references", "scripts"):
            for path in (SKILL_ROOT / folder).iterdir():
                if path.is_file():
                    with self.subTest(path=path):
                        self.assertIn(path.name, entrypoints)

    def test_every_hook_markdown_and_adapter_is_linked(self) -> None:
        hook_root = SKILL_ROOT / "hooks"
        guide = (hook_root / "README.md").read_text(encoding="utf-8")
        capabilities = (hook_root / "host-capabilities.json").read_text(encoding="utf-8")
        assembler = (
            ROOT / "maintenance/tools/assemble_hook_companion.py"
        ).read_text(encoding="utf-8")
        combined = guide + "\n" + capabilities + "\n" + assembler

        for path in hook_root.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            relative = path.relative_to(hook_root).as_posix()
            if relative == "README.md":
                continue
            with self.subTest(path=relative):
                if path.name == "README.md":
                    self.assertIn(relative, guide)
                elif relative == "core/gate_stop_hook.py":
                    self.assertIn(relative, guide)
                else:
                    self.assertTrue(
                        path.name in combined or relative in combined,
                        f"unreachable Hook asset: {relative}",
                    )

    def test_package_and_maintenance_children_are_indexed(self) -> None:
        packages_index = (ROOT / "packages/README.md").read_text(encoding="utf-8")
        for directory in (ROOT / "packages").iterdir():
            if directory.is_dir():
                self.assertIn(f"`{directory.name}/`", packages_index)

        maintenance_index = (ROOT / "maintenance/README.md").read_text(encoding="utf-8")
        for directory in (ROOT / "maintenance").iterdir():
            if directory.is_dir() and directory.name != "output":
                self.assertIn(f"`{directory.name}/", maintenance_index)
        for tool in (ROOT / "maintenance/tools").iterdir():
            if tool.is_file() and tool.suffix == ".py":
                self.assertIn(f"`tools/{tool.name}`", maintenance_index)

    def test_public_readme_links_to_second_level_indexes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[兼容包索引](packages/README.md)", readme)
        self.assertIn("[维护区索引](maintenance/README.md)", readme)
        self.assertIn("[Hook 使用说明](chinese-official-writing/hooks/README.md)", readme)

    def test_spec_documents_are_indexed(self) -> None:
        spec_root = ROOT / "maintenance/specs"
        index = (spec_root / "README.md").read_text(encoding="utf-8")
        for path in spec_root.glob("*.md"):
            if path.name == "README.md":
                continue
            with self.subTest(path=path.name):
                self.assertIn(f"]({path.name})", index)

    def test_product_and_eval_clis_have_non_test_entrypoints(self) -> None:
        cli_roots = (
            SKILL_ROOT,
            ROOT / "maintenance/tools",
            ROOT / "maintenance/evals",
        )
        active_sources = [
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "maintenance/package.json",
        ]
        for base in (SKILL_ROOT, ROOT / "maintenance"):
            active_sources.extend(
                path
                for path in base.rglob("*")
                if path.is_file()
                and path.suffix.lower() in {".md", ".py", ".json"}
                and not {"tests", "evidence", "archive", "__pycache__"}.intersection(
                    path.parts
                )
            )

        for cli_root in cli_roots:
            for path in cli_root.rglob("*.py"):
                if {"tests", "evidence", "__pycache__"}.intersection(path.parts):
                    continue
                source = path.read_text(encoding="utf-8")
                if "__main__" not in source and "ArgumentParser" not in source:
                    continue
                relative = path.relative_to(ROOT).as_posix()
                search_terms = {path.name, relative}
                for prefix in ("chinese-official-writing/", "maintenance/"):
                    if relative.startswith(prefix):
                        search_terms.add(relative.removeprefix(prefix))
                incoming = []
                for entrypoint in active_sources:
                    if entrypoint == path:
                        continue
                    text = entrypoint.read_text(encoding="utf-8")
                    if any(term in text for term in search_terms):
                        incoming.append(entrypoint)
                with self.subTest(path=relative):
                    self.assertTrue(incoming, f"CLI only reachable from tests: {relative}")

    def test_active_markdown_local_links_exist(self) -> None:
        active_markdown = {
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "maintenance/README.md",
            ROOT / "maintenance/docs/待办.md",
            ROOT / "maintenance/docs/evidence/README.md",
        }
        active_markdown.update(SKILL_ROOT.rglob("*.md"))
        active_markdown.update((ROOT / "packages").rglob("*.md"))
        active_markdown.update((ROOT / "maintenance/specs").glob("*.md"))

        for document in sorted(active_markdown):
            text = document.read_text(encoding="utf-8")
            for match in MARKDOWN_LINK_RE.finditer(text):
                raw_target = match.group("target").strip("<>")
                if raw_target.startswith(("#", "http://", "https://", "mailto:", "data:")):
                    continue
                local_target = unquote(raw_target.split("#", 1)[0])
                if not local_target:
                    continue
                resolved = (document.parent / local_target).resolve()
                with self.subTest(document=document.relative_to(ROOT), target=raw_target):
                    self.assertTrue(resolved.exists(), f"broken link: {raw_target}")


if __name__ == "__main__":
    unittest.main()

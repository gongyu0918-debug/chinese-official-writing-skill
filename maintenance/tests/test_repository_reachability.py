from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"


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


if __name__ == "__main__":
    unittest.main()

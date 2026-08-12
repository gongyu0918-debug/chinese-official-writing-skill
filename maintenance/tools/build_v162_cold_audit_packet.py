#!/usr/bin/env python3
"""Build a self-contained v1.6.0-to-v1.6.2 product cold-audit packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = "0f6ec603993d5595e784fa7079837e299d1b0da3"
CANDIDATE_COMMIT = "0d53b3656e351020600b3754d1fe06ff2fc26ddd"
PATCH_PATHS = (
    "chinese-official-writing",
    "README.md",
    "AGENTS.md",
    "LICENSE",
    "packages/README.md",
    "packages/agent-skills/README.md",
    "packages/qwen-code/README.md",
    "packages/hermes/README.md",
    "packages/openclaw/README.md",
    "maintenance/tools/assemble_hook_companion.py",
    "maintenance/tools/build_skillhub_package.py",
    "maintenance/tools/sync_adapters.py",
    "maintenance/tests/test_hook_layer_contract.py",
    "maintenance/tests/test_repository_reachability.py",
    "maintenance/tests/test_complexity_contract.py",
    "maintenance/tests/test_gate_stop_hook.py",
    "maintenance/tests/test_host_gate_adapter.py",
    "maintenance/tests/test_claude_gate_adapter.py",
    "maintenance/tests/test_skill_boundary.py",
)
ENGINEERING_RESULT = ROOT / "maintenance/tests/evidence/v162-hook-architecture-engineering-result-20260812.md"
WRITING_TECHNICAL_RESULT = ROOT / "maintenance/tests/evidence/v162-hook-writing-real-ab-technical-result-20260812.md"


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=True
    )
    return completed.stdout.decode("utf-8", errors="replace")


def build_packet() -> str:
    shortstat = git("diff", "--shortstat", BASE_COMMIT, CANDIDATE_COMMIT).strip()
    dirstat = git("diff", "--dirstat=files,0", BASE_COMMIT, CANDIDATE_COMMIT).strip()
    names = git("diff", "--name-status", "--find-renames", BASE_COMMIT, CANDIDATE_COMMIT).strip()
    patch = git("diff", "--find-renames", BASE_COMMIT, CANDIDATE_COMMIT, "--", *PATCH_PATHS).strip()
    engineering = ENGINEERING_RESULT.read_text(encoding="utf-8").strip()
    writing = WRITING_TECHNICAL_RESULT.read_text(encoding="utf-8").strip()
    return f"""# v1.6.0 -> v1.6.2 product cold-audit packet

## 审计任务

这是非匿名产品 DIFF 冷审。固定基线 `{BASE_COMMIT}`，固定候选 `{CANDIDATE_COMMIT}`。请区分：

1. 纯目录迁移、镜像去重、文档与许可证变化；
2. canonical 写作行为变化；
3. 可选 Hook 的能力、适配、知情同意、任务关闭和无 Hook 闭环；
4. 新增新闻/新闻评论能力；
5. 孤儿脚本、孤儿叶子、断链、魔法数字、大字典、上帝函数；
6. 用户可见 README 是否混入维护口令、内部思考、候选范围或过度承诺；
7. 是否误带篇幅补写 Hook；
8. 真实写稿技术结果是否足以支持产品文案。

只报告 packet 可复现的 P0/P1/P2。每项必须给具体文件/补丁证据、影响和最小修复；不能把历史 evidence 的旧结论、路径迁移本身或已登记债务直接当新回归。没有可复现问题时明确 PASS。不得调用工具或读取外部文件。

## 完整仓库差异摘要

`{shortstat}`

### 目录占比

```text
{dirstat}
```

### 全部 940 条 name-status 路径

下列清单覆盖全部仓库差异；历史 evidence 与重复平台镜像的逐字内容不在后续补丁中重复，但路径没有省略。

```text
{names}
```

## 产品与关键工程逐字补丁

补丁覆盖 canonical 全部文件、公开 README/AGENTS/LICENSE、包索引/说明、Hook assembler、SkillHub builder、镜像同步和关键边界测试。平台镜像正文由 canonical 生成，因此不重复塞入同字节补丁。

```diff
{patch}
```

## 已冻结工程结果

{engineering}

## 已冻结真实写稿技术结果

{writing}

## 裁判输出格式

只输出一个 JSON 对象，不要 Markdown：

{{
  "verdict": "PASS|HOLD",
  "findings": [
    {{"severity":"P0|P1|P2","title":"","location":"","evidence":"","impact":"","minimal_fix":""}}
  ],
  "confirmed_boundaries": {{
    "no_length_hook": true,
    "no_hook_closed_loop": true,
    "task_opt_out": true,
    "static_consent_first_adapters": true,
    "news_and_commentary": true
  }},
  "overclaim_risks": [],
  "migration_only_observations": [],
  "summary": ""
}}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_packet(), encoding="utf-8", newline="\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

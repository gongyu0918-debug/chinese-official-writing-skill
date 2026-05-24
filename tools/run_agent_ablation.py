#!/usr/bin/env python3
"""Run a model-agnostic three-agent ablation for the Chinese official-writing Skill.

Agent A: writer with the installed Skill available.
Agent B: writer without Skill instructions.
Agent C: independent evaluator comparing A/B outputs against public
official-document style profiles.

Raw generated drafts are written under output/ and are ignored by git.
Only sanitized aggregate evidence should be copied into tests/evidence/.
Set OFFICIAL_WRITING_AGENT_COMMAND to the current agent or model command.
Include {prompt} in the command template or the prompt will be appended as the
final argument.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import textwrap
import time


GENRES = [
    "通知",
    "请示",
    "报告",
    "说明",
    "方案",
    "申请",
    "函",
    "复函",
    "批复",
    "意见",
    "决定",
    "公告",
    "公示",
    "通报",
    "会议纪要",
    "工作要点",
    "工作总结",
    "调研报告",
    "可研报告",
    "实施方案",
    "建设方案",
    "审查材料",
    "算力服务可研报告",
    "算力资源采购方案",
    "GPU/服务器租赁技术需求",
    "云端部署成本对比说明",
    "技术服务审查材料",
]


SCENARIOS = [
    "报送材料",
    "专项启动",
    "阶段进展",
    "情况补充",
    "协同联调",
    "年度安排",
    "整改复核",
    "征求意见",
    "验收归档",
    "运行优化",
]


PUBLIC_STYLE_PROFILES = """
# Public Official-Document Style Reference Profiles

These profiles are distilled from public Chinese official-document examples and
format guidance. They do not quote raw source text.

Sources used as style anchors include:
- State Council and ministry public notices, implementation plans, and work reports from gov.cn.
- Public local-government notices, announcements, circulars, and meeting materials.
- Public official-document writing guidance based on GB/T 9704-2012.
- Public procurement and computing-resource service documents used only for generic technical writing patterns.

Common reference traits:
- Notices and announcements state the matter early, then list addressee, deadline, material, channel, and contact requirements.
- Requests for instructions keep one main requested matter, state the basis and need, and end with a formal request for approval.
- Reports state facts and progress without inserting approval requests.
- Letters and replies keep an equal, concise tone and specify the matter, feedback deadline, and coordination requirements.
- Meeting minutes record agreed matters, responsibility division, and follow-up arrangements.
- Plans and implementation plans use goal, task, schedule, responsibility, safeguard, and acceptance logic.
- Feasibility, construction, review, procurement, and AI-compute materials need a clear chain: demand source -> usage or Token/resource calculation -> cost comparison -> service/SLA/security/acceptance requirements.
"""


def external_cmd(prompt: str) -> list[str]:
    template = (
        os.environ.get("OFFICIAL_WRITING_AGENT_COMMAND")
        or os.environ.get("OFFICIAL_WRITING_EVAL_COMMAND")
        or ""
    ).strip()
    if not template:
        raise FileNotFoundError("OFFICIAL_WRITING_AGENT_COMMAND is not set")
    tokens = shlex.split(template, posix=os.name != "nt")
    replacements = {
        "{prompt}": prompt,
        "{prompt_json}": json.dumps(prompt, ensure_ascii=False),
    }
    has_placeholder = any(marker in token for token in tokens for marker in replacements)
    if has_placeholder:
        return [
            token.replace("{prompt}", replacements["{prompt}"]).replace("{prompt_json}", replacements["{prompt_json}"])
            for token in tokens
        ]
    return [*tokens, prompt]


def task_list_for_genres(genres: list[str]) -> list[tuple[str, str, str]]:
    tasks: list[tuple[str, str, str]] = []
    for genre in genres:
        for index, scenario in enumerate(SCENARIOS, start=1):
            task_id = f"T{len(tasks) + 1:03d}"
            if "算力" in genre or "GPU" in genre or "云端" in genre or "技术服务" in genre:
                prompt = (
                    f"【{genre}】场景为{scenario}。写一段正式材料节选，"
                    "需体现 Token 或资源需求、云端成本、租赁服务、SLA、并发、安全或验收中的至少三项。"
                )
            else:
                prompt = f"【{genre}】场景为{scenario}。写一段正式公文或工作材料节选，事项要清楚，语气要正式。"
            tasks.append((task_id, genre, prompt))
    return tasks


def render_tasks(tasks: list[tuple[str, str, str]]) -> str:
    return "\n".join(f"{task_id}: {prompt}" for task_id, _genre, prompt in tasks)


def read_file(path: Path, max_chars: int = 12000) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n[truncated]\n"


def load_skill_context(cwd: Path, genres: list[str]) -> str:
    skill_dir = cwd / ".agents" / "skills" / "chinese-official-writing"
    parts = [
        ("SKILL.md", read_file(skill_dir / "SKILL.md", 9000)),
        ("references/genre-checklist.md", read_file(skill_dir / "references" / "genre-checklist.md", 9000)),
        ("references/anti-ai-patterns.md", read_file(skill_dir / "references" / "anti-ai-patterns.md", 7000)),
    ]
    if any("算力" in genre or "GPU" in genre or "云端" in genre or "技术服务" in genre for genre in genres):
        parts.append(("references/ai-compute-docs.md", read_file(skill_dir / "references" / "ai-compute-docs.md", 10000)))
    return "\n\n".join(f"## {name}\n{text}" for name, text in parts)


def skill_prompt(tasks: list[tuple[str, str, str]], cwd: Path) -> str:
    genres = sorted({genre for _task_id, genre, _prompt in tasks})
    skill_context = load_skill_context(cwd, genres)
    return textwrap.dedent(
        f"""
        You are Writer A. The repository has the Skill installed at
        `.agents/skills/chinese-official-writing/`.

        Use the installed Skill instructions and references below. Follow them as
        drafting rules, not as text to copy. Do not output explanations of the Skill.

        Draft exactly one compact Chinese paragraph for each task below, 100-180 Chinese characters per task.
        Do not invent real organizations, real policies, real amounts, names,
        phone numbers, emails, or internal project facts.
        Output format:
        ### A-<task id>
        <draft>

        Installed Skill context:
        ```text
        {skill_context}
        ```

        Tasks:
        {render_tasks(tasks)}
        """
    ).strip()


def baseline_prompt(tasks: list[tuple[str, str, str]]) -> str:
    return textwrap.dedent(
        f"""
        You are Writer B. Do not read or use any Skill, checklist,
        repository file, or special drafting constraint. Draft from the simple
        prompts only, using your normal writing habits.

        Draft exactly one compact Chinese paragraph for each task below, 100-180 Chinese characters per task.
        Do not invent real organizations, real policies, real amounts, names,
        phone numbers, emails, or internal project facts.
        Output format:
        ### B-<task id>
        <draft>

        Tasks:
        {render_tasks(tasks)}
        """
    ).strip()


def evaluator_prompt(tasks: list[tuple[str, str, str]], a_text: str, b_text: str) -> str:
    return textwrap.dedent(
        f"""
        You are Evaluator C. You have no access to the writer contexts.
        Evaluate Writer A and Writer B independently against the public official-document
        style profiles below. Do not modify files and do not infer any real facts.

        For each genre in this batch, decide whether A, B, or Tie is closer to
        public Chinese official-document style. Focus on genre fit, viewpoint,
        paragraph logic, official tone, anti-AI wording, and for AI-compute texts:
        demand -> Token/resource -> cost -> SLA/security/acceptance logic.

        Return:
        ## Answer
        - aggregate winner by genre
        - overall winner count
        - whether the ablation supports Skill effectiveness
        ## Evidence
        - concise evidence by dimension
        ## Uncertainty
        - limitations and risks
        ## Suggested Codex Checks
        - checks needed before publishing the evidence

        {PUBLIC_STYLE_PROFILES}

        ## Task List
        {render_tasks(tasks)}

        ## Writer A Output
        {a_text}

        ## Writer B Output
        {b_text}
        """
    ).strip()


def call_external(prompt: str, cwd: Path, timeout: int, out_path: Path, retries: int = 0) -> int:
    output = ""
    return_code = 4
    for attempt in range(retries + 1):
        result = subprocess.run(
            external_cmd(prompt),
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output = output.rstrip() + "\n\n[stderr]\n" + result.stderr
        return_code = result.returncode
        if output.strip() or return_code != 0:
            break
        time.sleep(2 + attempt)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    if not output.strip() and return_code == 0:
        return 4
    return return_code


def parse_winner_counts(review_texts: list[str]) -> dict[str, int]:
    counts = {"A": 0, "B": 0, "Tie": 0}
    combined = "\n".join(review_texts)
    for key in counts:
        patterns = [
            rf"{key}\s*[:：]\s*(\d+)",
            rf"{key}\s*胜\s*(\d+)",
            rf"{key}\s*获胜\s*(\d+)",
            rf"\b{key}\b\s+(\d+)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, combined, flags=re.IGNORECASE):
                counts[key] += int(match.group(1))
    return counts


def write_summary(out_dir: Path, evidence_path: Path, genres: list[str], review_files: list[Path], started: float) -> bool:
    reviews = [path.read_text(encoding="utf-8", errors="replace") for path in review_files if path.exists()]
    counts = parse_winner_counts(reviews)
    batch_dirs = sorted(path for path in out_dir.glob("batch-*") if path.is_dir())
    task_genres: set[str] = set()
    task_total = 0
    for batch_dir in batch_dirs:
        task_path = batch_dir / "tasks.md"
        if not task_path.exists():
            continue
        task_lines = [line for line in task_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
        task_total += len(task_lines)
        for line in task_lines:
            match = re.search(r"【([^】]+)】", line)
            if match:
                task_genres.add(match.group(1))
    genre_total = len(task_genres) if task_genres else len(genres)
    task_total = task_total if task_total else len(genres) * len(SCENARIOS)
    valid_writer_batches = 0
    valid_review_batches = 0
    invalid_notes: list[str] = []
    for batch_dir in batch_dirs:
        task_path = batch_dir / "tasks.md"
        expected = len(task_path.read_text(encoding="utf-8", errors="replace").splitlines()) if task_path.exists() else len(SCENARIOS)
        a_path = batch_dir / "writer-a-skill.md"
        b_path = batch_dir / "writer-b-baseline.md"
        c_path = batch_dir / "evaluator-c-review.md"
        a_count = len(re.findall(r"^###\s+A", a_path.read_text(encoding="utf-8", errors="replace"), re.M)) if a_path.exists() else 0
        b_count = len(re.findall(r"^###\s+B", b_path.read_text(encoding="utf-8", errors="replace"), re.M)) if b_path.exists() else 0
        c_ok = c_path.exists() and bool(c_path.read_text(encoding="utf-8", errors="replace").strip())
        if a_count == expected and b_count == expected:
            valid_writer_batches += 1
        else:
            invalid_notes.append(f"- {batch_dir.name}: Writer A={a_count}/{expected}, Writer B={b_count}/{expected}")
        if c_ok:
            valid_review_batches += 1
        else:
            invalid_notes.append(f"- {batch_dir.name}: Evaluator C returned empty output")
    elapsed = time.time() - started
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        "\n".join(
            [
                "# Model-Agnostic A/B/C Ablation Summary",
                "",
                "本文件只记录脱敏评估结论，不包含用户材料、内部文件内容、个人信息或原始公开公文全文。",
                "",
                "## 测试设计",
                "",
                f"- 覆盖文体：{genre_total} 类。",
                f"- 每类任务：{len(SCENARIOS)} 次。",
                f"- 总任务数：{task_total} 个。",
                "- Writer A：当前 agent 或指定模型在已安装 `chinese-official-writing` Skill 的条件下生成样稿。",
                "- Writer B：当前 agent 或指定模型不读取 Skill，仅按普通提示生成样稿。",
                "- Evaluator C：独立上下文仅根据 A/B 输出和公开公文风格参照进行评估。",
                "- 公开原稿处理：发布包不保存原文，只保存脱敏后的风格参照和聚合评估结论。",
                "",
                "## 运行结果",
                "",
                f"- 评估批次数：{len(review_files)}。",
                f"- A/B 写稿有效批次：{valid_writer_batches}/{len(batch_dirs)}。",
                f"- C 独立评估有效批次：{valid_review_batches}/{len(batch_dirs)}。",
                f"- 运行耗时：{elapsed:.1f} 秒。",
                f"- 自动解析胜出计数：A={counts['A']}，B={counts['B']}，Tie={counts['Tie']}。该计数仅从评估文本中抽取，最终以人工复核为准。",
                "",
                "## 无效或需补评批次",
                "",
                "\n".join(invalid_notes) if invalid_notes else "- 未发现空返回或缺项批次。",
                "",
                "## 原始输出位置",
                "",
                f"- 原始 A/B/C 输出保存在 `{out_dir.as_posix()}`，该目录被 `.gitignore` 排除，不进入发布包。",
                "",
                "## 复核结论",
                "",
                "Evaluator C 的独立评估用于验证 Skill 是否改善文种适配、视角控制、公文语气、反 AI 句式和算力类论证链条。"
                "该测试不能替代人工审稿，也不代表具体事实、政策依据、金额或采购结论已经通过业务审核。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return valid_writer_batches == len(batch_dirs) and valid_review_batches == len(batch_dirs)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="output/agent-public-ablation")
    parser.add_argument("--evidence", default="tests/evidence/agent-public-ablation-summary.md")
    parser.add_argument("--genres-per-batch", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=420)
    parser.add_argument("--only-first-batch", action="store_true")
    parser.add_argument("--summarize-only", action="store_true")
    args = parser.parse_args()

    cwd = Path.cwd()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    review_files: list[Path] = []
    selected_genres = GENRES[: args.genres_per_batch] if args.only_first_batch else GENRES

    if args.summarize_only:
        review_files = sorted(Path(args.out).glob("batch-*/evaluator-c-review.md"))
        ok = write_summary(out_dir, Path(args.evidence), selected_genres, review_files, started)
        print(f"summary written: {args.evidence}")
        return 0 if ok else 1

    for batch_index, start in enumerate(range(0, len(selected_genres), args.genres_per_batch), start=1):
        genres = selected_genres[start : start + args.genres_per_batch]
        tasks = task_list_for_genres(genres)
        batch_dir = out_dir / f"batch-{batch_index:02d}"
        task_path = batch_dir / "tasks.md"
        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(render_tasks(tasks), encoding="utf-8")

        a_path = batch_dir / "writer-a-skill.md"
        b_path = batch_dir / "writer-b-baseline.md"
        c_path = batch_dir / "evaluator-c-review.md"
        print(f"batch {batch_index}: genres={','.join(genres)} tasks={len(tasks)}")
        a_code = call_external(skill_prompt(tasks, cwd), cwd, args.timeout_seconds, a_path, retries=1)
        b_code = call_external(baseline_prompt(tasks), cwd, args.timeout_seconds, b_path, retries=1)
        a_text = a_path.read_text(encoding="utf-8", errors="replace")
        b_text = b_path.read_text(encoding="utf-8", errors="replace")
        c_code = call_external(evaluator_prompt(tasks, a_text, b_text), cwd, args.timeout_seconds, c_path, retries=2)
        review_files.append(c_path)
        print(f"batch {batch_index}: A={a_code} B={b_code} C={c_code}")

    ok = write_summary(out_dir, Path(args.evidence), selected_genres, review_files, started)
    print(f"summary written: {args.evidence}")
    return 0 if ok else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())

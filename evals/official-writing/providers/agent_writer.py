#!/usr/bin/env python3
"""Promptfoo Python providers for official-writing ablation evals.

The provider has two modes:
- baseline: draft from the task only.
- skill: load the installed Skill entrypoint plus genre-specific references.

By default the provider uses deterministic local drafts so tests can run in
any agent without a model-specific CLI. Set OFFICIAL_WRITING_AGENT_COMMAND to
use the current agent or any model command; include {prompt} in the command
template or the prompt will be appended as the final argument.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import textwrap
import time
from typing import Any


GENRE_REFERENCES: dict[str, list[str]] = {
    "sparse": [
        "references/task-route-cards.md",
    ],
    "routing": [
        "references/genre-routing.md",
    ],
    "review": [
        "references/review-checklist.md",
    ],
    "anti_ai": [
        "references/anti-ai-patterns.md",
    ],
    "style": [
        "references/official-style.md",
    ],
    "argument": [
        "references/argument-chains.md",
    ],
    "playbook": [
        "references/genre-playbooks.md",
    ],
    "ai_compute": [
        "references/ai-compute-docs.md",
    ],
    "complex": [
        "references/workflow.md",
        "references/handling-elements.md",
    ],
    "format": [
        "references/format-gbt9704.md",
    ],
}

MAX_SKILL_CONTEXT_CHARS = 50_000
DEFAULT_TIMEOUT_SECONDS = 720

CHAIN_GENRES = {
    "请示",
    "报告",
    "通知",
    "函",
    "复函",
    "征求意见函",
    "采购公告",
    "公示",
    "批复",
    "会议纪要",
    "方案",
    "意见",
    "工作要点",
    "工作总结",
    "调研报告",
    "可研报告",
    "实施方案",
    "建设方案",
    "审查材料",
    "说明",
    "情况说明",
    "申请",
}

PLAYBOOK_GENRES = CHAIN_GENRES | {
    "通告",
    "公告",
    "通报",
    "决定",
    "决议",
    "议案",
    "公报",
    "命令",
    "命令（令）",
    "讲话稿",
    "致辞",
    "述职报告",
    "研究报告",
}

COMPLEX_TASK_MARKERS = (
    "完整文种骨架",
    "完整结构",
    "复杂改稿",
    "多材料",
    "多附件",
    "合稿",
    "长文",
)
FORMAT_TASK_MARKERS = ("Word", "word", "DOCX", "docx", "GB/T 9704", "红头", "版记")
LONG_FORM_RE = re.compile(r"(?<!\d)(\d{3,5})\s*字")

AI_COMPUTE_MARKERS = (
    "算力",
    "GPU",
    "模型服务",
    "智算中心",
    "AI平台",
    "AI 平台",
    "大模型",
    "Token",
    "模型推理",
    "推理服务",
    "模型训练",
    "训练服务",
)

AI_COMPUTE_EXACT_GENRES = {
    "算力服务可研报告",
    "算力资源采购方案",
    "GPU/服务器租赁技术需求",
}

AI_NEGATION_MARKERS = (
    "不涉及AI",
    "不涉及 AI",
    "非AI",
    "非 AI",
    "与AI无关",
    "与 AI 无关",
    "不用于AI",
    "不用于 AI",
)

SPARSE_CARD_GENRES = {"通知", "报告", "情况说明", "说明", "通报", "会议纪要"}
SPARSE_TASK_MARKERS = (
    "材料只有",
    "只按已给",
    "不新增事实",
    "不要新增事实",
    "只给",
    "只保留",
    "简短",
    "短稿",
    "未决",
    "未形成",
    "局部修改",
    "只改",
    "补一句",
)
REVIEW_TASK_MARKERS = (
    "只审",
    "审一下",
    "只检查",
    "检查这段",
    "检查这份",
    "格式核验",
    "语气检查",
    "复核这段",
    "复核这份",
)
REVIEW_REWRITE_MARKERS = (
    "再按建议重写",
    "再重写",
    "然后重写",
    "并重写",
    "同时重写",
    "审后重写",
    "输出改后稿",
    "修改并输出",
    "改写成",
    "修改全文",
    "修改正文",
    "直接改",
    "代改",
    "输出修改稿",
    "输出改稿",
    "给出改后稿",
)
REVIEW_REWRITE_ACTION_RE = re.compile(
    r"(?:"
    r"改写(?:成|为|全文|正文|一版)|"
    r"重写(?:全文|正文|一版)|"
    r"改一版|改成|改好|修改全文|修改正文|代改|"
    r"(?:请|并|再|然后|同时|直接|帮我|代为|给我|后帮我)[^，。；;\n]{0,6}(?:重写|改写)"
    r")"
)
REVIEW_REWRITE_NEGATIONS = (
    "不重写",
    "不要重写",
    "不改写",
    "不要改写",
    "不修改",
    "不要修改",
    "不代改",
    "不要代改",
    "不输出修改稿",
    "不要输出修改稿",
    "不输出改后稿",
    "不要输出改后稿",
    "只给修改建议",
    "仅给修改建议",
    "修改建议",
)
ANTI_AI_TASK_MARKERS = ("AI 味", "AI味", "降 AI 味", "降AI味", "模板化", "空话套话")
STYLE_TASK_MARKERS = ("去口语化", "降 AI 味", "降AI味", "润色", "正式一点", "统一语气", "顺稿")
ROUTING_TASK_MARKERS = ("文种不清", "判断文种", "选择文种", "请示还是报告", "函还是通知")
ARGUMENT_TASK_MARKERS = ("论证", "可行性", "必要性", "方案比较", "成本比较")

_BATCH_CACHE: dict[str, dict[str, str]] = {}


class ProviderError(RuntimeError):
    pass


def _options_config(options: dict[str, Any]) -> dict[str, Any]:
    config = options.get("config") or {}
    if not isinstance(config, dict):
        return {}
    return config


def _base_path(config: dict[str, Any]) -> Path:
    base_path = config.get("basePath")
    if base_path:
        return Path(str(base_path)).resolve()
    return Path(__file__).resolve().parents[1]


def _repo_root(config: dict[str, Any]) -> Path:
    configured = config.get("repoRoot")
    if configured:
        return (_base_path(config) / str(configured)).resolve()
    return _base_path(config).parents[1]


def _dataset_path(config: dict[str, Any]) -> Path:
    configured = config.get("datasetPath", "datasets/cases.jsonl")
    return (_base_path(config) / str(configured)).resolve()


def _cache_dir(config: dict[str, Any]) -> Path:
    repo_root = _repo_root(config)
    return repo_root / "output" / "promptfoo" / "cache"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _load_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for line in _dataset_path(config).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        vars_ = item.get("vars") or {}
        metadata = item.get("metadata") or {}
        case = {
            "description": item.get("description", vars_.get("case_id", "")),
            "vars": vars_,
            "metadata": metadata,
        }
        cases.append(case)

    limit_text = os.environ.get("OFFICIAL_WRITING_EVAL_LIMIT", "").strip()
    if limit_text:
        try:
            limit = int(limit_text)
        except ValueError as exc:
            raise ProviderError(f"OFFICIAL_WRITING_EVAL_LIMIT must be an integer: {limit_text}") from exc
        cases = cases[:limit]
    return cases


def _current_case(context: dict[str, Any]) -> dict[str, Any]:
    vars_ = context.get("vars") or {}
    test = context.get("test") or {}
    return {
        "description": test.get("description", vars_.get("case_id", "")),
        "vars": vars_,
        "metadata": test.get("metadata") or {},
    }


def _contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _is_ai_compute(genre: str, tasks: list[str] | None = None) -> bool:
    if genre in AI_COMPUTE_EXACT_GENRES:
        return True
    text = "\n".join([genre, *(tasks or [])])
    original_folded = text.casefold()
    negative_clause = re.compile(
        r"(?:不涉及|不用于)[^。；;\n]*?(?=(?:，?(?:但|不过|然而|可是|而是|却|仍需|同时|另需|仅涉及))|[。；;\n]|$)",
        re.I,
    )
    text = negative_clause.sub("", text)
    text = re.sub(r"非\s*AI[^，。；;\n]*", "", text, flags=re.I)
    for marker in AI_NEGATION_MARKERS:
        text = text.replace(marker, "")
    folded = text.casefold()
    if any(marker.casefold() in folded for marker in AI_COMPUTE_MARKERS):
        return True
    if any(marker.casefold() in original_folded for marker in AI_NEGATION_MARKERS):
        return False
    return all(marker in text for marker in ("云端", "本地", "部署"))


def _skill_root(repo_root: Path) -> Path:
    installed = repo_root / ".agents" / "skills" / "chinese-official-writing"
    if installed.exists():
        return installed
    return repo_root / "chinese-official-writing"


def _task_requires_complex_route(tasks: list[str]) -> bool:
    if any(marker in task for task in tasks for marker in COMPLEX_TASK_MARKERS):
        return True
    return any(int(match.group(1)) >= 800 for task in tasks for match in LONG_FORM_RE.finditer(task))


def _tasks_are_review_only(tasks: list[str]) -> bool:
    def requests_rewrite(task: str) -> bool:
        normalized = task
        for marker in REVIEW_REWRITE_NEGATIONS:
            normalized = normalized.replace(marker, "")
        return _contains_marker(normalized, REVIEW_REWRITE_MARKERS) or bool(
            REVIEW_REWRITE_ACTION_RE.search(normalized)
        )

    return bool(tasks) and all(
        _contains_marker(task, REVIEW_TASK_MARKERS)
        and not requests_rewrite(task)
        for task in tasks
    )


def _task_uses_sparse_card(genres: list[str], tasks: list[str], ai_compute: bool) -> bool:
    if ai_compute or _task_requires_complex_route(tasks):
        return False
    if not tasks:
        return not any(genre in PLAYBOOK_GENRES for genre in genres)
    if not any(genre in SPARSE_CARD_GENRES for genre in genres):
        return False
    return all(_contains_marker(task, SPARSE_TASK_MARKERS) for task in tasks)


def _reference_paths_for_genres(genres: list[str], tasks: list[str] | None = None) -> list[str]:
    tasks = tasks or []
    paths = ["SKILL.md"]
    ai_compute = any(_is_ai_compute(genre, tasks) for genre in genres)

    if _tasks_are_review_only(tasks):
        paths.extend(GENRE_REFERENCES["review"])
        if any(_contains_marker(task, ANTI_AI_TASK_MARKERS) for task in tasks):
            paths.extend(GENRE_REFERENCES["anti_ai"])
        if any(marker in task for task in tasks for marker in FORMAT_TASK_MARKERS):
            paths.extend(GENRE_REFERENCES["format"])
        return list(dict.fromkeys(paths))

    sparse_route = _task_uses_sparse_card(genres, tasks, ai_compute)
    if sparse_route:
        paths.extend(GENRE_REFERENCES["sparse"])
        if "会议纪要" in genres:
            # v1.5.13 同时要求稀疏材料先读轻卡、会议纪要再转长 reference；
            # 在产品路由冲突获批修订前，评测必须如实保留两段读取。
            paths.extend(GENRE_REFERENCES["playbook"])
    else:
        if any(genre in PLAYBOOK_GENRES or _is_ai_compute(genre, tasks) for genre in genres):
            paths.extend(GENRE_REFERENCES["playbook"])
        if any(_contains_marker(task, ROUTING_TASK_MARKERS) for task in tasks):
            paths.extend(GENRE_REFERENCES["routing"])

    complex_route = _task_requires_complex_route(tasks)
    argument_requested = any(_contains_marker(task, ARGUMENT_TASK_MARKERS) for task in tasks)
    if complex_route:
        paths.extend(GENRE_REFERENCES["complex"])
        if any(genre in CHAIN_GENRES for genre in genres) or ai_compute or argument_requested:
            paths.extend(GENRE_REFERENCES["argument"])
    elif argument_requested:
        paths.extend(GENRE_REFERENCES["argument"])

    if any(_contains_marker(task, STYLE_TASK_MARKERS) for task in tasks):
        paths.extend(GENRE_REFERENCES["style"])
    if ai_compute:
        paths.extend(GENRE_REFERENCES["ai_compute"])
    if any(marker in task for task in tasks for marker in FORMAT_TASK_MARKERS):
        paths.extend(GENRE_REFERENCES["format"])

    seen: set[str] = set()
    ordered: list[str] = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            ordered.append(path)
    return ordered


def _load_skill_context_from_paths(repo_root: Path, reference_paths: list[str]) -> str:
    root = _skill_root(repo_root)
    parts: list[str] = []
    for relative in reference_paths:
        path = root / relative
        if not path.exists():
            raise ProviderError(f"selected skill reference does not exist: {path}")
        parts.append(f"## {relative}\n{_read_text(path)}")
    context = "\n\n".join(parts)
    if len(context) > MAX_SKILL_CONTEXT_CHARS:
        raise ProviderError(
            f"selected skill context exceeds {MAX_SKILL_CONTEXT_CHARS} characters: {len(context)}"
        )
    return context


def _load_skill_context(repo_root: Path, genres: list[str], tasks: list[str] | None = None) -> str:
    return _load_skill_context_from_paths(repo_root, _reference_paths_for_genres(genres, tasks))


def _case_id(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("case_id", "")).strip()


def _case_genre(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("genre", "")).strip()


def _case_task(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("task", "")).strip()


def _case_reference_paths(case: dict[str, Any]) -> list[str]:
    genre = _case_genre(case)
    task = _case_task(case)
    return _reference_paths_for_genres([genre] if genre else [], [task] if task else [])


def _reference_paths_for_cases(cases: list[dict[str, Any]]) -> list[str]:
    paths: list[str] = []
    for case in cases:
        paths.extend(_case_reference_paths(case))
    return list(dict.fromkeys(paths))


def _skill_batch_reference_paths(cases: list[dict[str, Any]]) -> list[str]:
    signatures = {tuple(_case_reference_paths(case)) for case in cases}
    if not signatures:
        raise ProviderError("cannot build a skill prompt without cases")
    if len(signatures) != 1:
        raise ProviderError("skill batch contains mixed reference routes")
    return list(next(iter(signatures)))


def _render_tasks(cases: list[dict[str, Any]]) -> str:
    return "\n".join(f"{_case_id(case)}: {_case_task(case)}" for case in cases)


def _baseline_prompt(cases: list[dict[str, Any]]) -> str:
    return textwrap.dedent(
        f"""
        你是中文正式材料写作助手。请不要读取或使用任何仓库文件、Skill、清单或模板，只依据下面任务写作。

        对每个任务输出一段中文正式材料初稿，控制在 160-260 个汉字。不要编造真实单位、真实政策、真实金额、
        人名、电话、邮箱或内部项目事实。可使用“有关单位”“相关部门”等泛称，但不要把“发文机关、
        发文字号、主送单位”等占位标签写进正文。

        输出必须严格按如下格式，不要解释：
        ### <case_id>
        <正文>

        任务：
        {_render_tasks(cases)}
        """
    ).strip()


def _skill_prompt(cases: list[dict[str, Any]], config: dict[str, Any]) -> str:
    repo_root = _repo_root(config)
    tasks = [_case_task(case) for case in cases if _case_task(case)]
    reference_paths = _skill_batch_reference_paths(cases)
    skill_context = _load_skill_context_from_paths(repo_root, reference_paths)
    if _tasks_are_review_only(tasks):
        delivery_instruction = (
            "按用户指定范围输出审稿结论；只审不改时不得重写全文，也不受初稿篇幅要求约束。"
        )
    else:
        delivery_instruction = (
            "按用户指定的文种、输出模式和篇幅要求交付；任务未指定篇幅时，正文控制在 160-260 个汉字。"
        )
    return textwrap.dedent(
        f"""
        你是中文公文 Skill 写作代理。仓库已安装 Skill：
        `.agents/skills/chinese-official-writing/SKILL.md`。

        只使用下列 Skill 入口和本批任务已选中的 references；不要加载整包上下文，不要复制参考资料原文，
        也不要自行扩展到未选中的 reference 路线。{delivery_instruction}

        不要编造真实单位、真实政策、真实金额、
        人名、电话、邮箱或内部项目事实。可使用“有关单位”“相关部门”等泛称，但不要把“发文机关、
        发文字号、主送单位”等占位标签写进正文。

        输出必须严格按如下格式，不要解释：
        ### <case_id>
        <正文或审稿结果>

        Skill context:
        ```text
        {skill_context}
        ```

        任务：
        {_render_tasks(cases)}
        """
    ).strip()


def _single_prompt(mode: str, case: dict[str, Any], config: dict[str, Any]) -> str:
    if mode == "skill":
        return _skill_prompt([case], config)
    return _baseline_prompt([case])


def _agent_command_template(config: dict[str, Any] | None = None) -> str:
    config = config or {}
    return str(
        config.get("commandTemplate")
        or os.environ.get("OFFICIAL_WRITING_AGENT_COMMAND")
        or os.environ.get("OFFICIAL_WRITING_EVAL_COMMAND")
        or ""
    ).strip()


def _truthy_env(name: str) -> bool | None:
    value = os.environ.get(name)
    if value is None:
        return None
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _use_stub(config: dict[str, Any] | None = None) -> bool:
    explicit = _truthy_env("OFFICIAL_WRITING_EVAL_STUB")
    if explicit is not None:
        return explicit
    return not _agent_command_template(config)


def use_stub(config: dict[str, Any] | None = None) -> bool:
    return _use_stub(config)


def _agent_cmd(prompt: str, config: dict[str, Any] | None = None) -> list[str]:
    template = _agent_command_template(config)
    if not template:
        raise ProviderError("agent eval command is not configured")
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


def call_model_prompt(
    prompt: str,
    cwd: Path,
    timeout_seconds: int,
    config: dict[str, Any] | None = None,
    retries: int = 1,
) -> tuple[str, int, int]:
    output = ""
    return_code = 1
    for attempt in range(retries + 1):
        try:
            result = subprocess.run(
                _agent_cmd(prompt, config),
                cwd=str(cwd),
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") + "\n" + (exc.stderr or "")
            return_code = 124
        else:
            output = result.stdout
            if result.stderr:
                output = output.rstrip() + "\n\n[stderr]\n" + result.stderr
            return_code = result.returncode
        if output.strip() or return_code != 0:
            break
        time.sleep(2 + attempt)
    return output, return_code, len(prompt)


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[A-Za-z0-9_-]*\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _normalize_draft(text: str, case_id: str) -> str:
    text = _strip_code_fences(text)
    text = re.sub(rf"^\s*(?:#{1,6}\s*)?(?:[AB]-)?{re.escape(case_id)}[：:\s-]*", "", text).strip()
    text = re.sub(r"^\s*(以下为|下面是|正文如下)[^。\n]*[。:\n]", "", text).strip()
    return text.strip()


def _parse_sections(raw: str, case_ids: set[str]) -> dict[str, str]:
    lines = raw.splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    header_re = re.compile(r"^\s*(?:#{1,6}\s*)?(?:[AB]-)?(C\d{3})\b[：:\s-]*(.*)$", re.I)
    for line in lines:
        match = header_re.match(line)
        if match and match.group(1) in case_ids:
            current = match.group(1)
            sections.setdefault(current, [])
            if match.group(2).strip():
                sections[current].append(match.group(2).strip())
            continue
        if current:
            sections[current].append(line)

    parsed: dict[str, str] = {}
    for case_id, body_lines in sections.items():
        body = _normalize_draft("\n".join(body_lines), case_id)
        if body:
            parsed[case_id] = body
    return parsed


def _stub_draft(mode: str, case: dict[str, Any]) -> str:
    genre = _case_genre(case)
    scenario = str((case.get("vars") or {}).get("scenario", "")).strip()
    if mode == "baseline":
        return (
            f"围绕{scenario}事项，相关工作要全面赋能、不断提升，形成一批阶段性成果。"
            "各单位应高度重视，加强统筹协调，确保任务顺利推进。下一步将结合实际持续优化流程，"
            "进一步提升管理水平和服务能力，满足未来发展需要。"
        )
    if _is_ai_compute(genre):
        return (
            f"本{genre}围绕{scenario}需求，先按业务系统、使用人数、任务频次和单次 Token 消耗测算年度调用量，"
            "再折算 GPU、并发和云端费用。拟通过租赁服务明确部署边界、SLA、运维响应、安全审计和验收责任，"
            "以稳定周期成本并降低一次性建设风险。"
        )
    if genre == "请示":
        return (
            f"为推进{scenario}事项，拟由牵头部门组织相关单位开展资料核验、责任分工和节点管理，"
            "同步明确经费来源、实施范围和风险控制要求。现提请审定该事项启动安排及后续办理路径，"
            "妥否，请批示。"
        )
    if genre == "报告":
        return (
            f"现将{scenario}有关情况报告如下：前期已完成任务梳理、资料核验和责任分工，"
            "主要问题集中在数据口径、协同流程和归档标准不够统一。下一步将完善台账管理，"
            "按节点推进整改复核和成果归档。"
        )
    if genre == "复函":
        return (
            f"关于{scenario}事项的来函收悉。经研究，现函复如下：请按既定程序明确材料范围、"
            "办理条件、责任分工和反馈时限，同步说明联系人、附件依据和后续管理要求；"
            "涉及数据口径和结果报送的，请留存核验记录，便于后续沟通。"
        )
    return (
        f"现就{scenario}有关事项作出安排。请相关单位对照{genre}办理要求，明确责任分工、材料清单、"
        "反馈时限和联系人，按程序完成资料核验、过程记录和结果报送。涉及附件、数据和后续管理的，"
        "同步说明来源、范围和复核方式。"
    )


def _cache_key(mode: str, cases: list[dict[str, Any]], config: dict[str, Any]) -> str:
    routes = {
        _case_id(case): _case_reference_paths(case)
        for case in cases
    } if mode == "skill" else {}
    refs = _reference_paths_for_cases(cases) if mode == "skill" else []
    ref_hashes: dict[str, str] = {}
    if mode == "skill":
        root = _skill_root(_repo_root(config))
        for relative in refs:
            path = root / relative
            if path.exists():
                ref_hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    payload = {
        "mode": mode,
        "cases": [case.get("vars", {}) for case in cases],
        "routes": routes,
        "refs": refs,
        "ref_hashes": ref_hashes,
        "provider_version": 8,
        "stub": _use_stub(config),
        "command_configured": bool(_agent_command_template(config)),
        "command_template_hash": hashlib.sha256(
            _agent_command_template(config).encode("utf-8")
        ).hexdigest(),
        "batch_size": config.get("batchSize", 10),
        "timeout_seconds": config.get("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS),
        "retries": config.get("retries", 1),
    }
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return digest[:20]


def _write_cache(path: Path, data: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_cache(path: Path) -> dict[str, str] | None:
    if not path.exists() or os.environ.get("OFFICIAL_WRITING_EVAL_REFRESH"):
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _run_batch(mode: str, cases: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, str]:
    if _use_stub(config):
        return {_case_id(case): _stub_draft(mode, case) for case in cases}

    repo_root = _repo_root(config)
    timeout = int(config.get("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS))
    retries = int(config.get("retries", 1))
    prompt = _skill_prompt(cases, config) if mode == "skill" else _baseline_prompt(cases)
    raw, code, _prompt_chars = call_model_prompt(prompt, repo_root, timeout, config=config, retries=retries)
    if code != 0 and not raw.strip():
        raise ProviderError(f"agent eval command returned code {code} with empty output")
    case_ids = {_case_id(case) for case in cases}
    parsed = _parse_sections(raw, case_ids)
    return parsed


def _run_single(mode: str, case: dict[str, Any], config: dict[str, Any]) -> str:
    if _use_stub(config):
        return _stub_draft(mode, case)

    repo_root = _repo_root(config)
    timeout = int(config.get("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS))
    retries = int(config.get("retries", 1))
    prompt = _single_prompt(mode, case, config)
    raw, code, _prompt_chars = call_model_prompt(prompt, repo_root, timeout, config=config, retries=retries)
    if code != 0 and not raw.strip():
        raise ProviderError(f"agent eval command returned code {code} for {_case_id(case)} with empty output")
    parsed = _parse_sections(raw, {_case_id(case)})
    if parsed.get(_case_id(case)):
        return parsed[_case_id(case)]
    return _normalize_draft(raw, _case_id(case))


def _batch_cases(mode: str, cases: list[dict[str, Any]], batch_size: int) -> list[list[dict[str, Any]]]:
    if mode != "skill":
        return [cases[index : index + batch_size] for index in range(0, len(cases), batch_size)]

    route_groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for case in cases:
        route_groups.setdefault(tuple(_case_reference_paths(case)), []).append(case)

    batches: list[list[dict[str, Any]]] = []
    for group in route_groups.values():
        batches.extend(group[index : index + batch_size] for index in range(0, len(group), batch_size))
    return batches


def _ensure_batch_cache(mode: str, config: dict[str, Any]) -> dict[str, str]:
    memory_key = f"{mode}:{_cache_key(mode, _load_cases(config), config)}"
    if memory_key in _BATCH_CACHE:
        return _BATCH_CACHE[memory_key]

    cases = _load_cases(config)
    cache_path = _cache_dir(config) / f"writer-{memory_key.replace(':', '-')}.json"
    cached = _load_cache(cache_path)
    if cached is not None:
        _BATCH_CACHE[memory_key] = cached
        return cached

    batch_size = max(1, int(config.get("batchSize", 10)))
    outputs: dict[str, str] = {}
    for chunk in _batch_cases(mode, cases, batch_size):
        outputs.update(_run_batch(mode, chunk, config))
        _write_cache(cache_path, outputs)

    _BATCH_CACHE[memory_key] = outputs
    return outputs


def _estimate_usage(prompt: str, output: str, config: dict[str, Any]) -> tuple[dict[str, int], float]:
    prompt_tokens = max(1, len(prompt) // 2)
    completion_tokens = max(1, len(output) // 2)
    total = prompt_tokens + completion_tokens
    cost_per_1k_chars = float(config.get("estimatedCostPer1kChars", 0.00002))
    cost = ((len(prompt) + len(output)) / 1000.0) * cost_per_1k_chars
    return {"prompt": prompt_tokens, "completion": completion_tokens, "total": total, "numRequests": 1}, cost


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    config = _options_config(options)
    mode = str(config.get("mode", "baseline")).strip().lower()
    if mode not in {"baseline", "skill"}:
        return {"output": "", "error": f"unsupported provider mode: {mode}"}

    case = _current_case(context)
    case_id = _case_id(case)
    started = time.time()
    try:
        outputs = _ensure_batch_cache(mode, config) if config.get("prebatch", True) else {}
        output = outputs.get(case_id)
        if not output:
            output = _run_single(mode, case, config)
    except Exception as exc:
        return {"output": "", "error": str(exc)}

    output = _normalize_draft(output, case_id)
    if not output:
        return {"output": "", "error": f"empty output for {case_id} in {mode} mode"}

    token_usage, cost = _estimate_usage(prompt, output, config)
    return {
        "output": output,
        "tokenUsage": token_usage,
        "cost": cost,
        "latencyMs": int((time.time() - started) * 1000),
        "metadata": {
            "case_id": case_id,
            "genre": _case_genre(case),
            "mode": mode,
            "selected_references": _case_reference_paths(case) if mode == "skill" else [],
            "provider": str(
                config.get("providerLabel")
                or os.environ.get("OFFICIAL_WRITING_EVAL_PROVIDER_LABEL")
                or ("deterministic-local" if _use_stub(config) else "agent-eval-command")
            ),
            "estimated_cost_note": "character-count proxy; agent command billing is not read here",
        },
    }

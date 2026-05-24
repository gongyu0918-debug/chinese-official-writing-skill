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
    "default": [
        "references/genre-routing.md",
        "references/handling-elements.md",
        "references/genre-checklist.md",
        "references/anti-ai-patterns.md",
    ],
    "argument": [
        "references/argument-chains.md",
        "references/official-style.md",
    ],
    "ai_compute": [
        "references/argument-chains.md",
        "references/ai-compute-docs.md",
        "references/anti-ai-patterns.md",
    ],
}

ARGUMENT_GENRES = {
    "请示",
    "报告",
    "方案",
    "意见",
    "工作要点",
    "工作总结",
    "调研报告",
    "可研报告",
    "实施方案",
    "建设方案",
    "审查材料",
}

AI_COMPUTE_MARKERS = ("算力", "GPU", "服务器", "云端", "技术服务")

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


def _read_text(path: Path, max_chars: int = 12000) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n[truncated]\n"


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


def _is_ai_compute(genre: str) -> bool:
    return any(marker in genre for marker in AI_COMPUTE_MARKERS)


def _skill_root(repo_root: Path) -> Path:
    installed = repo_root / ".agents" / "skills" / "chinese-official-writing"
    if installed.exists():
        return installed
    return repo_root / "chinese-official-writing"


def _reference_paths_for_genres(genres: list[str]) -> list[str]:
    paths = ["SKILL.md", *GENRE_REFERENCES["default"]]
    if any(genre in ARGUMENT_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["argument"])
    if any(_is_ai_compute(genre) for genre in genres):
        paths.extend(GENRE_REFERENCES["ai_compute"])

    seen: set[str] = set()
    ordered: list[str] = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            ordered.append(path)
    return ordered


def _load_skill_context(repo_root: Path, genres: list[str]) -> str:
    root = _skill_root(repo_root)
    parts: list[str] = []
    for relative in _reference_paths_for_genres(genres):
        path = root / relative
        if not path.exists():
            continue
        limit = 9000 if relative == "SKILL.md" else 7000
        parts.append(f"## {relative}\n{_read_text(path, limit)}")
    return "\n\n".join(parts)


def _case_id(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("case_id", "")).strip()


def _case_genre(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("genre", "")).strip()


def _case_task(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("task", "")).strip()


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
    genres = sorted({_case_genre(case) for case in cases if _case_genre(case)})
    skill_context = _load_skill_context(repo_root, genres)
    return textwrap.dedent(
        f"""
        你是中文公文 Skill 写作代理。仓库已安装 Skill：
        `.agents/skills/chinese-official-writing/SKILL.md`。

        只使用下列 Skill 入口和与本批文种相关的 references；不要加载整包上下文，不要复制参考资料原文。
        先判断文种，再抽取办理要素，再组织论证链条，最后做反 AI、文种边界和格式噪点自查。

        对每个任务输出一段中文正式材料初稿，控制在 160-260 个汉字。不要编造真实单位、真实政策、真实金额、
        人名、电话、邮箱或内部项目事实。可使用“有关单位”“相关部门”等泛称，但不要把“发文机关、
        发文字号、主送单位”等占位标签写进正文。

        输出必须严格按如下格式，不要解释：
        ### <case_id>
        <正文>

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
    return (
        f"现就{scenario}有关事项作出安排。请相关单位对照{genre}办理要求，明确责任分工、材料清单、"
        "反馈时限和联系人，按程序完成资料核验、过程记录和结果报送。涉及附件、数据和后续管理的，"
        "同步说明来源、范围和复核方式。"
    )


def _cache_key(mode: str, cases: list[dict[str, Any]], config: dict[str, Any]) -> str:
    genres = sorted({_case_genre(case) for case in cases})
    refs = _reference_paths_for_genres(genres)
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
        "refs": refs,
        "ref_hashes": ref_hashes,
        "provider_version": 3,
        "stub": _use_stub(config),
        "command_configured": bool(_agent_command_template(config)),
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
    timeout = int(config.get("timeoutSeconds", 600))
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
    timeout = int(config.get("timeoutSeconds", 600))
    retries = int(config.get("retries", 1))
    prompt = _single_prompt(mode, case, config)
    raw, code, _prompt_chars = call_model_prompt(prompt, repo_root, timeout, config=config, retries=retries)
    if code != 0 and not raw.strip():
        raise ProviderError(f"agent eval command returned code {code} for {_case_id(case)} with empty output")
    parsed = _parse_sections(raw, {_case_id(case)})
    if parsed.get(_case_id(case)):
        return parsed[_case_id(case)]
    return _normalize_draft(raw, _case_id(case))


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
    for index in range(0, len(cases), batch_size):
        chunk = cases[index : index + batch_size]
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
            "provider": str(
                config.get("providerLabel")
                or os.environ.get("OFFICIAL_WRITING_EVAL_PROVIDER_LABEL")
                or ("deterministic-local" if _use_stub(config) else "agent-eval-command")
            ),
            "estimated_cost_note": "character-count proxy; agent command billing is not read here",
        },
    }

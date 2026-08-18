#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter, defaultdict
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUN = ROOT / "output/post-integration-wr-ah-cold-review/formal-r1"
MAPPING = ROOT / "output/post-integration-wr-ah-cold-review/restricted-mapping.json"
CASES = HERE / "cases.json"
WRITING_PACKET = HERE / "writing-blind-packet.md"
DIFF_PACKET = HERE / "diff-cold-review-packet.md"
ENTROPY_PACKET = HERE / "entropy-review-packet.md"
FREEZE = HERE / "packet-freeze.json"
BASELINE = "17de0712fd09a409fc56135e4929caf8bc4c0fce"
CANDIDATE = "9a130454ff0d7a84a5d2195390a6985b01ae8a62"
RANDOM_SEED = 20260818
PRODUCT_PATHS = [
    "chinese-official-writing/hooks/capabilities/over_length/runtime.py",
    "chinese-official-writing/hooks/capabilities/under_length/runtime.py",
    "chinese-official-writing/hooks/shared/hard_anchors.py",
    "chinese-official-writing/references/anti-ai-patterns.md",
    "chinese-official-writing/references/genre-playbook-request.md",
]
SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？；])")
MARKDOWN_PREFIX_RE = re.compile(r"^(?:#{1,6}\s+|[-*+]\s+|\d+[.)、]\s*)")
NORMALIZE_RE = re.compile(r"[\s`*_>#|：:，,。；;！？!?（）()\[\]【】‘’“”\"'—-]+")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=True,
        timeout=60,
    ).stdout


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str, str], dict[str, Any]]]:
    cases = {
        item["id"]: item
        for item in json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    }
    manifest = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("calls_completed") != 24 or manifest.get("technical_valid") != 24:
        raise RuntimeError("formal run is not 24/24 valid")
    arms = {
        (item["provider"], item["case_id"], item["treatment"]): item
        for item in manifest["arms"]
    }
    if len(arms) != 24:
        raise RuntimeError("arm matrix incomplete")
    return cases, arms


def final_text(arm: dict[str, Any]) -> str:
    return (RUN / "raw" / arm["arm_id"] / "final.txt").read_text(encoding="utf-8")


def build_writing_packet(
    cases: dict[str, dict[str, Any]],
    arms: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, Any]:
    rng = random.Random(RANDOM_SEED)
    lines = [
        "# 集成后真实写稿匿名包",
        "",
        "逐组独立评价稿件甲、乙。先检查事实、状态、责任、文种、篇幅和是否可直接使用，再评价自然度、重复、自证和机械化。只把候选稿相对另一稿新增的问题记为 DIFF 风险；无法归因时明确写抽样差异。不得猜测版本身份。",
        "",
    ]
    mapping: dict[str, Any] = {}
    pair_index = 0
    for provider in sorted({key[0] for key in arms}):
        for case_id in sorted(cases):
            pair_index += 1
            pair_id = f"P{pair_index:02d}"
            order = ["baseline", "candidate"]
            rng.shuffle(order)
            labels = {"甲": order[0], "乙": order[1]}
            case = cases[case_id]
            lines.extend([f"## {pair_id}", "", f"任务：{case['request']}", ""])
            pair_mapping: dict[str, Any] = {"provider": provider, "case_id": case_id}
            for label in ("甲", "乙"):
                treatment = labels[label]
                arm = arms[(provider, case_id, treatment)]
                text = final_text(arm)
                lines.extend([f"### 稿件{label}", "", text.rstrip(), ""])
                pair_mapping[label] = {
                    "treatment": treatment,
                    "arm_id": arm["arm_id"],
                    "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                }
            mapping[pair_id] = pair_mapping
    lines.extend(
        [
            "## 输出格式",
            "",
            "为每组输出：甲/乙各自的 facts、state、genre、length、naturalness、repetition、direct_use_cost（PASS/WARN/FAIL 或 0—5），winner（甲/乙/难分），以及一句具体理由。最后列出最多5项跨组共同问题。",
        ]
    )
    write_text(WRITING_PACKET, "\n".join(lines))
    write_json(MAPPING, mapping)
    return mapping


def read_load_table(arms: dict[tuple[str, str, str], dict[str, Any]]) -> str:
    rows = ["| Pair | Baseline files/bytes | Candidate files/bytes |", "| --- | ---: | ---: |"]
    for provider in sorted({key[0] for key in arms}):
        for case_id in sorted({key[1] for key in arms}):
            baseline = arms[(provider, case_id, "baseline")]
            candidate = arms[(provider, case_id, "candidate")]
            rows.append(
                f"| {provider}-{case_id} | {len(baseline['loaded_skill_files'])}/{baseline['loaded_skill_bytes']} | "
                f"{len(candidate['loaded_skill_files'])}/{candidate['loaded_skill_bytes']} |"
            )
    return "\n".join(rows)


def normalized(value: str) -> str:
    value = MARKDOWN_PREFIX_RE.sub("", value.strip())
    return NORMALIZE_RE.sub("", value).lower()


def collect_sentences() -> list[dict[str, Any]]:
    skill_root = ROOT / "chinese-official-writing"
    paths = [skill_root / "SKILL.md", *sorted((skill_root / "references").glob("*.md"))]
    items: list[dict[str, Any]] = []
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for part in SENTENCE_SPLIT_RE.split(line):
                text = part.strip()
                key = normalized(text)
                if 20 <= len(key) <= 180 and not text.startswith("|"):
                    items.append(
                        {
                            "path": path.relative_to(skill_root).as_posix(),
                            "line": line_number,
                            "text": text,
                            "key": key,
                        }
                    )
    return items


def grams(value: str) -> set[str]:
    return {value[index : index + 2] for index in range(len(value) - 1)}


def duplicate_candidates(items: list[dict[str, Any]]) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]]]:
    exact_by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        exact_by_key[item["key"]].append(item)
    exact = [group for group in exact_by_key.values() if len(group) > 1]
    exact.sort(key=lambda group: (-len(group), -len(group[0]["key"])))

    gram_sets = [grams(item["key"]) for item in items]
    index: dict[str, list[int]] = defaultdict(list)
    intersections: Counter[tuple[int, int]] = Counter()
    for current, current_grams in enumerate(gram_sets):
        for gram in current_grams:
            previous = index[gram]
            if len(previous) <= 80:
                for other in previous:
                    intersections[(other, current)] += 1
            previous.append(current)
    near: list[dict[str, Any]] = []
    for (left, right), intersection in intersections.items():
        if items[left]["key"] == items[right]["key"]:
            continue
        union = len(gram_sets[left]) + len(gram_sets[right]) - intersection
        if not union or intersection / union < 0.52:
            continue
        similarity = SequenceMatcher(
            None, items[left]["key"], items[right]["key"], autojunk=False
        ).ratio()
        if similarity >= 0.78:
            near.append(
                {"similarity": round(similarity, 3), "left": items[left], "right": items[right]}
            )
    near.sort(key=lambda item: (-item["similarity"], -min(len(item["left"]["key"]), len(item["right"]["key"]))))
    return exact[:20], near[:40]


def build_diff_and_entropy_packets(
    arms: dict[tuple[str, str, str], dict[str, Any]]
) -> None:
    diff = git("diff", "--no-ext-diff", BASELINE, CANDIDATE, "--", *PRODUCT_PATHS)
    write_text(
        DIFF_PACKET,
        "\n".join(
            [
                "# WR-007 + AH-001 产品 DIFF 冷审包",
                "",
                "只审下列固定 DIFF。重点检查：规则是否造成新外扩或过严回退；共享硬锚是否错误处理数量去重、引语、字段、主体/对象/范围/状态关系；异常时是否仍回退 D0；是否出现上帝函数、魔法数字、孤儿路径或普通无 Hook 路径污染。逐项报告 P0—P2；没有问题写 PASS。",
                "",
                "```diff",
                diff.rstrip(),
                "```",
            ]
        ),
    )

    items = collect_sentences()
    exact, near = duplicate_candidates(items)
    skill_root = ROOT / "chinese-official-writing"
    files = [skill_root / "SKILL.md", *sorted((skill_root / "references").glob("*.md"))]
    lines = [
        "# SKILL 与 references 信息熵复核包",
        "",
        f"当前共 {len(files)} 个入口/reference 文件，{sum(path.stat().st_size for path in files)} 字节，"
        f"{sum(len(path.read_text(encoding='utf-8').splitlines()) for path in files)} 行。",
        "",
        "先结合真实写稿读取量，再审下列确定性重复候选。相似不等于应删；只有重复加载、规则冲突、机械化或真实稿回退能够支持减载。不要建议把所有规则并回 SKILL.md，也不要创建总词典。",
        "",
        "## 真实读取量",
        "",
        read_load_table(arms),
        "",
        "## SKILL.md 全文",
        "",
        (skill_root / "SKILL.md").read_text(encoding="utf-8").rstrip(),
        "",
        "## 逐字重复候选",
        "",
    ]
    for index, group in enumerate(exact, start=1):
        lines.append(f"### E{index:02d}")
        for item in group:
            lines.append(f"- `{item['path']}:{item['line']}` {item['text']}")
        lines.append("")
    lines.extend(["## 高相似候选", ""])
    for index, item in enumerate(near, start=1):
        left, right = item["left"], item["right"]
        lines.extend(
            [
                f"### N{index:02d} similarity={item['similarity']}",
                f"- `{left['path']}:{left['line']}` {left['text']}",
                f"- `{right['path']}:{right['line']}` {right['text']}",
                "",
            ]
        )
    write_text(ENTROPY_PACKET, "\n".join(lines))


def main() -> int:
    cases, arms = load_inputs()
    mapping = build_writing_packet(cases, arms)
    build_diff_and_entropy_packets(arms)
    freeze = {
        "baseline_commit": BASELINE,
        "candidate_commit": CANDIDATE,
        "pairs": len(mapping),
        "writing_packet_sha256": sha256_file(WRITING_PACKET),
        "diff_packet_sha256": sha256_file(DIFF_PACKET),
        "entropy_packet_sha256": sha256_file(ENTROPY_PACKET),
        "manifest_sha256": sha256_file(RUN / "manifest.json"),
    }
    write_json(FREEZE, freeze)
    print(json.dumps(freeze, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

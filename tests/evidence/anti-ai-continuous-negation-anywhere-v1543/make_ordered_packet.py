from __future__ import annotations

import hashlib
import json
import secrets

from harness import JUDGE_FACTS, OUT


HEADINGS = [f"## {name}" for name in ("T1", "T2", "T3", "C1", "C2", "C3")]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def heading_status(text: str) -> tuple[bool, list[int], list[str]]:
    positions = [text.find(heading) for heading in HEADINGS]
    reasons: list[str] = []
    if not all(text.count(heading) == 1 for heading in HEADINGS):
        reasons.append("missing_or_duplicate_headings")
    if positions != sorted(positions):
        reasons.append("wrong_heading_order")
    return not reasons, positions, reasons


def main() -> None:
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest["records"]
    by_key = {
        (record["provider"], record["replicate"], record["arm"]): record for record in records
    }
    providers = sorted({record["provider"] for record in records})

    arm_validity: dict[tuple[str, int, str], dict] = {}
    for key, record in by_key.items():
        text = (OUT / record["final_file"]).read_text(encoding="utf-8")
        headings_ok, positions, reasons = heading_status(text)
        if record["return_code"] != 0:
            reasons.append("nonzero_return_code")
        if record["error"] is not None:
            reasons.append("execution_error")
        if not text:
            reasons.append("empty_final")
        arm_validity[key] = {
            "valid": headings_ok and not reasons,
            "heading_positions": positions,
            "reasons": reasons,
        }

    valid_pairs: list[tuple[str, int]] = []
    invalid_pairs: list[dict] = []
    for provider in providers:
        replicates = sorted(
            {record["replicate"] for record in records if record["provider"] == provider}
        )
        for replicate in replicates:
            invalid_arms = {
                arm: arm_validity[(provider, replicate, arm)]["reasons"]
                for arm in ("baseline", "candidate")
                if not arm_validity[(provider, replicate, arm)]["valid"]
            }
            if invalid_arms:
                invalid_pairs.append(
                    {"provider": provider, "replicate": replicate, "invalid_arms": invalid_arms}
                )
            else:
                valid_pairs.append((provider, replicate))

    if not valid_pairs:
        raise RuntimeError("no valid pairs")

    rng = secrets.SystemRandom()
    mapping: dict[str, dict] = {}
    sections = ["# 连续否定全位置减载匿名 A/B（有序标题有效对）", "", JUDGE_FACTS, ""]
    for index, (provider, replicate) in enumerate(valid_pairs, start=1):
        pair_id = f"P{index}"
        arms = ["baseline", "candidate"]
        rng.shuffle(arms)
        mapping[pair_id] = {
            "provider": provider,
            "replicate": replicate,
            "A": arms[0],
            "B": arms[1],
        }
        sections.extend([f"## {pair_id}", ""])
        for label, arm in zip(("A", "B"), arms):
            record = by_key[(provider, replicate, arm)]
            body = (OUT / record["final_file"]).read_text(encoding="utf-8").strip()
            sections.extend([f"### {label}", "", body, ""])

    packet = "\n".join(sections).rstrip() + "\n"
    mapping_text = json.dumps(mapping, ensure_ascii=False, indent=2) + "\n"
    packet_bytes = packet.encode("utf-8")
    mapping_bytes = mapping_text.encode("utf-8")
    packet_path = OUT / "blind-packet-valid-ordered-pairs.md"
    mapping_path = OUT / "blind-mapping-valid-ordered-pairs.json"
    if packet_path.exists() or mapping_path.exists():
        raise RuntimeError("ordered-pair blind artifacts already exist")
    packet_path.write_bytes(packet_bytes)
    mapping_path.write_bytes(mapping_bytes)

    manifest["ordered_arm_validity"] = {
        f"{provider}-r{replicate}-{arm}": value
        for (provider, replicate, arm), value in arm_validity.items()
    }
    manifest["ordered_valid_pairs"] = [
        f"{provider}-r{replicate}" for provider, replicate in valid_pairs
    ]
    manifest["ordered_invalid_pairs"] = invalid_pairs
    manifest["ordered_blind_packet_sha256"] = sha256_bytes(packet_bytes)
    manifest["ordered_blind_mapping_sha256"] = sha256_bytes(mapping_bytes)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"valid_pairs={len(valid_pairs)}")
    print(f"invalid_pairs={json.dumps(invalid_pairs, ensure_ascii=False)}")
    print(f"blind_packet_sha256={manifest['ordered_blind_packet_sha256']}")
    print(f"blind_mapping_sha256={manifest['ordered_blind_mapping_sha256']}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import hashlib
import json
import secrets

from harness import JUDGE_FACTS, OUT


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest["records"]
    by_key = {
        (record["provider"], record["replicate"], record["arm"]): record for record in records
    }

    valid_pairs: list[tuple[str, int]] = []
    invalid_pairs: list[dict] = []
    for provider in ("alibaba", "ollama"):
        for replicate in (1, 2, 3):
            pair_records = [
                by_key[(provider, replicate, "baseline")],
                by_key[(provider, replicate, "candidate")],
            ]
            invalid_arms = [
                record["arm"]
                for record in pair_records
                if record["return_code"] != 0
                or record["error"] is not None
                or record["final_chars"] == 0
                or not record["headings_complete"]
            ]
            if invalid_arms:
                invalid_pairs.append(
                    {"provider": provider, "replicate": replicate, "invalid_arms": invalid_arms}
                )
            else:
                valid_pairs.append((provider, replicate))

    if valid_pairs != [
        ("alibaba", 1),
        ("alibaba", 2),
        ("alibaba", 3),
        ("ollama", 1),
        ("ollama", 2),
    ]:
        raise RuntimeError(f"unexpected valid pairs: {valid_pairs}")

    rng = secrets.SystemRandom()
    mapping: dict[str, dict] = {}
    sections = ["# 连续否定全位置减载匿名 A/B", "", JUDGE_FACTS, ""]
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
    packet_path = OUT / "blind-packet-valid-pairs.md"
    mapping_path = OUT / "blind-mapping-valid-pairs.json"
    if packet_path.exists() or mapping_path.exists():
        raise RuntimeError("valid-pair blind artifacts already exist")
    packet_path.write_bytes(packet_bytes)
    mapping_path.write_bytes(mapping_bytes)

    manifest["valid_pairs"] = [f"{provider}-r{replicate}" for provider, replicate in valid_pairs]
    manifest["invalid_pairs"] = invalid_pairs
    manifest["valid_pair_blind_packet_sha256"] = sha256_bytes(packet_bytes)
    manifest["valid_pair_blind_mapping_sha256"] = sha256_bytes(mapping_bytes)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"valid_pairs={len(valid_pairs)}")
    print(f"invalid_pairs={json.dumps(invalid_pairs, ensure_ascii=False)}")
    print(f"blind_packet_sha256={manifest['valid_pair_blind_packet_sha256']}")
    print(f"blind_mapping_sha256={manifest['valid_pair_blind_mapping_sha256']}")


if __name__ == "__main__":
    main()

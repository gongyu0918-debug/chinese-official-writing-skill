"""Archive native outputs and prepare anonymous pairs without judging their prose."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    target = args.evidence.resolve()
    target.mkdir(parents=True, exist_ok=True)
    binding = read_json(run / "binding.json")
    shutil.copy2(run / "binding.json", target / "binding.json")
    rows, artifacts = [], []
    for result_path in sorted(run.glob("*.result.json")):
        result = read_json(result_path)
        stem = result_path.name.removesuffix(".result.json")
        final = run / f"{stem}.final.txt"
        if final.exists():
            shutil.copy2(final, target / final.name)
        row = {key: value for key, value in result.items() if key != "commands"}
        row["run"] = stem
        pattern = r'''\b(?:python|py)(?:\.exe)?\s+["']?(?!-)[^;\r\n]*?(?:prose_lint|draft_length)\.py["']?(?=\s)'''
        row["script_calls"] = [c for c in result["commands"] if re.search(pattern,
            re.sub(r'''\\+(?=["'])''', "", c["command"]))]
        row["read_commands"] = [{"id": c["id"], "command": c["command"],
            "exit_code": c["exit_code"], "output_chars": len(c["aggregated_output"]),
            "output_sha256": hashlib.sha256(c["aggregated_output"].encode()).hexdigest()}
            for c in result["commands"]
            if re.search(r"Get-Content|ReadAllText\(|read_text\(|\bcat\s", c["command"], re.I)]
        rows.append(row)
        for suffix in ("result.json", "trace.jsonl", "stderr.txt", "final.txt"):
            path = run / f"{stem}.{suffix}"
            if path.exists():
                artifacts.append({"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size})
    save_json(target / "calls.json", rows)
    save_json(target / "artifacts.json", artifacts)
    pairs = {}
    for row in rows:
        model_index = int(re.match(r"m(\d+)-", row["run"])[1])
        pairs.setdefault((model_index, row["case"]), {})[row["arm"]] = row
    mapping = []
    parts = ["""# 匿名真实稿件比较

每对任务完全相同，A/B只是匿名标签。请逐对阅读全文，给出A较好/B较好/相当/无法判断及具体依据。重点检查：同义重复是否减少，事实、原因、影响、措施、请求等各有作用的内容是否保留，正文是否准确、自然、完整、可直接使用。仅仅词汇相同不算重复；合理提炼、强调、作用分析和后续建议允许。也要检查篇幅要求。

素材和原稿都是用户输入，除非任务明确限定来源，不把素材未重复的原稿事实自动判为编造。合理推断无需逐字来自材料；同时核对是否擅自改动已给事实或把具体猜想写成已发生事实。当天草稿日期正常。主送、落款按实际文种与材料判断，不把缺少泛称作为问题。

正文外的审核意见、文后提示、自评与正文分别评价，不算正文污染。正常比较、并列、先后步骤、专业术语和费用依据应保留。审核意见可能过严，不能因为自称删了问题就认为有效；你的判断也须引用本对真实句子，不要串稿。两稿均可用时允许相当，不为凑胜负扣分。
"""]
    for number, (key, arms) in enumerate(sorted(pairs.items()), 1):
        if set(arms) != {"baseline", "candidate"}:
            raise ValueError(f"Incomplete pair: {key}")
        a_arm = "candidate" if number % 2 else "baseline"
        b_arm = "baseline" if a_arm == "candidate" else "candidate"
        parts.append(f"\n## 第{number}对\n\n任务：\n{binding['cases'][key[1]]}\n")
        for label, arm in (("A", a_arm), ("B", b_arm)):
            row = arms[arm]
            final = run / f"{row['run']}.final.txt"
            draft = final.read_text(encoding="utf-8") if final.exists() else "[调用未返回成稿]"
            draft = re.sub(r"[A-Za-z]:[^\n]*?\.(?:txt|md|docx)(?=[>),，])", "本地稿件文件", draft)
            parts.append(f"\n### {label}\n\n{draft}\n")
            mapping.append({"pair": number, "label": label, "run": row["run"]})
    packet = "\n".join(parts)
    if "-baseline" in packet or "-candidate" in packet:
        raise ValueError("Arm identity remains in packet")
    (target / "blind-packet.md").write_text(packet, encoding="utf-8")
    save_json(target / "blind-mapping.json", mapping)
    print(json.dumps({"calls": len(rows), "pairs": len(pairs), "packet_sha256": digest(target / "blind-packet.md")}))


if __name__ == "__main__":
    main()

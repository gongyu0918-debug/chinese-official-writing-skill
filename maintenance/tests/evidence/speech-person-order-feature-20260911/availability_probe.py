"""One preregistered baseline writing observation per newly checked routine route."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("feature_writer_harness", HERE / "harness_qwen.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--route", required=True)
    args = p.parse_args()
    out = args.out.resolve()
    registry = harness.read(HERE / "model-registry.json")
    registration = harness.read(HERE / "availability-preregister.json")
    freeze = harness.read(out / "freeze.json")
    assert args.route in registration["routes"] and registry["routine"][args.route]
    assert harness.sha((HERE / "harness_qwen.py").read_bytes()) == freeze["harness_sha256"]
    source = out / "frozen/baseline"
    assert harness.manifest(source) == harness.read(out / "baseline-manifest.json")
    task = HERE / registration["prompt_file"]
    plan = dict(freeze["plan"])
    plan.update({k: registration[k] for k in ("effort", "timeout_seconds", "request_timeout_seconds", "max_output_tokens")})
    run = out / "availability" / args.route.replace("/", "--") / "attempt-1"
    def prompt(snapshot):
        return ("这是只读、隔离的真实写稿测试。先读 " + (snapshot / "SKILL.md").as_posix() +
                "，按入口选读任务需要的包内页面。只读input目录，不读其他目录或记忆，不联网、不启用Hook、不执行脚本。\n\n" +
                task.read_text(encoding="utf-8-sig"))
    receipt = harness.execute(run, args.route, prompt, lambda dest: shutil.copytree(source, dest), plan)
    receipt.update(purpose="routine_model_usability_only_not_feature_AB",
                   availability_preregister_sha256=harness.sha((HERE / "availability-preregister.json").read_bytes()),
                   task_sha256=harness.sha(task.read_bytes()), source_commit=freeze["commits"]["baseline"],
                   probe_sha256=harness.sha(Path(__file__).read_bytes()))
    harness.save(run / "receipt.json", receipt)
    return 0 if receipt["technical_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path

import run_cause_hint as runner


runner.CONFIG_PATH = Path(__file__).resolve().with_name("cause-hint-holdout-cases.json")
runner.OUTPUT_ROOT = runner.REPO / "output/short-inference-r1/cause-hint-holdout"


if __name__ == "__main__":
    raise SystemExit(runner.main())

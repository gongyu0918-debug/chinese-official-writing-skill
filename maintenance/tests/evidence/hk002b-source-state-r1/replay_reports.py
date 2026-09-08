"""Replay existing R2 observations after report-only malformed-input handling."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def read(path): return json.loads(path.read_text(encoding="utf-8"))

def main():
    module_path=ROOT/"chinese-official-writing/scripts/review_gate.py"
    current=module_path.read_text(encoding="utf-8")
    frozen=(HERE/"raw/core-r2/product/chinese-official-writing/scripts/review_gate.py").read_text(encoding="utf-8")
    start="def source_fact_report(";end="def dispatch_transaction("
    assert frozen.split(start)[0]==current.split(start)[0]
    assert frozen.split(end)[1]==current.split(end)[1]
    spec=importlib.util.spec_from_file_location("report_replay_gate",module_path)
    gate=importlib.util.module_from_spec(spec);sys.modules[spec.name]=gate;spec.loader.exec_module(gate)
    checked=[]
    for lane in sorted((HERE/"raw/core-r2/transactions").glob("*/*")):
        baseline=read(lane/"shared-report-before-echo.json")
        assert gate.source_fact_report(lane/"txn")==baseline
        checked.append(str((lane/"shared-report-before-echo.json").relative_to(HERE)))
        if (lane/"shared-report.json").exists():
            writer,cid=lane.parent.name,lane.name
            observed=(HERE/"raw/core-r2/calls/echo"/cid/writer/"attempt-01/final.txt").read_text(encoding="utf-8")
            assert gate.source_fact_report(lane/"txn",observed)==read(lane/"shared-report.json")
            checked.append(str((lane/"shared-report.json").relative_to(HERE)))
    result={"report_only_change_after_r2":True,"model_calls_added":0,"reports_equal":len(checked),"report_module_git_lf_sha256":hashlib.sha256(current.encode("utf-8")).hexdigest(),"checked":checked}
    (HERE/"post-r2-report-check.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"reports_equal":len(checked),"model_calls_added":0}))

if __name__=="__main__": main()

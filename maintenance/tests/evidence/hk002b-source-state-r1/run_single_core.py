"""R2: one frozen production instruction per call; preserve R1 failures."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("hk002b_previous_driver",HERE/"run_core.py")
CORE=importlib.util.module_from_spec(spec);sys.modules[spec.name]=CORE;spec.loader.exec_module(CORE)
BASE=CORE.BASE
OUT=CORE.ROOT/"output/hk002b-core-r2"
CORE.OUT=OUT
IDS=("real_condition","ongoing_counterexample","real_control","latest_correction_control")

def prepare():
    OUT.mkdir(parents=True,exist_ok=False)
    product=OUT/"product/chinese-official-writing"
    shutil.copytree(CORE.ROOT/"chinese-official-writing",product,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    manifest=[{"path":p.relative_to(product).as_posix(),"sha256":BASE.sha(p.read_bytes())} for p in sorted(product.rglob("*")) if p.is_file()]
    BASE.save(OUT/"product-manifest.json",manifest)
    cases=[c for c in CORE.read(BASE.OUT/"cases.json") if c["id"] in IDS]
    BASE.save(OUT/"cases.json",cases)
    gate,hook=CORE.modules()
    jobs=[]
    for writer in CORE.PROVIDERS:
        for case in cases:
            lane=OUT/"transactions"/writer/case["id"];lane.mkdir(parents=True)
            for key in ("request","source","draft"):
                (lane/(key+".txt")).write_text(case[key],encoding="utf-8",newline="\n")
            txn=lane/"txn"
            state=gate.detect_transaction(lane/"request.txt",lane/"draft.txt",[lane/"source.txt"] if case["source"] else [],txn,1800,1800)
            BASE.save(lane/"initial-state.json",state)
            if state["state"]==gate.STATE_AWAITING_REPAIR:
                instruction=hook._repair_instruction(txn);assert instruction
                (lane/"repair-prompt.txt").write_text(instruction+"\n不要调用工具或读取文件；本条已包含完整绑定输入。",encoding="utf-8")
                jobs.append({"writer":writer,"case":case["id"]})
    assert len(jobs)==10
    BASE.save(OUT/"repair-jobs.json",jobs)
    BASE.save(OUT/"freeze.json",{"base":"f69534f05a2ae8c2da4f39d35a35497a90d0efff","models":BASE.MODELS,"verifier_routes":CORE.VERIFIERS,"effort":"max","cases":len(cases),"repair_jobs":len(jobs),"frozen_files":len(manifest),"native_host_installation_tested":False,"changes_from_r1":["one complete instruction per CLI call","merge enclosed source and existing findings without deleting existing labels","predicate-only repair instruction preserves local anchors","verification proof reconstructed from frozen snapshots on finalize and recovery"],"method":"canonical detect/prepare/finalize/emit with real separate-route CLI responses; final CLI echo separately observed"})
    print(json.dumps({"prepared":True,"product_files":len(manifest),"repair_jobs":len(jobs)}),flush=True)

def call_path(job,phase):
    provider=job["writer"] if phase=="repair" else CORE.VERIFIERS[job["writer"]]
    return OUT/"calls"/phase/job["case"]/job["writer"]/provider/"attempt-01"

def run_phase(phase):
    CORE.assert_frozen()
    jobs=CORE.read(OUT/(phase+"-jobs.json"))
    def run(job):
        writer,cid=job["writer"],job["case"]
        BASE.run_one(writer if phase=="repair" else CORE.VERIFIERS[writer],prompt_path=OUT/"transactions"/writer/cid/(phase+"-prompt.txt"),run_root=OUT/"calls"/phase/cid/writer)
    def lane(writer):
        for job in jobs:
            if job["writer"]==writer: run(job)
    with ThreadPoolExecutor(max_workers=5) as pool: list(pool.map(lane,CORE.PROVIDERS))

def consume(phase):
    CORE.assert_frozen();gate,hook=CORE.modules();summary=[];next_jobs=[]
    for job in CORE.read(OUT/(phase+"-jobs.json")):
        lane=OUT/"transactions"/job["writer"]/job["case"];txn=lane/"txn"
        call=call_path(job,phase)
        receipt=CORE.read(call/"receipt.json")
        response=hook._extract_json_object((call/"final.txt").read_text(encoding="utf-8")) if receipt["technical_completed"] else None
        response_path=lane/(phase+"-response.json")
        if isinstance(response,dict): BASE.save(response_path,response)
        else: response_path=None
        if phase=="repair":
            state=gate.prepare_transaction(txn,response_path)
            if state["state"]==gate.STATE_AWAITING_VERDICT:
                instruction=hook._verdict_instruction(txn);assert instruction
                (lane/"verdict-prompt.txt").write_text(instruction+"\n不要调用工具或读取文件；本条已包含完整绑定输入。",encoding="utf-8")
                next_jobs.append(job)
        else: state=gate.finalize_transaction(txn,response_path)
        BASE.save(lane/(phase+"-state.json"),state)
        summary.append({**job,"state":state["state"],"selected":state.get("selected"),"reason":state["reason"]})
    BASE.save(OUT/(phase+"-summary.json"),summary)
    if phase=="repair": BASE.save(OUT/"verdict-jobs.json",next_jobs)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)

def emit():
    CORE.assert_frozen();gate,_=CORE.modules()
    for writer in CORE.PROVIDERS:
        for case in CORE.read(OUT/"cases.json"):
            lane=OUT/"transactions"/writer/case["id"];txn=lane/"txn"
            assert CORE.read(txn/gate.STATE_FILE)["state"] in gate.TERMINAL_STATES
            stdout=io.StringIO()
            with redirect_stdout(stdout): selected=gate.emit_transaction(txn)
            assert stdout.getvalue()==selected
            (lane/"emitted.txt").write_text(selected,encoding="utf-8",newline="\n")
            BASE.save(lane/"shared-report-before-echo.json",gate.source_fact_report(txn))
    def echo(job):
        writer,cid=job["writer"],job["case"];lane=OUT/"transactions"/writer/cid
        selected=(lane/"emitted.txt").read_text(encoding="utf-8")
        prompt=lane/"echo-prompt.txt"
        prompt.write_text("交付门禁已完成emit。请将以下终稿逐字作为整条最终回复，不加说明，不调用工具，不改任何字、标点和换行：\n"+selected,encoding="utf-8")
        BASE.run_one(writer,prompt_path=prompt,run_root=OUT/"calls/echo"/cid)
        call=OUT/"calls/echo"/cid/writer/"attempt-01"
        receipt=CORE.read(call/"receipt.json")
        observed=(call/"final.txt").read_text(encoding="utf-8") if receipt["technical_completed"] else None
        report=gate.source_fact_report(lane/"txn",observed)
        BASE.save(lane/"shared-report.json",report)
        print(json.dumps({"writer":writer,"case":cid,"selected":report["selected"],"delivery_verified":report["delivery_verified"],"unresolved_ids":report["unresolved_ids"]}),flush=True)
    def lane(writer):
        for job in CORE.read(OUT/"repair-jobs.json"):
            if job["writer"]==writer: echo(job)
    with ThreadPoolExecutor(max_workers=5) as pool: list(pool.map(lane,CORE.PROVIDERS))

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["prepare","repair","consume-repair","verdict","consume-verdict","emit"]);args=parser.parse_args()
    if args.action=="prepare": prepare()
    elif args.action in {"repair","verdict"}: run_phase(args.action)
    elif args.action.startswith("consume-"): consume(args.action.removeprefix("consume-"))
    else: emit()

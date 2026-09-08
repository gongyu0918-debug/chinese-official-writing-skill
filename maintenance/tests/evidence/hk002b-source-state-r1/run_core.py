"""Exercise frozen production detect/repair/verdict/emit with real CLI replies."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / "output/hk002b-core-r1"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

BASE = load("hk002b_cli_driver", HERE / "prototype.py")
PROVIDERS = list(BASE.MODELS)
VERIFIERS = {p: PROVIDERS[(i+1) % len(PROVIDERS)] for i,p in enumerate(PROVIDERS)}

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def modules():
    product = OUT / "product/chinese-official-writing"
    return (load("hk002b_frozen_gate", product / "scripts/review_gate.py"),
            load("hk002b_frozen_stop", product / "hooks/core/gate_stop_hook.py"))

def prepare():
    OUT.mkdir(parents=True,exist_ok=False)
    product = OUT / "product/chinese-official-writing"
    shutil.copytree(ROOT / "chinese-official-writing",product,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    manifest = [{"path":p.relative_to(product).as_posix(),"sha256":BASE.sha(p.read_bytes())} for p in sorted(product.rglob("*")) if p.is_file()]
    BASE.save(OUT / "product-manifest.json",manifest)
    cases = read(BASE.OUT / "cases.json")
    BASE.save(OUT / "cases.json",cases)
    gate, hook = modules()
    for provider in PROVIDERS:
        jobs=[]
        for case in cases:
            lane = OUT / "transactions" / provider / case["id"]
            lane.mkdir(parents=True)
            for key in ("request","source","draft"):
                (lane/(key+".txt")).write_text(case[key],encoding="utf-8",newline="\n")
            txn=lane/"txn"
            state=gate.detect_transaction(lane/"request.txt",lane/"draft.txt",[lane/"source.txt"] if case["source"] else [],txn,1800,1800)
            if state["state"]==gate.STATE_AWAITING_REPAIR:
                instruction=hook._repair_instruction(txn)
                assert instruction
                jobs.append({"id":case["id"],"instruction":instruction,"context":{k:case[k] for k in ("request","source","draft")}})
            BASE.save(lane/"initial-state.json",state)
        write_batch(OUT/"prompts"/provider/"repair.txt",jobs)
    BASE.save(OUT/"freeze.json",{"base":"f69534f05a2ae8c2da4f39d35a35497a90d0efff","models":BASE.MODELS,"verifier_routes":VERIFIERS,"effort":"max","cases":len(cases),"frozen_files":len(manifest),"native_host_installation_tested":False,"method":"Frozen canonical core lifecycle with fresh Codex CLI repair and separate-route verification; exact final echoes separately recorded."})
    print(json.dumps({"prepared":True,"product_files":len(manifest),"repair_jobs":{p:len(read_jobs(p,'repair')) for p in PROVIDERS}}),flush=True)

def write_batch(path,jobs):
    BASE.save(path.with_suffix(".jobs.json"),jobs)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("各job相互独立，逐项执行instruction。只返回JSON对象{\"results\":[{\"id\":\"job id\",\"response\":该job要求的JSON对象}]}。不要用工具、读文件、联网、返回正文或增添解释。各job数据不互相借用。\n"+json.dumps({"jobs":jobs},ensure_ascii=False),encoding="utf-8")

def read_jobs(provider,phase):
    return read(OUT/"prompts"/provider/(phase+".jobs.json"))

def assert_frozen():
    product=OUT/"product/chinese-official-writing"
    assert all(BASE.sha((product/row["path"]).read_bytes())==row["sha256"] for row in read(OUT/"product-manifest.json"))

def run_phase(phase):
    assert_frozen()
    def lane(writer):
        jobs=read_jobs(writer,phase)
        if not jobs: return
        provider=writer if phase=="repair" else VERIFIERS[writer]
        BASE.run_one(provider,prompt_path=OUT/"prompts"/writer/(phase+".txt"),run_root=OUT/"calls"/phase/writer)
    with ThreadPoolExecutor(max_workers=5) as pool: list(pool.map(lane,PROVIDERS))

def replies(writer,phase,hook):
    provider=writer if phase=="repair" else VERIFIERS[writer]
    path=OUT/"calls"/phase/writer/provider/"attempt-01"
    if not path.exists(): return {}
    receipt=read(path/"receipt.json")
    if not receipt["technical_completed"]: return {}
    raw=(path/"final.txt").read_text(encoding="utf-8")
    payload=hook._extract_json_object(raw)
    if not isinstance(payload,dict) or set(payload)!={"results"} or not isinstance(payload["results"],list): return {}
    results={}
    for row in payload["results"]:
        if not isinstance(row,dict) or set(row)!={"id","response"} or row["id"] in results or not isinstance(row["response"],dict): return {}
        results[row["id"]]=row["response"]
    if set(results)!={j["id"] for j in read_jobs(writer,phase)}: return {}
    return results

def consume(phase):
    assert_frozen();gate,hook=modules();cases=read(OUT/"cases.json");summary=[]
    for writer in PROVIDERS:
        outputs=replies(writer,phase,hook);jobs=[]
        for case in cases:
            lane=OUT/"transactions"/writer/case["id"];txn=lane/"txn"
            state=read(txn/gate.STATE_FILE)
            expected=gate.STATE_AWAITING_REPAIR if phase=="repair" else gate.STATE_AWAITING_VERDICT
            if state["state"]!=expected: continue
            response=outputs.get(case["id"])
            response_path=lane/(phase+"-response.json")
            if response is not None: BASE.save(response_path,response)
            if phase=="repair":
                state=gate.prepare_transaction(txn,response_path if response is not None else None)
                if state["state"]==gate.STATE_AWAITING_VERDICT:
                    instruction=hook._verdict_instruction(txn);assert instruction
                    jobs.append({"id":case["id"],"instruction":instruction,"context":{k:case[k] for k in ("request","source","draft")}})
            else:
                state=gate.finalize_transaction(txn,response_path if response is not None else None)
            BASE.save(lane/(phase+"-state.json"),state)
            summary.append({"writer":writer,"case":case["id"],"state":state["state"],"selected":state.get("selected"),"reason":state["reason"]})
        if phase=="repair": write_batch(OUT/"prompts"/writer/"verdict.txt",jobs)
    BASE.save(OUT/(phase+"-summary.json"),summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)

def emit():
    assert_frozen();gate,hook=modules();cases=read(OUT/"cases.json")
    for writer in PROVIDERS:
        for case in cases:
            lane=OUT/"transactions"/writer/case["id"];txn=lane/"txn"
            state=read(txn/gate.STATE_FILE)
            if state["state"] not in gate.TERMINAL_STATES:
                state=gate.abort_transaction(txn,"prototype_unfinished")
            stdout=io.StringIO()
            with redirect_stdout(stdout): text=gate.emit_transaction(txn)
            assert stdout.getvalue()==text
            (lane/"emitted.txt").write_text(text,encoding="utf-8",newline="\n")
            BASE.save(lane/"shared-report-before-echo.json",gate.source_fact_report(txn))
    def echo(job):
        writer,cid=job;lane=OUT/"transactions"/writer/cid
        prompt=lane/"echo-prompt.txt"
        selected=(lane/"emitted.txt").read_text(encoding="utf-8")
        prompt.write_text("交付门禁已完成emit。请将以下终稿逐字作为整条最终回复，不加说明，不调用工具，不改任何字、标点和换行：\n"+selected,encoding="utf-8")
        BASE.run_one(writer,prompt_path=prompt,run_root=OUT/"calls"/"echo"/cid)
        call=OUT/"calls"/"echo"/cid/writer/"attempt-01"
        receipt=read(call/"receipt.json")
        observed=(call/"final.txt").read_text(encoding="utf-8") if receipt["technical_completed"] else None
        report=gate.source_fact_report(lane/"txn",observed)
        BASE.save(lane/"shared-report.json",report)
        print(json.dumps({"writer":writer,"case":cid,"selected":report["selected"],"delivery_verified":report["delivery_verified"],"unresolved_ids":report["unresolved_ids"]}),flush=True)
    jobs=[(writer,cid) for writer in PROVIDERS for cid in ("ongoing_counterexample","real_condition")]
    with ThreadPoolExecutor(max_workers=5) as pool: list(pool.map(echo,jobs))

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["prepare","repair","consume-repair","verdict","consume-verdict","emit"]);args=parser.parse_args()
    if args.action=="prepare": prepare()
    elif args.action in {"repair","verdict"}: run_phase(args.action)
    elif args.action.startswith("consume-"): consume(args.action.removeprefix("consume-"))
    else: emit()

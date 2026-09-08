"""Derive call counts and exact handoff sample paths from archived evidence."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def read(path): return json.loads(path.read_text(encoding="utf-8"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")

def main():
    routes=read(HERE/"raw/prototype/freeze.json")["models"]
    receipts=[read(p) for p in sorted((HERE/"raw").rglob("receipt.json"))]
    assert len(receipts)==42
    for r in receipts:
        assert r["requested_model"]==routes[r["provider"]]
        assert r["effort"]=="max" and r["technical_completed"] and r["tool_count"]==0
        assert r["host_turn_context"]==[{"model":routes[r["provider"]],"effort":"max"}]
    rows=[]
    for writer in routes:
        for cid in ("real_condition","ongoing_counterexample"):
            p=HERE/"raw/core-r2/transactions"/writer/cid/"shared-report.json"
            report=read(p)
            rows.append({"writer":writer,"case":cid,"selected":report["selected"],"candidate_verdict":report["candidate_verdict"],"delivery_verified":report["delivery_verified"],"delivered_corrections":sum(f["delivered_issue_resolved"] is True for f in report["findings"]),"unresolved_ids":report["unresolved_ids"]})
    save(HERE/"summary.json",{"models":routes,"effort":"max","cli_calls":len(receipts),"technical_cli_completed":len(receipts),"upstream_response_model_observed":False,"calls_by_route":{p:sum(r["provider"]==p for r in receipts) for p in routes},"r2":rows,"actual_corrected_deliveries":sum(r["selected"]=="D1" and r["delivery_verified"] and r["delivered_corrections"]==1 for r in rows),"retained_d0":sum(r["selected"]=="D0" for r in rows),"exact_echoes":sum(r["delivery_verified"] for r in rows)})
    samples=[]
    for writer,cid,kind,verifier in (("opencode","ongoing_counterexample","pass_delivered","ollama"),("opencode","real_condition","pass_delivered_request_as_material","ollama"),("minimax","ongoing_counterexample","d0_unresolved_invalid_verdict","opencode")):
        lane=HERE/"raw/core-r2/transactions"/writer/cid
        report=read(lane/"shared-report.json")
        inputs={}
        for name,filename in (("request","request.snapshot.txt"),("source","source.snapshot.txt"),("d0","d0.snapshot.txt"),("d1","d1.candidate.txt")):
            path=lane/"txn"/filename
            assert sha(path)==report[name+"_sha256"]
            inputs[name]={"path":path.relative_to(HERE).as_posix(),"sha256":sha(path),"bytes":path.stat().st_size}
        samples.append({"kind":kind,"inputs":inputs,"report":(lane/"shared-report.json").relative_to(HERE).as_posix(),"original_verdict":f"raw/core-r2/calls/verdict/{cid}/{writer}/{verifier}/attempt-01/final.txt","actual_echo":f"raw/core-r2/calls/echo/{cid}/{writer}/attempt-01/final.txt","selected":report["selected"],"delivery_verified":report["delivery_verified"],"unresolved_ids":report["unresolved_ids"]})
    save(HERE/"samples.json",samples)
    print(json.dumps({"calls":len(receipts),"corrected_deliveries":sum(r["delivered_corrections"] for r in rows),"exact_echoes":sum(r["delivery_verified"] for r in rows),"samples":len(samples)}))

if __name__=="__main__": main()

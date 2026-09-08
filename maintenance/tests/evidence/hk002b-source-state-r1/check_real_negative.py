"""One independent verifier probe of an unchanged, real failed model repair."""
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("hk002b_single_driver",HERE/"run_single_core.py")
RUN=importlib.util.module_from_spec(spec);sys.modules[spec.name]=RUN;spec.loader.exec_module(RUN)

def main():
    RUN.CORE.assert_frozen();gate,hook=RUN.CORE.modules()
    case=next(c for c in RUN.CORE.read(RUN.OUT/"cases.json") if c["id"]=="real_condition")
    raw=(RUN.BASE.OUT/"runs/ali1/attempt-01/final.txt").read_text(encoding="utf-8")
    proposal=next(c for c in json.loads(raw)["cases"] if c["id"]==case["id"])["findings"][0]
    lane=RUN.OUT/"negative-real-proposal";lane.mkdir(parents=True,exist_ok=False)
    for key in ("request","source","draft"):
        (lane/(key+".txt")).write_text(case[key],encoding="utf-8",newline="\n")
    txn=lane/"txn"
    gate.detect_transaction(lane/"request.txt",lane/"draft.txt",[],txn,1800,1800)
    packet=gate.read_json(txn/gate.REPAIR_PACKET_FILE)
    repairs=[];assessments=[]
    for finding in packet["findings"]:
        target=finding["target"]
        replacement=target
        if finding.get("source_relation"):
            assert proposal["draft_quote"] in target
            replacement=target.replace(proposal["draft_quote"],proposal["replacement"])
            assessments.append({"finding_id":finding["finding_id"],"status":"error","reason":proposal["relation"]})
        repairs.append({"finding_id":finding["finding_id"],"target":target,"decision":"REWRITE" if replacement!=target else "KEEP","replacement":replacement})
    response={"schema_version":packet["response_schema_version"],**{k:packet[k] for k in ("run_id","request_sha256","source_sha256","draft_sha256")},"revision_count":1,"repair_mode":"decisions","repairs":repairs,"source_assessments":assessments}
    RUN.BASE.save(lane/"repair-response.json",response)
    state=gate.prepare_transaction(txn,lane/"repair-response.json")
    RUN.BASE.save(lane/"repair-state.json",state)
    if state["state"]==gate.STATE_AWAITING_VERDICT:
        instruction=hook._verdict_instruction(txn);assert instruction
        prompt=lane/"verdict-prompt.txt";prompt.write_text(instruction+"\n不要使用工具或读取文件。",encoding="utf-8")
        receipt=RUN.BASE.run_one("ollama",prompt_path=prompt,run_root=lane/"calls")
        call=lane/"calls/ollama/attempt-01"
        verdict=hook._extract_json_object((call/"final.txt").read_text(encoding="utf-8")) if receipt["technical_completed"] else None
        path=lane/"verdict-response.json"
        if isinstance(verdict,dict): RUN.BASE.save(path,verdict)
        state=gate.finalize_transaction(txn,path if isinstance(verdict,dict) else None)
    RUN.BASE.save(lane/"result.json",{"proposal_origin":"prototype/ali1/attempt-01/final.txt real_condition","proposal_sha256":RUN.BASE.sha(raw.encode()),"synthesized_new_replacement":False,"new_repair_model_calls":0,"state":state,"report":gate.source_fact_report(txn)})
    print(json.dumps({"selected":state["selected"],"reason":state["reason"]}),flush=True)

if __name__=="__main__": main()

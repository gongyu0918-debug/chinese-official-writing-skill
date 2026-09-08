"""Reuse the committed extractor and retain exact manuscripts plus observed isolation."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

def main(round_name):
    evidence = ROOT / 'maintenance/tests/evidence' / ({'boundary-r4':'speech-role-boundary-r4','route-r6':'speech-role-route-r6','route-r7':'speech-role-route-r7','final-r6':'speech-role-r6-final-smoke','sol-r8':'speech-sol-check-r8','minimal-r9':'speech-viewpoint-minimal-r9'}.get(round_name, 'speech-role-leaf-' + round_name))
    spec = importlib.util.spec_from_file_location('speech_run', evidence / 'run_real.py')
    run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run)
    extractor = run.load(run.EXTRACTOR)
    extractor.ROOT, extractor.SOURCE, extractor.DEST, extractor.MODELS = ROOT, run.OUT, evidence / 'actual', run.MODELS
    extractor.DEST.mkdir(exist_ok=True)
    extractor.put('.gitattributes', b'* -text -whitespace\n')
    rows = []
    arms = ('baseline', 'candidate') if round_name in ('r1','boundary-r4','sol-r8') else ('candidate',)
    for case in run.CASES:
        for provider in run.MODELS:
            for arm in arms:
                lane = run.OUT / 'runs' / case / provider / arm
                if not (lane / 'receipt.json').exists():
                    continue
                receipt = json.loads((lane / 'receipt.json').read_text(encoding='utf-8'))
                assert all(t['name'] in ('Read','Skill') for t in receipt['tool_uses'])
                assert all(t['input'].get('skill') == 'official-writing-eval:chinese-official-writing' for t in receipt['tool_uses'] if t['name'] == 'Skill')
                row = extractor.archive_lane(lane)
                events = [json.loads(l) for l in (lane / 'stream.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
                inits = [x for x in events if x.get('type') == 'system' and x.get('subtype') == 'init']
                assert len(inits) == 1 and inits[0].get('mcp_servers') == []
                hooks = [x for x in events if str(x.get('subtype','')).startswith('hook_')]
                assert not hooks
                for tool in row.get('tool_evidence',[]):
                    assert tool.get('name') in ('Read','Skill')
                target = extractor.DEST / row['receipt']
                compact = json.loads(target.read_text(encoding='utf-8'))
                assert all(t.get('scope') == 'package' or (t.get('scope') == 'failed_read' and t.get('requested_scope') == 'package') or t['name'] == 'Skill' for t in compact['tool_evidence'])
                memory_files = list((lane / 'runtime').rglob('MEMORY.md'))
                observation = {'mcp_servers': [], 'hook_events_observed': len(hooks), 'runtime_memory_files': len(memory_files), 'skill_catalog': inits[0].get('skills',[]), 'cli_version': inits[0].get('claude_code_version'), 'stream_sha256':run.sha((lane/'stream.jsonl').read_bytes()), 'scope':'Read stayed within frozen package; any absent baseline leaf remained a failed read.'}
                compact['isolation_observed'] = observation
                extractor.save(row['receipt'], compact)
                assert (extractor.DEST / compact['final_path']).read_bytes() == (lane / 'final.txt').read_bytes()
                rows.append(row)
    for arm in ('baseline','candidate'):
        manifest = json.loads((run.OUT / (arm + '-manifest.json')).read_text(encoding='utf-8'))
        extractor.save('manifests/' + arm + '.json', manifest)
        for rel in run.OVERLAYS:
            source = run.OUT / 'plugins' / arm / 'skills/chinese-official-writing' / rel
            if source.exists():
                extractor.put('snapshots/' + arm + '/' + rel, source.read_bytes())
    extractor.put('freeze.json', (run.OUT/'freeze.json').read_bytes())
    expected = len(run.CASES) * len(run.MODELS) * len(arms)
    extractor.save('summary.json',{'round':round_name,'expected':expected,'attempts_completed':len(rows),'technical_valid':sum(x['technical_valid'] for x in rows),'complete':len(rows)==expected,'runs':rows,'quality':'Read manuscripts; technical validity is not writing quality.'})
    print(json.dumps({'round':round_name,'completed':len(rows),'expected':expected,'technical_valid':sum(x['technical_valid'] for x in rows)}))

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('round',choices=['r1','r2','r3','r4','r5','r8','boundary-r4','route-r6','route-r7','final-r6','sol-r8','minimal-r9']);main(parser.parse_args().round)

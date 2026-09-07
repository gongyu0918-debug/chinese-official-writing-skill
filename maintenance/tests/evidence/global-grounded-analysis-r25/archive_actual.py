"""Archive actual R25 lanes with the fixed R23 extractor; no manuscript rewriting."""
import argparse
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r25_run', HERE / 'run_real.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
FORBIDDEN = rb'(?<![A-Za-z])[A-Za-z]:[\\/]|-----BEGIN .*PRIVATE KEY|(?i:authorization\s*:\s*bearer)'


def archive_invalid(extractor, lane):
    """Keep failed/scope-invalid observations without importing outside-work files."""
    receipt, invocation = extractor.read_json(lane / 'receipt.json'), extractor.read_json(lane / 'invocation.json')
    case, provider, arm = lane.relative_to(run.OUT / 'runs').parts
    assert (case, provider, arm) == (receipt['case'], receipt['provider'], receipt['arm'])
    assert receipt['model'] == run.MODELS[provider]
    assert receipt['session'] == invocation['session'] and not invocation['hook_enabled']
    prompt = run.OUT / 'prompts' / (case + '.txt')
    assert invocation['prompt'] == prompt.read_text(encoding='utf-8')
    prefix = f'runs/{case}/{provider}/{arm}'
    source_final = (lane / 'final.txt').read_bytes()
    assert run.sha((lane / 'final.txt').read_text(encoding='utf-8').encode()) == receipt['final_sha256']
    work = (lane / 'runtime/work').resolve()
    approved_prefix = rb'[\\/]'.join(re.escape(part.encode()) for part in work.as_posix().split('/'))
    final, redactions = re.subn(approved_prefix + rb'(?=[\\/])', b'<isolated-work>', source_final, flags=re.I)
    assert not re.search(FORBIDDEN, final), 'Manually review invalid final before archiving'
    extractor.put('prompts/' + case + '.txt', prompt.read_bytes())
    extractor.put(prefix + '/final.txt', final)
    documents = []
    for path in sorted(work.rglob('*')):
        if not path.is_file():
            continue
        assert path.resolve().is_relative_to(work) and not path.is_symlink()
        data = path.read_bytes()
        assert not re.search(FORBIDDEN, data), 'Manually review invalid working artifact before archiving'
        target = f'{prefix}/working-file-{len(documents) + 1}{path.suffix}'
        extractor.put(target, data)
        documents.append({'work_relative_path': path.relative_to(work).as_posix(),
            'archive_path': target, 'sha256': run.sha(data), 'bytes': len(data),
            'delivery_state': 'invalid_scope_diagnostic' if receipt['technical_valid'] else 'interrupted_working_file_not_final_delivery'})
    compact = {key: receipt[key] for key in ('arm', 'provider', 'model', 'case', 'session',
        'technical_valid', 'return_code', 'failure', 'seconds', 'frozen_unchanged',
        'final_chars', 'init_models', 'assistant_models', 'usage_models', 'result_count',
        'result_subtypes', 'result_errors')}
    compact.update(source_receipt_sha256=run.sha((lane / 'receipt.json').read_bytes()),
        final_path=prefix + '/final.txt', final_sha256=run.sha(final), source_final_sha256=run.sha(source_final),
        final_redaction={'replacement_count': redactions, 'archive_is_original_bytes': redactions == 0,
                        'scope': 'Only this lane approved runtime/work prefix; source bytes unchanged.'},
        documents=documents, hook_enabled=False, paired_quality_eligible=False,
        omissions=['outside-work memory files', 'raw stream', 'runtime configuration', 'original argv', 'tool arguments'],
        observation='All remaining files inside this lane work are retained; no claim that interrupted files were delivered.')
    assert not re.search(FORBIDDEN, json.dumps(compact, ensure_ascii=False).encode()), 'Review invalid receipt before archiving'
    extractor.save(prefix + '/receipt.json', compact)
    return {'case': case, 'provider': provider, 'arm': arm, 'technical_valid': receipt['technical_valid'],
        'receipt': prefix + '/receipt.json', 'artifacts': len(documents), 'quality_eligible': False}


def archive(provider, verify_only=False):
    extractor = run.load(run.EXTRACTOR)
    extractor.ROOT, extractor.SOURCE, extractor.DEST = run.ROOT, run.OUT, HERE / ('actual-' + provider)
    extractor.BLIND, extractor.CASES, extractor.MODELS = HERE / ('blind-' + provider), run.CASES, run.MODELS
    extractor.SEED = 'r25-global-analysis-v1'
    if verify_only:
        return verify(extractor, provider)
    audit = json.loads((run.OUT / 'scope-audit.json').read_text(encoding='utf-8'))
    lanes = [run.OUT / 'runs' / case / provider / arm for case in run.CASES for arm in ('baseline', 'candidate')]
    for lane in lanes:
        assert (lane / 'receipt.json').is_file(), 'Provider profile still running'
        scope = audit['lanes'][lane.relative_to(run.OUT / 'runs').as_posix()]
        assert scope['source_receipt_sha256'] == run.sha((lane / 'receipt.json').read_bytes())
    extractor.DEST.mkdir(exist_ok=False)
    extractor.put('.gitattributes', b'* -text -whitespace\n')
    rows = []
    for case in run.CASES:
        for model in (provider,):
            for arm in ('baseline', 'candidate'):
                lane = run.OUT / 'runs' / case / model / arm
                scope = audit['lanes'][f'{case}/{model}/{arm}']
                assert scope['source_receipt_sha256'] == run.sha((lane / 'receipt.json').read_bytes())
                valid = extractor.read_json(lane / 'receipt.json')['technical_valid'] and scope['pass']
                row = extractor.archive_lane(lane) if valid else archive_invalid(extractor, lane)
                path = extractor.DEST / row['receipt']
                receipt = extractor.read_json(path)
                receipt['runner_technical_valid'] = receipt['technical_valid']
                receipt['scope_audit'] = scope
                receipt['technical_valid'] = receipt['technical_valid'] and scope['pass']
                assert not re.search(FORBIDDEN, json.dumps(receipt, ensure_ascii=False).encode()), 'Review bound receipt before archiving'
                row['technical_valid'] = receipt['technical_valid']
                row['scope_pass'] = scope['pass']
                extractor.save(row['receipt'], receipt)
                rows.append(row)
    for arm in ('baseline', 'candidate'):
        manifest = extractor.read_json(run.OUT / (arm + '-manifest.json'))
        package = run.OUT / 'plugins' / arm / 'skills/chinese-official-writing'
        for row in manifest:
            data = (package / row['path']).read_bytes()
            assert run.sha(data) == row['sha256'] and len(data) == row['bytes']
        extractor.save('manifests/' + arm + '.json', manifest)
        for name in run.OVERLAYS:
            extractor.put('snapshots/' + arm + '/' + name, (package / name).read_bytes())
    extractor.put('freeze.json', (run.OUT / 'freeze.json').read_bytes())
    extractor.save('summary.json', {'baseline_commit': run.BASELINE, 'attempts': len(rows),
        'technical_valid': sum(r['technical_valid'] for r in rows), 'runs': rows,
        'quality': 'Not judged by extractor; invalid scope samples remain in actual but excluded from paired blind delivery'})
    extractor.create_blind()
    verify(extractor, provider)
    print(json.dumps({'attempts': len(rows), 'technical_valid': sum(r['technical_valid'] for r in rows)}))


def verify(extractor, provider):
    manifest = extractor.read_json(extractor.DEST / 'archive-manifest.json')
    assert {p.relative_to(extractor.DEST).as_posix() for p in extractor.DEST.rglob('*') if p.is_file()} == {r['path'] for r in manifest} | {'archive-manifest.json'}
    for row in manifest:
        data = extractor.within(extractor.DEST / row['path'], extractor.DEST).read_bytes()
        assert run.sha(data) == row['sha256'] and len(data) == row['bytes']
    summary = extractor.read_json(extractor.DEST / 'summary.json')
    assert {(r['case'], r['provider'], r['arm']) for r in summary['runs']} == {(c, provider, a) for c in run.CASES for a in ('baseline', 'candidate')}
    for row in summary['runs']:
        receipt = extractor.read_json(extractor.DEST / row['receipt'])
        lane = run.OUT / 'runs' / row['case'] / provider / row['arm']
        assert receipt['scope_audit']['source_receipt_sha256'] == run.sha((lane / 'receipt.json').read_bytes())
        assert receipt['technical_valid'] == row['technical_valid'] == (receipt['runner_technical_valid'] and receipt['scope_audit']['pass'])
        assert run.sha((lane / 'final.txt').read_bytes()) == receipt['source_final_sha256']
        assert run.sha((extractor.DEST / receipt['final_path']).read_bytes()) == receipt['final_sha256']
        for doc in receipt['documents']:
            if doc['archive_path']:
                source = extractor.within(lane / 'runtime/work' / doc['work_relative_path'], lane / 'runtime/work').read_bytes()
                assert source == extractor.within(extractor.DEST / doc['archive_path'], extractor.DEST).read_bytes()
                assert run.sha(source) == doc['sha256'] and len(source) == doc['bytes']
    extractor.verify_blind()
    print(json.dumps({'provider': provider, 'archive_payload_files': len(manifest), 'source_bound_lanes': len(summary['runs']), 'status': 'PASS'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', choices=run.MODELS, required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    archive(args.provider, args.verify_only)

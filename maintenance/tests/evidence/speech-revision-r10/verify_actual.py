"""Verify archived bytes and observed isolation without copying provider state."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(round_name):
    source = ROOT / 'output' / round_name
    dest = ROOT / 'maintenance/tests/evidence' / round_name / 'actual'
    rows = []
    for receipt_path in sorted(dest.glob('runs/*/*/*/receipt.json')):
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        lane = source / receipt_path.parent.relative_to(dest)
        raw = (lane / 'stream.jsonl').read_bytes()
        events = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
        inits = [e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init']
        assert len(inits) == 1
        init = inits[0]
        assert init.get('mcp_servers') == []
        assert set(init['tools']) == {'Read', 'Skill'}
        assert Path(init['cwd']).resolve() == (lane / 'runtime/work').resolve()
        assert not any(str(e.get('subtype', '')).startswith('hook_') for e in events)
        assert not list((lane / 'runtime').rglob('MEMORY.md'))
        for tool in receipt['tool_evidence']:
            assert tool['name'] in ('Read', 'Skill')
            if tool['name'] == 'Skill':
                assert tool['skill_name'] == 'official-writing-eval:chinese-official-writing'
            else:
                assert tool.get('scope') == 'package' or (tool.get('scope') == 'failed_read' and tool.get('requested_scope') == 'package')
        manuscript = (lane / 'final.txt').read_bytes()
        assert manuscript == (dest / receipt['final_path']).read_bytes()
        assert sha(manuscript) == receipt['final_sha256']
        arm = receipt['arm']
        manifest = json.loads((source / f'{arm}-manifest.json').read_text(encoding='utf-8'))
        package = source / 'plugins' / arm / 'skills/chinese-official-writing'
        for file in manifest:
            assert sha((package / file['path']).read_bytes()) == file['sha256']
        for tool in receipt['tool_evidence']:
            if tool.get('read_success_observed'):
                assert sha((package / tool['package_path']).read_bytes()) == tool['frozen_file_sha256']
        entry = (package / 'SKILL.md').read_text(encoding='utf-8')
        user_texts = [b.get('text', '') for e in events if e.get('type') == 'user'
                      for b in (e.get('message') or {}).get('content', []) if isinstance(b, dict)]
        observation = {'cwd_matches_isolated_work': True, 'mcp_servers': [], 'hook_events': 0,
                       'runtime_memory_files': 0, 'model': receipt['model'],
                       'skill_catalog': init.get('skills', []), 'cli_version': init.get('claude_code_version'),
                       'native_full_entry_expansions': sum(entry in text for text in user_texts),
                       'stream_sha256': sha(raw), 'raw_final_bytes_verified': True,
                       'frozen_files_verified': len(manifest)}
        receipt['isolation_observed'] = observation
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        rows.append({'receipt': receipt_path.relative_to(dest).as_posix(), **observation})
    (dest / '.gitattributes').write_text('* -text -whitespace\n', encoding='utf-8')
    report = {'verified_runs': len(rows), 'rows': rows,
              'scope': 'Observed package-only reads, no MCP or Hook events; builtin skill catalog remains visible. Technical validity is not writing quality.'}
    (dest / 'isolation-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'round': round_name, 'verified_runs': len(rows)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('round')
    verify(parser.parse_args().round)

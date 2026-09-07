"""Replay final source binding against derived native user/read prefixes."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
path = ROOT / 'chinese-official-writing/hooks/shared/revision_context.py'
spec = importlib.util.spec_from_file_location('final_context_replay', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
rows = json.loads((HERE / 'continuity/final-parser-replay.json').read_text(encoding='utf-8'))
native_matches = 0
for row in rows:
    actual = module.recover(HERE / 'continuity' / row['prefix'], row['session'], row['current'], Path(row['skill_root']))
    assert (actual is not None) == row['final_parser_would_enter']
    if actual:
        assert actual['sha256'] == row['context']['sha256']
    if row['native_recorded']:
        assert actual['sha256'] == row['native_recorded']['sha256']
        native_matches += 1
print(json.dumps({'status': 'PASS', 'requests': len(rows), 'native_source_hash_matches': native_matches,
                  'method': 'offline replay of derived native prefixes; does not replace the recorded R3 round7 miss'}))

"""Repeat only the frozen main declaration prompt once; never call fallback."""
import hashlib
import json
from pathlib import Path
import runpy
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = Path(__file__).resolve().parent
    sys.argv = [str(evidence / 'run_atom.py'), str(evidence / 'diagnostics.json')]
    runner = runpy.run_path(str(evidence / 'run_atom.py'), run_name='statement_repeat_runner')
    assert runner['config']['baseline'] == 'e8103f53'
    assert runner['config']['candidate'] == 'e8103f53'
    assert runner['m'].MODELS[0] == 'minimax-cn/MiniMax-M3'
    original = runner['OUT'] / 'runs/0/public_statement/baseline/max'
    repeat = original / 'repeat1'
    assert not repeat.exists(), 'The sole repeat already exists; no additional call.'
    receipt = json.loads((original / 'receipt.json').read_text(encoding='utf-8'))
    assert receipt['valid_final'] and receipt['effort'] == 'max'
    prompt_hash = digest(original / 'prompt.txt')
    assert prompt_hash == receipt['prompt_sha256']
    original_final_hash = digest(original / 'final.txt')
    result = runner['one'](0, 'public_statement', 'baseline', repeat=True)
    assert digest(repeat / 'prompt.txt') == prompt_hash
    assert digest(original / 'final.txt') == original_final_hash
    print(json.dumps({'exact_prompt_match': True, 'original_final_unchanged': True,
                      'original_final_sha256': original_final_hash,
                      'repeat_final_sha256': digest(repeat / 'final.txt') if (repeat / 'final.txt').exists() else None,
                      'fallback_permitted': False}, ensure_ascii=False), flush=True)
    return 0 if result['valid_final'] else 2


if __name__ == '__main__':
    raise SystemExit(main())

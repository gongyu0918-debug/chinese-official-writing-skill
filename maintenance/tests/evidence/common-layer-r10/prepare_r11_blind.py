"""Prepare anonymous complete messages for an independent review of the length refinement."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / 'output/common-layer-native-r11-length'
DEST = ROOT / 'output/common-layer-blind-r11'
DEST.mkdir(exist_ok=True)
binding = json.loads((RUN / 'binding.json').read_text(encoding='utf-8-sig'))
pairs, mappings = [], []
for i, (model_index, case) in enumerate([(0, 'guards_grammar_quote'), (2, 'grammar_correct_control'), (2, 'guards_grammar_quote'), (0, 'grammar_correct_control')], 1):
    pair = {'id': f'L{i:02}', 'request': binding['cases'][case]}
    mapping = {'id': pair['id'], 'case': case, 'model_index': model_index}
    for letter, arm in zip('AB', ('candidate', 'baseline') if i in (1, 4) else ('baseline', 'candidate')):
        path = RUN / f'm{model_index}-{case}-{arm}.final.txt'
        raw = path.read_bytes()
        message = raw.decode('utf-8-sig')
        message = re.sub(r'(?:/)?C:/Users/admin/AppData/Local/Temp/[^\s)]+', '/<临时工作路径>', message, flags=re.I)
        pair[letter] = message
        mapping[letter] = {'arm': arm, 'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()}
    pairs.append(pair)
    mappings.append(mapping)
packet = {'scope': 'Compare actual corrected body and complete delivery separately. Respect the supplied task scope. Ordinary complete draft minimum is 80 nonspace characters; explicit limits and local or proofreading-only scope matter. A correct supplied paragraph need not be expanded just to create a new standalone manuscript. Allow grounded inference, ordinary stylistic alternatives and quoted text. Do not infer script execution from self-reports. Do not count masked file paths as inaccessible-delivery errors.', 'pairs': pairs}
for name, value in [('packet.json', packet), ('mapping.json', mappings)]:
    path = DEST / name
    assert not path.exists(), path
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(hashlib.sha256((DEST / 'packet.json').read_bytes()).hexdigest())

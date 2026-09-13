"""Correct one path-only validity false negative without altering its receipt."""
from pathlib import Path
import hashlib
import json
import re
import secrets

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / 'output/correspondence-purpose-native-r16'
DEST = ROOT / 'output/blind-r16/correspondence-restored'
assert not DEST.exists()
DEST.mkdir(parents=True)
receipt = RUN / 'm2-approval_request_letter-baseline.result.json'
raw_receipt = receipt.read_bytes()
row = json.loads(raw_receipt)
assert row['invalid'] == ['missing_skill_read_trace']
entry = (RUN / 'snapshots/main/SKILL.md').read_text(encoding='utf-8-sig').replace('\r\n', '\n').strip()
matches = [c for c in row['commands'] if c.get('exit_code') == 0 and entry in c.get('aggregated_output', '').replace('\r\n', '\n')]
assert matches
binding = json.loads((RUN / 'binding.json').read_text(encoding='utf-8'))
scope = json.loads((ROOT / 'output/blind-r16/correspondence/packet.json').read_text(encoding='utf-8'))['scope']
pair = {'id': 'P01', 'request': binding['cases']['approval_request_letter']}
mapping = {'id': 'P01', 'model': row['model'], 'case': row['case'], 'run': RUN.name}
arms = ['baseline', 'candidate']
if secrets.randbits(1):
    arms.reverse()
for label, arm in zip('AB', arms):
    final = RUN / f'm2-approval_request_letter-{arm}.final.txt'
    data = final.read_bytes()
    pair[label] = re.sub(r'(?:/)?C:[\\/]+Users[\\/]+admin[\\/]+AppData[\\/]+Local[\\/]+Temp[\\/]+[^\s)>]+', '/<临时工作路径>', data.decode('utf-8-sig'), flags=re.I)
    mapping[label] = {'arm': arm, 'file': final.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(data).hexdigest()}
correction = {'receipt': receipt.relative_to(ROOT).as_posix(), 'receipt_sha256': hashlib.sha256(raw_receipt).hexdigest(), 'original_invalid': row['invalid'], 'calibrated_invalid': [], 'proof': [{'id': c['id'], 'command': c['command'], 'returned_entry_sha256': hashlib.sha256(entry.encode()).hexdigest()} for c in matches], 'reason': '完整冻结SKILL.md已由成功命令返回；相对路径不构成漏读。原receipt、全文及初始排除记录保持原样。'}
for name, value in [('packet', {'scope': scope, 'pairs': [pair]}), ('mapping', [mapping]), ('calibration', correction)]:
    (DEST / f'{name}.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert receipt.read_bytes() == raw_receipt
print(json.dumps({'packet': str(DEST/'packet.json'), 'sha256': hashlib.sha256((DEST/'packet.json').read_bytes()).hexdigest(), 'calibrated_calls': 12, 'original_valid_calls': 11}))

"""Recover user materials for one bounded, explicitly revised Claude task."""
import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 4_000_000
MAX_TURNS = 8
MAX_CHARS = 40_000


def is_revision(text):
    # Route on the request paragraph, not action words inside supplied material.
    text = text.split('\n\n', 1)[0]
    if re.search(r"另(?:[一份篇个]|写|起草|做)|(?<![最更])新(?:任务|话题|报告|稿)|换[一份篇个]|先不写", text):
        return False
    if re.search(r"(?:删除|删掉|清理)[^。；\n]{0,12}(?:临时文件|缓存|临时目录|输出目录)", text):
        return False
    if re.search(r"(?:修改|改写|重写|润色|整理)(?:一下)?(?:下面|以下)(?:这|那)?[份篇]", text):
        return False
    return bool(re.search(r"修改|更正|改[为成得]|更新|补充|精简|删|压缩|压到|加.{0,8}段|调整|替换", text)
                and re.search(r"刚才|(?:上一|这)[稿版]|这件事|最新稿|保留最新|其他(?:内容|部分|段落)|其余.{0,20}保留", text))


def recover(path, session, current, skill_root):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        return None
    # Read a bounded snapshot even if the host appends after stat().
    with path.open('rb') as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        return None
    groups, pending = [], {}
    skill = skill_root.resolve()
    for line in raw.decode('utf-8').splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(item, dict) or item.get('sessionId') != session or item.get('isSidechain'):
            continue
        message = item.get('message') or {}
        if not isinstance(message, dict):
            continue
        content = message.get('content', [])
        if isinstance(content, str):
            text = content
            blocks = []
        elif isinstance(content, list):
            blocks = [b for b in content if isinstance(b, dict)]
            text = ''.join(b.get('text', '') for b in blocks if b.get('type') == 'text')
        else:
            continue
        if item.get('type') == 'user' and text.strip() and not item.get('isMeta'):
            if not text.lstrip().startswith(('Stop hook feedback:', '<local-command', '<command-')):
                groups.append({'prompt': text.strip(), 'skill_seen': False})
        for block in blocks:
            if block.get('type') == 'tool_use' and groups:
                value = block.get('input') or {}
                if not isinstance(value, dict):
                    continue
                command = value.get('file_path') if block.get('name') == 'Read' else None
                if (isinstance(command, str) and isinstance(block.get('id'), str)
                        and block['id'] and Path(command).resolve().is_relative_to(skill)):
                    pending[block.get('id')] = groups[-1]
            if block.get('type') == 'tool_result' and block.get('tool_use_id') in pending:
                group = pending.pop(block['tool_use_id'])
                if block.get('is_error') is not True:
                    group['skill_seen'] = True
    if not groups or groups[-1]['prompt'] != current.strip() or not is_revision(current):
        return None
    start = len(groups) - 1
    while start and is_revision(groups[start]['prompt']):
        start -= 1
    chain = groups[start:]
    if not 2 <= len(chain) <= MAX_TURNS or not chain[0]['skill_seen']:
        return None
    if sum(len(g['prompt']) for g in chain) > MAX_CHARS:
        return None
    source = '以下为本篇稿按时间排列的用户材料与修改要求；后续明确更正、删除替代此前相冲突内容，不把旧稿当事实来源。\n\n'
    source += '\n\n'.join(f'【用户要求{i + 1}】\n{g["prompt"]}' for i, g in enumerate(chain))
    return {'source_text': source, 'turn_count': len(chain), 'sha256': hashlib.sha256(source.encode()).hexdigest()}

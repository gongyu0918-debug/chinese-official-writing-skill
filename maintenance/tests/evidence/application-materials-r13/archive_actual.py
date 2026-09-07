"""Archive completed R13 onward receipts; never run models or copy runtime state."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/application-materials-r13'
DEST = Path(__file__).resolve().parent / 'actual'
SNAPSHOTS = ('SKILL.md', 'references/handling-elements.md', 'references/argument-chains.md')
BASELINE = 'bb3eae9d69216f149737a00fd1126813cc7ef724'
FORBIDDEN_PARTS = {'runtime', 'auth', 'auth.json', 'credentials', 'credentials.json',
                   '.credentials', '.credentials.json', 'stream.jsonl', 'invocation.json'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def within(path, root):
    resolved = path.resolve()
    resolved.relative_to(root.resolve())
    return resolved


def put(relative, data):
    path = within(DEST / relative, DEST)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return relative


def save(relative, value):
    return put(relative, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def tool_results(lane):
    results = {}
    with (lane / 'stream.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            for block in (event.get('message') or {}).get('content', []):
                if isinstance(block, dict) and block.get('type') == 'tool_result':
                    content = json.dumps(block.get('content'), ensure_ascii=False).encode()
                    launch = re.fullmatch(r'Launching skill: ([A-Za-z0-9_:-]+)', str(block.get('content', '')))
                    results[block['tool_use_id']] = {'observed': True, 'is_error_field': block.get('is_error'),
                                                   'content_bytes': len(content), 'content_sha256': sha(content),
                                                   'skill_launch_acknowledgement': launch.group(1) if launch else None}
    return results


def file_scope(raw, package, work, allow_package):
    path = Path(raw)
    if not path.is_absolute():
        path = work / path
    if allow_package:
        try:
            resolved = within(path, package)
            return 'package', resolved, resolved.relative_to(package.resolve()).as_posix()
        except ValueError:
            pass
    resolved = within(path, work)
    return 'work', resolved, resolved.relative_to(work.resolve()).as_posix()


def archive_lane(lane):
    receipt, invocation = read_json(lane / 'receipt.json'), read_json(lane / 'invocation.json')
    case, provider, arm = lane.relative_to(SOURCE / 'runs').parts
    assert (case, provider, arm) == (receipt['case'], receipt['provider'], receipt['arm'])
    prompt = SOURCE / 'prompts' / (case + '.txt')
    assert invocation['prompt'] == prompt.read_text(encoding='utf-8')
    assert receipt['session'] == invocation['session'] and not invocation['hook_enabled']
    put(f'prompts/{case}.txt', prompt.read_bytes())
    prefix = f'runs/{case}/{provider}/{arm}'
    source_final = (lane / 'final.txt').read_bytes()
    assert sha((lane / 'final.txt').read_text(encoding='utf-8').encode()) == receipt['final_sha256']
    work = within(lane / 'runtime/work', lane / 'runtime')
    approved_prefix = rb'[\\/]'.join(re.escape(part.encode()) for part in work.as_posix().split('/'))
    final, redactions = re.subn(approved_prefix + rb'(?=[\\/])', b'<isolated-work>', source_final, flags=re.I)
    put(f'{prefix}/final.txt', final)
    package = SOURCE / 'plugins' / arm / 'skills/chinese-official-writing'
    results = tool_results(lane)
    tools, reads, documents = [], [], {}
    for number, use in enumerate(receipt['tool_uses'], 1):
        name, arg = use['name'], use.get('input', {})
        event = {'sequence': number, 'id': use['id'], 'name': name,
                 'result': results.get(use['id'], {'observed': False})}
        if name in ('Read', 'Write', 'Edit'):
            try:
                scope, path, relative = file_scope(arg['file_path'], package, work, name == 'Read')
            except ValueError:
                if name != 'Read' or not event['result'].get('observed') or event['result'].get('is_error_field') is not True:
                    raise
                event.update(scope='unresolved_failed_read', file_path_sha256=sha(arg['file_path'].encode()),
                             canonical_input_sha256=sha(json.dumps(arg, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()))
                tools.append(event)
                continue
            event['scope'] = scope
            if scope == 'package':
                event.update(package_path=relative, frozen_file_sha256=sha(path.read_bytes()))
                event['read_success_observed'] = event['result'].get('observed') is True and event['result'].get('is_error_field') is not True
                if event['read_success_observed']:
                    reads.append(relative)
            else:
                if relative not in documents:
                    exists = path.is_file()
                    data = path.read_bytes() if exists else None
                    artifact = f'{prefix}/document-{len(documents) + 1}.txt' if exists else None
                    if exists:
                        put(artifact, data)
                    documents[relative] = {
                        'work_relative_path': relative, 'archive_path': artifact,
                        'sha256': sha(data) if exists else None, 'bytes': len(data) if exists else None,
                        'file_state': 'last_on_disk_artifact' if exists else 'missing_not_archived',
                        'delivery_state': 'completed_run_artifact_quality_unreviewed' if receipt['technical_valid'] else 'interrupted_working_artifact_not_final_delivery',
                        'read_sequences': [], 'write_sequences': [], 'edit_sequences': [],
                    }
                documents[relative][name.lower() + '_sequences'].append(number)
                event.update(work_relative_path=relative, archive_path=documents[relative]['archive_path'])
            for key in ('offset', 'limit', 'replace_all'):
                if key in arg:
                    event[key] = arg[key]
            for key in ('content', 'old_string', 'new_string'):
                if key in arg:
                    event[key + '_sha256'] = sha(arg[key].encode())
        elif name == 'Bash':
            event.update(command_sha256=sha(arg.get('command', '').encode()), arguments_omitted=True)
        elif name == 'Skill':
            skill = arg.get('skill', '')
            assert re.fullmatch(r'[A-Za-z0-9_:-]+', skill), 'Unexpected Skill identifier'
            acknowledged = event['result'].get('skill_launch_acknowledgement') == skill
            event.update(skill_name=skill, launch_success_observed=acknowledged and event['result'].get('is_error_field') is not True,
                         response_visibility='launch_acknowledgement_only_no_skill_body' if acknowledged else 'response_summary_only_body_exposure_not_established')
        tools.append(event)
    compact = {key: receipt[key] for key in (
        'arm', 'provider', 'model', 'case', 'session', 'technical_valid', 'return_code', 'failure',
        'seconds', 'client_tools', 'explicit_entry', 'frozen_unchanged', 'final_chars',
        'init_models', 'assistant_models', 'usage_models', 'result_count', 'result_subtypes', 'result_errors')}
    compact.update(final_path=f'{prefix}/final.txt', final_sha256=sha(final),
                   source_final_sha256=sha(source_final), source_final_logical_sha256=receipt['final_sha256'],
                   final_redaction={'replacement_count': redactions, 'replacement': '<isolated-work>',
                                    'scope': 'Only this lane approved runtime/work prefix; slash variants accepted.',
                                    'source_unchanged': True, 'archive_is_original_bytes': redactions == 0}, hook_enabled=False,
                   timeout_seconds=480, automatic_retries=0, effort='max',
                   invalid_json_line_count=len(receipt['invalid_json_lines']), reads=reads,
                   tool_evidence=tools, documents=list(documents.values()),
                   helper_sha256=invocation['helper_sha256'], prompt_path=f'prompts/{case}.txt',
                   omissions=['raw stream', 'runtime', 'provider state', 'original argv', 'absolute paths', 'shell arguments and stdout'])
    save(f'{prefix}/receipt.json', compact)
    return {'case': case, 'provider': provider, 'arm': arm, 'technical_valid': receipt['technical_valid'],
            'receipt': f'{prefix}/receipt.json', 'artifacts': sum(d['archive_path'] is not None for d in documents.values()),
            'written_documents': sum(bool(d['write_sequences'] or d['edit_sequences']) and d['archive_path'] is not None for d in documents.values()),
            'missing_work_files': sum(d['archive_path'] is None for d in documents.values()),
            'skill_read': 'SKILL.md' in reads, 'skill_launch_success_observed': any(t.get('launch_success_observed') for t in tools),
            'failed_read_count': sum(t['name'] == 'Read' and t['result'].get('is_error_field') is True for t in tools),
            'unresolved_failed_read_count': sum(t.get('scope') == 'unresolved_failed_read' for t in tools),
            'final_path_redactions': redactions, 'handling_elements_read': 'references/handling-elements.md' in reads,
            'ai_compute_read': 'references/ai-compute-docs.md' in reads}


def archive(arms):
    # Snapshot completed receipt paths once; never follow or wait for running calls.
    lanes = sorted(p.parent for p in (SOURCE / 'runs').glob('*/*/*/receipt.json')
                   if not arms or p.parent.name in arms)
    assert lanes, 'No completed receipts selected'
    selected = set(lanes)
    archived_lanes = {p.parent.relative_to(DEST / 'runs').as_posix()
                      for p in (DEST / 'runs').glob('*/*/*/receipt.json')}
    assert archived_lanes <= {p.relative_to(SOURCE / 'runs').as_posix() for p in lanes}, 'Selection excludes previously archived calls; rerun without --arms'
    unfinished = [p.parent.relative_to(SOURCE / 'runs').as_posix()
                  for p in (SOURCE / 'runs').glob('*/*/*/invocation.json')
                  if p.parent not in selected and (not arms or p.parent.name in arms)]
    put('.gitattributes', b'# Frozen evidence retains exact model bytes and whitespace.\n* -text -whitespace\n')
    summaries = [archive_lane(lane) for lane in lanes]
    manifests = []
    for arm in sorted({row['arm'] for row in summaries}):
        manifest = read_json(SOURCE / f'{arm}-manifest.json')
        package = SOURCE / 'plugins' / arm / 'skills/chinese-official-writing'
        assert len(manifest) == 41, 'Unexpected frozen package; inspect before archiving'
        for item in manifest:
            data = within(package / item['path'], package).read_bytes()
            assert len(data) == item['bytes'] and sha(data) == item['sha256']
        save(f'manifests/{arm}.json', manifest)
        manifests.append({'arm': arm, 'files_verified': len(manifest)})
        for name in SNAPSHOTS:
            put(f'snapshots/{arm}/{name}', within(package / name, package).read_bytes())
    summary = {'baseline_commit': BASELINE, 'attempts_archived': len(summaries),
               'technical_valid': sum(row['technical_valid'] for row in summaries),
               'technical_invalid': sum(not row['technical_valid'] for row in summaries),
               'artifacts': sum(row['artifacts'] for row in summaries),
               'written_documents': sum(row['written_documents'] for row in summaries),
               'missing_work_files': sum(row['missing_work_files'] for row in summaries),
               'final_path_redactions': sum(row['final_path_redactions'] for row in summaries),
               'failed_read_count': sum(row['failed_read_count'] for row in summaries),
               'unresolved_failed_read_count': sum(row['unresolved_failed_read_count'] for row in summaries),
               'unfinished_selected_lanes_not_counted': sorted(unfinished),
               'arm_filter': arms, 'frozen_manifests': manifests,
               'frozen_files_verified': sum(row['files_verified'] for row in manifests), 'runs': summaries,
               'limits': ['Technical validity and Read exposure do not establish writing quality or rule effectiveness.',
                          'Skill launch acknowledgement is recorded separately from Read SKILL; CLI may not expose the loaded Skill body.',
                          'Final responses may summarize delivery; referenced work files are separately preserved.',
                          'Work artifacts are final on-disk bytes, not reconstructed from Write or Edit inputs.',
                          'A Read-only work artifact is not labeled a written document.',
                          'Incomplete calls are excluded from attempt and validity counts; no model is started.']}
    save('summary.json', summary)
    put('README.md', f'''# 实际写稿证据

本次归档 {summary['attempts_archived']} 次已完成调用：技术有效 {summary['technical_valid']} 次、技术无效 {summary['technical_invalid']} 次。技术有效不等于写稿质量通过。

`runs/` 分开保留最终回复、脱敏 receipt 和实际工作稿；后者由 Read/Write/Edit 的路径核验为该次隔离工作目录内的文件，再读取最后落盘字节，不能用生成文件摘要冒充正文。缺失工作文件 {summary['missing_work_files']} 份；未完成调用见 [汇总](summary.json)，不算有效样本。

final 副本仅将该次已核准的工作目录前缀替换为 `<isolated-work>`，共 {summary['final_path_redactions']} 处；receipt 分列原文件与归档副本 SHA-256、替换数量。其余字节及实际工作稿不改。Skill 工具的启动确认单列记录；没有 Read SKILL 不等于没有加载，CLI 未回显正文时不能声称已直接观察完整正文。

超界且已有明确工具错误响应的 Read 仅登记为 `unresolved_failed_read`，保留参数哈希与响应观察，不读取范围外文件，不计入包曝光或文稿；本次共 {summary['unresolved_failed_read_count']} 次。成功或响应不明的超界读取仍拒绝归档。

`prompts/` 保留调用原提示；`manifests/` 保留冻结包清单；`snapshots/` 保留 SKILL.md、handling-elements.md 与 argument-chains.md 的实际冻结版本。本次验证 {summary['frozen_files_verified']} 项包文件哈希。未复制 runtime、授权、原始流、原 argv、shell 参数或输出、绝对机器路径。

[SHA-256 清单](archive-manifest.json) 覆盖本目录除清单自身外全部文件。运行 `python -B -X utf8 maintenance/tests/evidence/application-materials-r13/archive_actual.py --verify-only` 复核；暂存后可用 `--verify-index` 核验 Git 索引字节。重新归档仅处理现存 receipt。首次归档时可用 `--arms baseline candidate` 限定 R13；已有后续轮次归档时须不带 `--arms`，不得缩小已归档范围。
'''.encode())
    paths = [p for p in sorted(DEST.rglob('*')) if p.is_file() and p.name != 'archive-manifest.json']
    save('archive-manifest.json', [{'path': p.relative_to(DEST).as_posix(), 'bytes': p.stat().st_size,
                                   'sha256': sha(p.read_bytes())} for p in paths])


def verify(index=False):
    manifest = read_json(DEST / 'archive-manifest.json')
    assert {p.relative_to(DEST).as_posix() for p in DEST.rglob('*') if p.is_file()} == {x['path'] for x in manifest} | {'archive-manifest.json'}
    for item in manifest:
        data = within(DEST / item['path'], DEST).read_bytes()
        assert len(data) == item['bytes'] and sha(data) == item['sha256']
        assert not re.search(rb'(?<![A-Za-z])[A-Za-z]:[\\/]', data), item['path']
        assert not (set(Path(item['path'].lower()).parts) & FORBIDDEN_PARTS), item['path']
    summary = read_json(DEST / 'summary.json')
    assert summary['attempts_archived'] == len(summary['runs'])
    assert summary['technical_valid'] == sum(row['technical_valid'] for row in summary['runs'])
    assert summary['technical_invalid'] + summary['technical_valid'] == summary['attempts_archived']
    assert {row['receipt'] for row in summary['runs']} == {
        p.relative_to(DEST).as_posix() for p in (DEST / 'runs').glob('*/*/*/receipt.json')}
    for key in ('artifacts', 'written_documents', 'missing_work_files', 'final_path_redactions', 'failed_read_count', 'unresolved_failed_read_count'):
        assert summary[key] == sum(row[key] for row in summary['runs'])
    frozen = {}
    for row in summary['frozen_manifests']:
        arm = row['arm']
        frozen[arm] = {item['path']: item for item in read_json(DEST / f'manifests/{arm}.json')}
        assert len(frozen[arm]) == row['files_verified'] == 41
        for name in SNAPSHOTS:
            assert sha((DEST / f'snapshots/{arm}/{name}').read_bytes()) == frozen[arm][name]['sha256']
    for row in summary['runs']:
        receipt = read_json(within(DEST / row['receipt'], DEST))
        assert sha(within(DEST / receipt['final_path'], DEST).read_bytes()) == receipt['final_sha256']
        assert receipt['technical_valid'] == row['technical_valid']
        assert receipt['final_redaction']['replacement_count'] == row['final_path_redactions']
        if not row['final_path_redactions']:
            assert receipt['source_final_sha256'] == receipt['final_sha256']
        for tool in receipt['tool_evidence']:
            if tool.get('scope') == 'unresolved_failed_read':
                assert tool['name'] == 'Read' and tool['result']['observed'] and tool['result']['is_error_field'] is True
                assert not any(key in tool for key in ('package_path', 'work_relative_path', 'archive_path'))
            if tool.get('scope') == 'package':
                assert tool['frozen_file_sha256'] == frozen[row['arm']][tool['package_path']]['sha256']
        for doc in receipt['documents']:
            if doc['archive_path']:
                data = within(DEST / doc['archive_path'], DEST).read_bytes()
                assert sha(data) == doc['sha256'] and len(data) == doc['bytes']
            else:
                assert doc['file_state'] == 'missing_not_archived'
    if index:
        for path in sorted(DEST.rglob('*')):
            if path.is_file():
                relative = path.relative_to(ROOT).as_posix()
                assert subprocess.check_output(['git', 'show', ':' + relative], cwd=ROOT) == path.read_bytes(), relative
    print(json.dumps({'archive_payload_files': len(manifest), 'archive_files_including_manifest': len(manifest) + 1,
                      'attempts_archived': summary['attempts_archived'], 'written_documents': summary['written_documents'],
                      'missing_work_files': summary['missing_work_files'], 'hashes_verified': len(manifest),
                      'index_verified': index, 'status': 'PASS',
                      'manifest_sha256': sha((DEST / 'archive-manifest.json').read_bytes())}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--verify-index', action='store_true')
    parser.add_argument('--arms', nargs='+')
    args = parser.parse_args()
    if not args.verify_only and not args.verify_index:
        archive(args.arms)
    verify(index=args.verify_index)

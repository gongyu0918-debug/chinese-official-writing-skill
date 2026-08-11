# chinese-official-writing 1.5.0 release evidence

Date: 2026-07-04 Asia/Shanghai

## Scope

1.5.0 promotes the playbook-based reference architecture prepared after the 1.4.15 baseline. The release keeps the change at the prompt/reference layer:

- add and route genre playbooks for request, notice, letter/reply, meeting minutes, report/explanation, plan, speech, procurement/review materials, and AI compute documents;
- keep anti-AI-flavor and lint checks as soft review guidance, not hard rewriting gates;
- tighten the fact boundary found during candidate ablation: ordinary procurement, review materials, speeches, and review-only tasks must not inherit AI compute wording unless the user asks for it.

No script-based cleaning, default network expansion, or formatting engine was added.

## Baseline

- Previous release baseline: `v1.4.15` / `9c218ea`
- Baseline worktree: `output/release-baselines/github-1.4.15`
- Current release branch before publish: `codex/ai-dedupe-round1-20260627`

## Deterministic Verification

Commands actually run:

- `python .\tools\sync_adapters.py`  
  Result: PASS. Synced canonical skill into `skills/`, `.agents/`, `.qwen/`, `hermes/`, and `openclaw/`; updated README, OpenClaw card, and Claude plugin version.
- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary tests.test_promptfoo_eval -v`  
  Result: PASS, 54 tests.
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.15 --baseline-label baseline-1.4.15 --current-root . --out .\output\real-prompt-vs-1.4.15-release-1.5.0`  
  Result: PASS. Baseline `71/81`; current `81/81`. Baseline failures are the new P072-P081 playbook coverage cases; current has no failure.
- `python -m unittest discover -s tests -v`  
  Result: PASS, 99 tests.
- `python .\tools\run_real_article_eval.py --out .\output\real-article-release-1.5.0`  
  Result: PASS for release use. Skill mode `0.00%` average missing-key-element rate, `100.00%` keyword coverage, `0` format risk, `0` repeat items, `0` anti-AI risk. Existing placeholder-risk samples remain a manual review signal, not a new 1.5.0 regression.
- `npm run eval:official-writing:smoke`  
  Initial sandbox/default PATH attempts failed because promptfoo could not spawn the Python selected by the local environment. Final non-sandbox run with PATH prefixed to `C:\Users\admin\AppData\Local\Programs\Python\Python313` passed: `20/20`, skill wins `10`, baseline wins `0`, `needs_manual_review=0`, judge consistency `1.0`.
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals\official-writing\run_eval.py --suite full --judge-batch-size 2`  
  Result: PASS, `540/540`; pairwise skill wins `259`, baseline wins `11`, `needs_manual_review=0`, judge consistency `1.0`.
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`  
  Result: PASS, `Skill is valid!`.
- `git diff --check`  
  Result: PASS. Only Windows LF-to-CRLF warnings were emitted.

Promptfoo reported local package version `0.121.11` while latest available was `0.121.17`; this is informational and did not fail the run.

## Real Subagent Writing Test

Writer agents used the installed adapter skill at `.agents/skills/chinese-official-writing/SKILL.md`. They were instructed to be read-only.

Coverage:

- W1-A: AI compute feasibility outline with missing budget, GPU model, concurrency, service period, SLA, and supplier.
- W1-B: ordinary office furniture procurement announcement, explicitly not AI/compute.
- W2-A: meeting notes to meeting minutes, no meeting conclusion supplied.
- W2-B: short internal speech with only three provided points, no audience/background/policy/evidence data.
- W3-A: field-style procurement review material, keep field order and avoid semicolon noise.
- W3-B: review-only AI-flavor and format check, no rewrite and no 0-100 score.
- W4-A: request for meeting-system upgrade service with missing amount, approval target, supplier, and contract dates.
- W4-B: notice for archive sorting with missing deadline, contact, and email.
- W4-C: solicitation letter with missing feedback deadline, email, and contact.

Independent verifier result:

- W1-A: PASS. Did not invent budget, GPU, concurrency, SLA, supplier, or other parameters.
- W1-B: PASS. Did not introduce AI, compute, GPU, or model-service wording.
- W2-A: PASS. Kept only item, unit, and deadline; did not add meeting-news framing or meeting conclusions.
- W2-B: PASS. Stayed within the three supplied points; did not invent audience, background, policy basis, achievements, or data.
- W3-A: PASS. Field order retained; no prose conversion, `。；`, or trailing semicolon noise.
- W3-B: PASS. Review-only output; no full rewrite and no numeric score.
- W4-A: PASS. Drafted first and moved missing facts to pending confirmation.
- W4-B: PASS. No external search and no invented deadline/contact/email.
- W4-C: PASS. Correct solicitation-letter shape; no invented feedback deadline/email/contact.

Verifier total: `9/9 PASS`; no release blocker and no additional minimal fix required.

## Publish Notes

Target surfaces for this release are GitHub, ClawHub, and the exact SkillHub project `https://skillhub.cn/skills/chinese-official-writing`. Do not republish similarly named SkillHub projects such as `yjkj-chinese-official-writing`.

ClawHub publish and inspect:

- Pre-publish inspect: `latestVersion.version=1.4.15`, moderation `clean`.
- Publish command: `clawhub publish .\openclaw\skills\chinese_official_writing --slug chinese-official-writing --name "中文公文写作" --version 1.5.0 --tags "chinese,official-document,writing,gongwen,ai-compute"`
- Publish result: `Published chinese-official-writing@1.5.0 (k97fj6xf2vshaybhp1appk94mh89t9b4)`.
- Post-publish inspect: `latestVersion.version=1.5.0`, `metadata.version=1.5.0`, `metadata.openclaw.version=1.5.0`, moderation verdict `clean`, no suspicious or malware flags.

GitHub `main` and tag `v1.5.0` were verified at release commit `91d2ec4009f8a8ae7b3a67bfb07d7bbd9faeebb5` before this SkillHub evidence follow-up. This follow-up records SkillHub status only and does not move the `v1.5.0` tag.

SkillHub target verification and publish submission:

- Public target API before publish confirmed `slug=chinese-official-writing`, `source=clawhub`, `sourceUrl=https://clawhub.ai/gongyu0918-debug/chinese-official-writing`, `latestVersion.version=1.4.15`, `tags.latest=1.4.15`, `stats.versions=20`, Keen/Sanbu security reports `benign`.
- Search API also showed similarly named skills; this run targeted only `slug=chinese-official-writing`.
- Local `skillhub` command was not on PATH, but an installed SkillHub CLI was found at `C:\Users\admin\AppData\Local\Temp\skillhub-kit-fce40d6c7e9a48a78c932a965343ea03\cli\skills_store_cli.py`.
- A temporary publish package was created under `output\skillhub-release-1.5.0\publish-package` from the current canonical skill package, with SkillHub-required top-level metadata `slug=chinese-official-writing`, `displayName=中文公文写作`, `summary`, `homepage`, and `_meta.json` version `1.5.0`.
- Dry-run command: `python ...\skills_store_cli.py publish .\output\skillhub-release-1.5.0\publish-package --dry-run --json`
- Dry-run result: `{"dryRun": true, "slug": "chinese-official-writing", "version": "1.5.0"}`.
- Publish command: `python ...\skills_store_cli.py publish .\output\skillhub-release-1.5.0\publish-package --changelog "1.5.0：补充文种 playbook 架构，强化请示、通知、函、会议纪要、报告、方案、讲话、采购/审查和 AI 算力材料的路由与事实边界；保持 prompt/reference 层最小更新，不新增硬清洗或默认联网。" --json`
- Publish result: `ok=true`, `slug=chinese-official-writing`, `version=1.5.0`, `skillId=70149`, `versionId=127481`, `fileCount=17`, `fingerprint=a9b3093204d7e79a10c3a220fa7b18d60fd2877f3427b156fccfe96cd081cb0f`, `reviewStatus=pending`, `securityScanStatus=pending`, `contentAuditStatus=pending`, `tags.latest=1.5.0`.
- Post-submit public API check: `slug=chinese-official-writing`, `sourceUrl=https://clawhub.ai/gongyu0918-debug/chinese-official-writing`, `tags.latest=1.5.0`, `stats.versions=21`, but `latestVersion.version=1.4.15`. The public latest version has not switched while review/security/content audit are pending.
- Public verification check for `chinese-official-writing@1.5.0` still returned `找不到该版本`, matching the pending public-switch state.

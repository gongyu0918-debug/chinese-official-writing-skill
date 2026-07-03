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

GitHub and ClawHub are the executable publish surfaces in this workspace. `clawhub` CLI is installed; no local `skillhub` CLI or SkillHub publish script was found in this repository, so SkillHub is not marked as published from this run unless a separate publishing channel is provided.

ClawHub publish and inspect:

- Pre-publish inspect: `latestVersion.version=1.4.15`, moderation `clean`.
- Publish command: `clawhub publish .\openclaw\skills\chinese_official_writing --slug chinese-official-writing --name "中文公文写作" --version 1.5.0 --tags "chinese,official-document,writing,gongwen,ai-compute"`
- Publish result: `Published chinese-official-writing@1.5.0 (k97fj6xf2vshaybhp1appk94mh89t9b4)`.
- Post-publish inspect: `latestVersion.version=1.5.0`, `metadata.version=1.5.0`, `metadata.openclaw.version=1.5.0`, moderation verdict `clean`, no suspicious or malware flags.

GitHub push and tag verification are performed after this evidence update is committed, so the exact remote SHA is reported in the final release handoff.

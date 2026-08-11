# chinese-official-writing 1.5.1 release evidence

## Scope

1.5.1 packages the two validated commits after `v1.5.0` plus a version metadata bump:

- `35385ee docs: record skillhub 1.5.0 pending status`
- `1fa0858 fix: harden review-found writing boundaries`

The release remains a prompt/reference/lint/tooling patch. It does not add hard writing blockers, default search, auto-cleaning, template libraries, or ClawHub avatar metadata.

Accepted fixes:

- Upper-writing drafts: when 请示/报告/上报申请缺主送机关、发文或申请单位、金额、成文日期, do not invent generic recipients or dates; list the structural gaps first in pending items and explain impact on formal submission/genre completeness.
- Compression/revision: preserve contact, signature unit, and date structure instead of truncating them for word count or anti-AI smoothing.
- Format lint: flag formal-body `---` horizontal rules while ignoring YAML frontmatter delimiters.
- Eval tooling: `run_agent_ablation.py` and `run_revision_instruction_eval.py` return readable timeout summaries with exit code `124` instead of tracebacks.

Deferred/non-blocking:

- The real writer/verifier run produced one WARN: a meeting notice sample filled `办公室` and the current date when the prompt did not provide issuer/date. This is recorded as a follow-up observation, not a release blocker, because the target 1.5.1 fixes are otherwise verified and expanding prompt changes at release time would require a new ablation loop.

## Version and icon handling

- Version source: `tools/sync_adapters.py` `VERSION = "1.5.1"`.
- Synced adapters: canonical package, `skills/`, `.agents/`, `.qwen/`, `hermes/`, `openclaw/`, README, OpenClaw card, and Claude plugin manifest.
- ClawHub: no skill-level avatar field was found in `clawhub inspect chinese-official-writing --json`; only owner avatar is exposed. No ClawHub avatar metadata is added to the package.
- SkillHub: public API exposes `skill.iconUrl`. A new blue Q-style icon was generated and uploaded through SkillHub's community skill icon upload endpoint.
- SkillHub uploaded icon URL: `https://skillhub-1388575217.cos.accelerate.myqcloud.com/skill-icons/uploads/437097/fbafa4ddeb204e4584a699f65e06d137.png`.
- Local generated icon source: `C:\Users\admin\.codex\generated_images\019f08a7-0105-7ae3-b1fc-7126123987a6\ig_0c130b21810d3dd8016a48b46668f0819a999c8f08e0d21940.png`.

## Deterministic verification

- `python .\tools\sync_adapters.py`
  - First sandbox run failed on `.agents` permission, then escalated rerun succeeded.
- `python -m unittest tests.test_review_regressions tests.test_real_prompt_ablation tests.test_skill_boundary -v`
  - Result: PASS, `77` tests.
- `python -m unittest discover -s tests -v`
  - Result: PASS, `104` tests.
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.5.0 --baseline-label baseline-1.5.0 --current-root . --out .\output\real-prompt-vs-1.5.0-release-1.5.1`
  - Result: PASS.
  - Baseline `1.5.0`: `84` cases, `81` pass, `3` fail.
  - Current `1.5.1`: `84` cases, `84` pass, `0` fail.
  - Baseline failures are P082-P084, the new review-found regression checks.
- `python .\tools\run_real_article_eval.py --out .\output\real-article-release-1.5.1`
  - Result: PASS for release regression use.
  - Skill mode: `0.00%` average missing-key-element rate, `100.00%` keyword coverage, `0` format risk, `0` repeat items, `0` anti-AI risk.
  - Existing placeholder-risk samples remain a manual/LLM judge signal.
- `npm run eval:official-writing:smoke`
  - First run failed because promptfoo tried the stale Hermes venv Python path and could not delete old `.promptfoo` logs under sandbox permissions.
  - Rerun with `PROMPTFOO_PYTHON=C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe` and elevated permissions passed.
  - Result: `20/20` passed, `0` failed, `0` errors; skill wins `10`, baseline wins `0`, invalid `0`, manual review `0`, judge consistency `1.0`.
- `git diff --check`
  - Result: PASS; only CRLF normalization warnings were printed.

## Real subagent verification

Writer subagent generated six read-only samples using the current skill:

- 请示起草 with missing main recipient, applicant unit, amount, and date.
- 会议通知 with missing contact and registration deadline.
- 函起草 with missing issuer, contact, and date.
- Field-style material rewrite with blank contact.
- Review-only AI-style/format check.
- Anti-AI/format lint risk-only check.

Independent verifier result:

- Sample 1: PASS.
- Sample 2: WARN. It filled `办公室` and the current date although issuer/date were not provided.
- Sample 3: PASS.
- Sample 4: PASS.
- Sample 5: PASS.
- Sample 6: PASS.
- Overall: `WARN`.
- `publish_blocking=false`.

## Publish targets

Target surfaces for this release:

- GitHub repository: `gongyu0918-debug/chinese-official-writing-skill`
- ClawHub slug: `chinese-official-writing`
- SkillHub exact project: `https://skillhub.cn/skills/chinese-official-writing`

SkillHub publish must use the new `iconUrl` in the publish payload. ClawHub publish must not receive any avatar/icon metadata.

## Publish results

GitHub:

- Release commit: `8a4be21baeb58781346e155f442de43f97249cdf`.
- `git push origin HEAD:main`: succeeded, `origin/main` advanced from `91d2ec4` to `8a4be21`.
- `git push origin v1.5.1`: succeeded.
- `git ls-remote --heads origin main`: `8a4be21baeb58781346e155f442de43f97249cdf`.
- `git ls-remote --tags origin v1.5.1`: annotated tag object `6bbc1fc0901352d707af6abd4116f01f12d79129`.

ClawHub:

- Pre-publish inspect: `latestVersion.version=1.5.0`, moderation verdict `clean`.
- Publish command: `clawhub publish .\openclaw\skills\chinese_official_writing --slug chinese-official-writing --name "中文公文写作" --version 1.5.1 --tags "chinese,official-document,writing,gongwen,ai-compute"`.
- Publish result: `Published chinese-official-writing@1.5.1 (k97amfb3qmjbv7yp0htx9z9p2989xhab)`.
- Post-publish inspect: `latestVersion.version=1.5.1`, metadata version `1.5.1`, OpenClaw version `1.5.1`, moderation verdict `clean`, no suspicious or malware flags.

SkillHub:

- Icon upload result: `iconUrl=https://skillhub-1388575217.cos.accelerate.myqcloud.com/skill-icons/uploads/437097/fbafa4ddeb204e4584a699f65e06d137.png`, `objectKey=skill-icons/uploads/437097/fbafa4ddeb204e4584a699f65e06d137.png`.
- Publish package dry-run: `{"dryRun": true, "slug": "chinese-official-writing", "version": "1.5.1"}`.
- Publish endpoint result: HTTP `201`, `ok=true`, `slug=chinese-official-writing`, `version=1.5.1`, `skillId=70149`, `versionId=127598`, `fileCount=17`, `fingerprint=4625cf0f4d7b08b102c2adb651de217f22a73e48cad0b39dc4229eb55cf21c59`, `reviewStatus=pending`, `securityScanStatus=pending`, `contentAuditStatus=pending`, `iconAuditStatus=pending`, `iconAuditTaskStatus=pending`, `tags.latest=1.5.1`.
- Post-submit public API check: target slug remains `chinese-official-writing`; `sourceUrl=https://clawhub.ai/gongyu0918-debug/chinese-official-writing`; `tags.latest=1.5.1`; `stats.versions=22`; public `skill.iconUrl` is the new blue Q-style icon URL; public `latestVersion.version` still reports `1.5.0` while review/security/content audit are queued.

Release status:

- GitHub: published.
- ClawHub: published and moderation clean.
- SkillHub: submitted to exact target project with `tags.latest=1.5.1` and icon URL updated; public latest version switch is pending platform audit.

# 1.4.11 Release Evidence

Date: 2026-06-28

Baseline: `chinese-official-writing@1.4.10`, GitHub/main `d8d7ee0a96a0c0b822446bd70d1d417eef2a729e`.

Release candidate commits:

- `273adb41ffd2400813376ce60b5582e6c06f6c89`: minimal follow-up fixes for the Hermes/GLM 1.4.10 review findings.
- This release commit: version metadata and adapter sync for `1.4.11`.

## Included Fixes

Accepted follow-up review items:

- `N-1`: narrow `可以说` lint to avoid `不可以说`.
- `N-2`: narrow `综上所述` lint to avoid section-reference false positives.
- `B3`: avoid `unsupported-conclusion` when `未发现重大隐患` is immediately preceded by explicit check/evaluation/review basis.
- `N-3`: add a prompt-level common-error reminder that long official drafts should not use Markdown bold/headings/code fences for formal正文 headings.

Deferred:

- `B1`: keep `高度重视` as `low/empty-filler`.
- `B2`: keep `有关方面认为` as `medium/vague-attribution`.

## Real Subagent Test

Real writer/verifier test was run after the behavior changes and before the 1.4.11 metadata-only bump. The version bump did not change prompt or lint behavior.

Coverage:

- Long节能宣传周/低碳日方案: no Markdown `**加粗**` or `###`; missing dates, funding, and contacts stayed in `待确认事项`.
- 设备维保请示: missing amount, procurement method, supplier, contract dates, and contacts were not fabricated.
- Field-form rewrite: preserved fields/order/empty values.
- Review-only: did not rewrite the draft or use 0-100 scoring.
- Lint-boundary judgment matched the direct script behavior.

Independent verifier result:

- `overall_verdict=PASS`
- `publish_blocking=false`

## Release Validation

Commands run after bumping to `1.4.11`:

- `python .\tools\sync_adapters.py`: OK.
- `python -m unittest discover -s tests -v`: 92 tests OK.
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`: 20/20 passed, skill win rate 1.0, judge consistency rate 1.0.
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.10-release-1.4.11 --baseline-label baseline-1.4.10 --current-root . --out .\output\real-prompt-vs-1.4.10-release-1.4.11`: baseline 54/54, current 54/54.
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`: `Skill is valid!`
- Direct lint repro: N-1/N-2/B3 supported cases produce no finding; unsupported `未发现重大隐患` still produces `medium/unsupported-conclusion`; `可以说，` and `综上所述，` still produce `medium/side-commentary`; Markdown/fenced format checks still fire.

Version scan:

- Canonical `chinese-official-writing/SKILL.md`: `1.4.11`.
- Mirrors `.agents`, `.qwen`, `skills`, `hermes`, `openclaw`: `1.4.11`.
- `README.md`, `openclaw/README.md`, `.claude-plugin/plugin.json`, `tools/sync_adapters.py`: `1.4.11`.

Conclusion: release candidate is ready for GitHub main, tag `v1.4.11`, and ClawHub publish if final git checks pass.

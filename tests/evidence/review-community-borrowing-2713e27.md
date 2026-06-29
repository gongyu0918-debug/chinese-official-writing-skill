# Community Borrowing Review for Hermes Commit 2713e27

Date: 2026-06-29

Reviewed source: `C:\Users\admin\chinese-official-writing-review\repo`, commit `2713e275ea118e15ad3e0ce705bcc73f606b86c4`.

Current working repo: `F:\Workspaces\chinese-official-writing-skill`. This file is review evidence only. No code from the Hermes work repo was applied here.

## Overall Decision

Do not accept `2713e27` as-is.

The commit contains useful community-skill ideas, but the implementation is not release-safe:

- existing tests fail in the Hermes work repo;
- adapter mirrors are not synchronized;
- `format_docx.py` is unsafe for real Word/document workflows;
- `genre-checklist.md` accidentally changes `## 函` to `## 函数`;
- the AI-flavor replacement table encourages fact upgrades in real writing tests.

## Reproduced Evidence

Commands run against the Hermes work repo:

- `git -C C:\Users\admin\chinese-official-writing-review\repo show --stat --oneline --decorate 2713e27`: 12 files changed, +300/-6.
- `git -C C:\Users\admin\chinese-official-writing-review\repo diff --check 8994880..2713e27`: passed.
- `python -m py_compile C:\Users\admin\chinese-official-writing-review\repo\chinese-official-writing\scripts\prose_lint.py C:\Users\admin\chinese-official-writing-review\repo\chinese-official-writing\scripts\format_docx.py`: passed.
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`: 58 tests run, 5 failures.
- `python -m unittest discover -s tests -v`: 92 tests run, 5 failures.

The five test failures were mirror consistency failures:

- `.agents/skills/chinese-official-writing` missing canonical `scripts/format_docx.py`.
- `.qwen/skills/chinese-official-writing` missing canonical `scripts/format_docx.py`.
- `skills/chinese-official-writing` missing canonical `scripts/format_docx.py`.
- `openclaw/skills/chinese_official_writing/scripts` missing canonical `format_docx.py`.
- `openclaw/skills/chinese_official_writing/references/genre-checklist.md` no longer matches canonical.

Static path check:

- canonical `chinese-official-writing/references/genre-checklist.md` contains `## 函数` and no longer contains the expected `## 函` heading.
- `.agents`, `skills`, and `openclaw` mirrors still contain `## 函`, proving the commit is internally inconsistent.

Lint probes:

- A repeated exact phrase sample produces `low/paragraph-isomorphism`, as intended.
- A normal official-writing sample with repeated execution requirements also produces `low/paragraph-isomorphism` on `按时报送材料。`, which is a common public-sector instruction. This is not a release blocker by itself, but it disproves the commit message's "zero regression" claim unless backed by stronger false-positive tests.

## Subagent Review

Read-only reviewer `019f126d-bf21-7310-bde2-eb64da7c169d` found:

- `format_docx.py` says it only sets layout, but it rebuilds the document from `.txt`, strips lines, changes fonts, and can overwrite the default same-name `.docx`.
- It treats any line starting with `关于` as a title, so正文 paragraphs such as `关于预算安排...` may be centered and enlarged.
- the commit does not update `.agents`, `.qwen`, `skills`, or `openclaw`, even though the repo has a sync script and tests requiring mirror parity.
- `paragraph-isomorphism` match output is unstable because it chooses from equal-length set windows.
- the commit adds no tests or evidence files, so the "ablation-verified" claim is not reproducible from the commit.

## Real Scenario Test

Writer subagent `019f126f-deac-7a63-ac71-6342d069f057` used the candidate canonical skill for five tasks:

- T1 函起草: PASS. 商请语气 and missing items handled outside正文.
- T2 只审不改: PASS. It did not rewrite or score; it correctly called out repeated sentence pattern risk.
- T3 Word/docx boundary: PASS. It did not claim formal Word output was complete and did not fabricate formal elements.
- T4 去 AI 味改写: FAIL. It changed `老板关心` into `领导高度关注` and added `资金使用具有必要性` / `按程序推进`, none of which were given facts.
- T5 字段式材料: FAIL. It preserved field order, but again upgraded `老板也关心` into `领导关注` and added `推进较为紧迫`.

Independent verifier `019f1271-2ba3-7230-aa06-65a98988fd15` judged `overall=FAIL`. The verifier's key point: T4/T5 are fact-boundary failures, not just style issues.

## Borrowing Point Matrix

| Point | Decision | Reason |
| --- | --- | --- |
| AB1 paragraph-isomorphism lint | Modify before accepting | Useful as a low-severity hint, but current 8-char window rule is noisy on normal execution language, match selection is unstable, and no tests were added. |
| AB2 hard-boundary checklist layer | Accept with caution | The idea is compatible with existing review discipline. It should remain a review checklist, not a new blocking workflow, and must be synced across mirrors. |
| AB3 AI-flavor replacement table | Reject as implemented | The table caused real outputs to upgrade oral source phrases into stronger official facts. It needs explicit "only when evidence is present" wording and tests. |
| AB4 `format_docx.py` | Reject as implemented | It can overwrite same-name output, rebuilds content despite claiming layout-only behavior, misclassifies `关于...`正文 as title, and was not synced to all packages. |
| AB5 genre structure skeleton | Modify before accepting | The concept is useful, but the implementation introduced `## 函数`, and skeletons need a clear warning that they are not visible labels and do not override user templates. |

## Recommendation

Do not cherry-pick `2713e27`.

If the community borrowing is revisited, take only the ideas and rebuild them in the current work repo with these gates:

1. Start from current `F:\Workspaces\chinese-official-writing-skill` HEAD, not the Hermes clone.
2. Apply one borrowing point at a time.
3. Run `tools/sync_adapters.py` after any canonical skill/resource/script change.
4. Add tests before accepting new lint rules or scripts.
5. For AI-flavor replacements, prove no fact upgrades on oral-source prompts.
6. For Word/docx tooling, prefer the existing document skill or a separate safe design that never overwrites templates and does not silently reshape content.

No 1.4.12 version bump or publication should be based on `2713e27`.

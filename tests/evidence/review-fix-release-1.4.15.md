# Review Fix Release 1.4.15

## Scope

External report: `C:/Users/2/Desktop/中文公文写作skill-1.4.14-交付Review报告.md`.

This release keeps the patch small:

- lower `project-card-summary` from a medium base lint blocker to a low structure-only quality hint, so field-style applications and project cards are not blocked by `--strict --fail-on medium`;
- stop scanning common bracketed external-note headings such as `（待确认事项）`;
- expand the trigger description for explicit legal/official genres: 通告、意见、决定、决议、议案、公报、命令;
- bump package metadata to `1.4.15` and sync mirrors.

## Accepted

- Field-style false positive: reproduced on a four-line project card. 1.4.14 flagged every field as `medium/project-card-summary` and exited 1 with `--strict --fail-on medium`, conflicting with field-style preservation rules.
- External note heading variants: reproduced `（待确认事项）` continuing into placeholder and western-bullet findings. The scanner now treats those headings as the start of external notes.
- Description coverage: the canonical body already knew these genres, but the frontmatter description missed several short prompts. Added compact terms and deterministic P065-P071 guards.

## Rejected Or Deferred

- Code fence over-scan: rejected for this round. Existing tests intentionally require `--format` to scan fenced content so placeholders and Markdown remnants cannot be hidden inside code blocks.
- BMP decorative symbols and `可以说。`: deferred. They are reproducible small lint gaps, but adding more lint surface without repeated real-writing evidence risks noise and scope creep.
- Architecture-level review items: deferred because they require broader lint redesign or real evaluator changes outside the minimal fix boundary.

## Deterministic Verification

Commands run:

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest tests.test_review_regressions tests.test_real_prompt_ablation tests.test_skill_boundary -v
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.4.14-review --baseline-label baseline-1.4.14 --current-root . --out output\real-prompt-vs-1.4.14-release-1.4.15-review
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests -v
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tools\run_real_article_eval.py --out output\real-article-release-1.4.15-review
set PATH=C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python;%PATH%&& C:\Progra~1\nodejs\npm.cmd run eval:official-writing:smoke
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
git diff --check
```

Results:

- targeted tests: 71 passed;
- full tests: 97 passed;
- deterministic ablation: baseline-1.4.14 65/71, current 71/71. Baseline failures are only new P065-P071 description guards except `意见`, which was already present in 1.4.14.
- real article eval wrote `output/real-article-release-1.4.15-review/summary.md`.
- npm smoke: 20/20 passed; skill wins 10, baseline wins 0, judge consistency 1.0.
- quick_validate: `Skill is valid!`.
- `git diff --check`: passed.

## Real Writing A/B

Writer A used current `1.4.15` candidate. Writer B used the detached `1.4.14` baseline. Both were asked to draft or review:

1. field-style training expense application, preserving fields;
2. short `通告` prompt;
3. incomplete-facts inspection report;
4. only-review-empty-phrases prompt.

Independent verifier judged A/B with only the prompts and outputs. No repository writes were allowed from writer or verifier agents.

Verifier result:

- A1 field-style application: PASS. Current kept field form, order, and known facts; only revised the requested field and left the new empty field blank.
- A2 short `通告`: PASS. Current produced the requested genre and included department scope, deadline, contact person, and phone.
- A3 incomplete-facts report: PASS. Current completed the draft, did not invent policy basis, rectification result, or `未发现重大隐患`, and placed completion hints after the body.
- A4 only-review prompt: PASS. Current did not rewrite the whole text and gave position, risk level, and advice.

Overall verifier judgment: current `1.4.15` showed no functional regression against `1.4.14` in instruction following, point placement, genre format, field boundaries, fact boundaries, non-blocking behavior, or format preservation.

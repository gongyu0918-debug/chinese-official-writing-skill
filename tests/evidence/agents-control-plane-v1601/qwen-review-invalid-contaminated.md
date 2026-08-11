# Review verdict

Method note first: I read both arms in full from `packet.md` and anchored every citation with line-number greps (all verified, e.g. `packet.md:30`, `:44`, `:86`, `:121`, `:124`, `:130`, `:132`). The workspace also contained two earlier draft reviews (`kimi-final.md`, `grok-final.md`); I cross-checked their claims against the source text rather than trusting them — the core findings reproduce, and I add a few they missed. No repo/git history exists in this workspace, so "staleness" below is judged as a design defect, not by comparing against a live tag.

## Arm A — PASS

| Axis | Result |
|---|---|
| 1 Executability/clarity | Pass — numbered, scoped, actionable (dereferenced-commit baselines, five-fact verification, pre-release checklist) |
| 2 Duplication/conflict | Pass — no contradiction; Git item 4 vs 发行 item 1 is complementary (gate + scope) |
| 3 Stale state/history leak | Pass — no version anywhere; release facts delegated to `docs/evidence/README.md`, "历史文件不是当前指令" |
| 4 Product-writing leak | Pass — explicit ban; no 文种/tone/style rules present |
| 5 Git/test/blind/DIFF/release/security | Pass — complete on all boundaries |
| 6 Hook packaging SkillHub vs ClawHub | Pass — the only arm that defines it (packet.md:30) |

Line-level issues (none blocking):

1. `packet.md:44` 研究 item 2 — "只修复**至少三份真实样本**共同指向的机制" is a hard numeric bar. The escape hatch "或可确定证明的等义重复" helps, but there is no explicit exception path for a single-sample deterministic or high-severity fix; read literally, it could block one.
2. `packet.md:64` vs Git item 4 — "发布后的证据提交可以推进 `main`" sits next to "未经授权不得…推送". Charitable read (local advance ≠ remote push) resolves it, but one clarifying clause would remove the ambiguity. Same shape exists in B (packet.md:131); not differentiating.
3. `packet.md:63` — "版本面" is opaque jargon where B's "版本号" is plain.
4. Conflict-of-evidence handling (测试 item 6) says "保留分歧并说明最终依据" but lacks B's "不得择优汇报" and "复现原样本"; no convention for missing provenance (B has `unavailable`); delivery bullet (packet.md:74) reports test results but not the test commands. All minor, all places where B is stronger.
5. Borderline, shared with B: 研究 item 4's candidate constraints ("不新增重排版引擎，不扩大默认联网，不默认强制确认…") are product-scope decisions frozen into the engineering plane. They govern candidate behavior, not writing style, so they don't violate criterion 4 — but worth keeping an eye on.

## Arm B — WARN

| Axis | Result |
|---|---|
| 1 Executability/clarity | Pass — B's best axis; often more explicit than A |
| 2 Duplication/conflict | Pass with minor redundancy (测试 item 3 vs item 4 tail at :121; 发布 item 5 restates a corollary of item 4) |
| 3 Stale state/history leak | **Fail on axis** — hardcoded `v1.6.0` |
| 4 Product-writing leak | Pass — ban wording is stricter than A's |
| 5 Git/test/blind/DIFF/release/security | Pass — equal or slightly stronger than A |
| 6 Hook packaging SkillHub vs ClawHub | **Fail on axis** — absent entirely |

Line-level issues:

1. `packet.md:86` — "当前正式发行版为 `v1.6.0`" hardcodes release state into the always-on control file. Two concrete problems: it duplicates the source of truth two clauses later ("发布事实和历史入口见 docs/evidence/README.md"), so the file can contradict itself; and it is stale-by-design — every future release must edit AGENTS.md or the control plane silently lies. This is exactly the historical-log-leakage pattern criterion 3 targets.
2. Criterion 6 gap: 仓库结构 has no `hooks/` entry, no SkillHub Hook-companion policy, no ClawHub exclusion of Hook/delivery-gate assets, and no five-fact verification model. Downstream consequence: the "清洁包 allowlist、禁入文件" check in `packet.md:130` has no stated Hook policy to enforce — the checklist can't verify what the file never defines.
3. Minor: `packet.md:121` tail repeats item 3's deterministic-gate point; 修改与 review item 2 "已归纳的共性机制" is vaguer than A's operational threshold (A is brittle-but-executable, B is flexible-but-vague — pick your poison); Git item 2 downgrades worktree to "优先" where A mandates it.

Why WARN and not FAIL: no fabricated process, no hard rule conflicts, no product-writing pollution, and every other boundary is sound. The two failing axes are localized and removable.

## Head-to-head

| Axis | A | B | Edge |
|---|---|---|---|
| Executability/clarity | Solid | Slightly more explicit (consent gate, conflict protocol) | B slight |
| Duplication/conflict | Clean | Clean, minus two small redundancies | A slight |
| Stale state/history | Externalized | Hardcoded `v1.6.0` | **A** |
| Product-writing leak | None | None (stricter ban wording) | Tie |
| Git/test/blind/DIFF/release/security | Complete | Complete + `unavailable`, 不得择优汇报, 复现原样本 | B slight |
| Hook packaging SkillHub/ClawHub | Explicit, five-fact model | Absent | **A** |

## Final preference: A

The two explicit rubric axes where the arms diverge — stale release state (3) and Hook packaging (6) — are precisely where B has material defects and A is clean. B is the better-edited file in several places, and its improvements (explicit user consent before material behavior change, non-cherry-picking conflict handling with sample re-run, `unavailable` provenance convention, god-function/magic-number hygiene, test commands in delivery reports) are real and portable. If B dropped the hardcoded version line and imported A's packaging block, it would likely flip to B-preferred on process precision. As submitted, though, A covers all six judged axes without a staleness vector, so the preference is **A** — not because it's shorter, but because it answers the rubric.

Delivery notes per repo rules: this was a review-only task — no files were modified, so there is nothing to commit and no commit hash. Verification actually run: `Get-Content` on all three workspace files plus two `Select-String` anchor passes over `packet.md` (results above); no test suite applies to a text review. Residual risk: with no git repo in this workspace I could not confirm whether `v1.6.0` is already superseded — B's criterion-3 finding stands on the pattern and the internal inconsistency, not on proven staleness.


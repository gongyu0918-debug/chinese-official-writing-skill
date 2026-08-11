## Review result

| Arm | Verdict | Preference |
|-----|---------|------------|
| **A** | **PASS** | **Preferred** |
| **B** | **WARN** | — |

Final preference: **A**

Shorter is not the reason. A better matches the control-plane job: it keeps release state out of the live instruction surface, and it actually defines SkillHub/ClawHub Hook packaging boundaries.

---

## Arm A — PASS

### 1. Engineering executability and clarity
Executable and sectioned well enough to act on: scope, surfaces, Git, research/review/DIFF, test/score, release, security.

Minor clarity only, not enough to downgrade:

- “研究、review 与归因” item 6 merges evidence-type separation and DIFF attribution in one bullet. Still readable; B separates them more cleanly.
- “只修复至少三份真实样本共同指向的机制” is a hard numeric bar. Usable, but brittle for rare/high-severity single-mechanism bugs.

### 2. Duplicated or conflicting rules
No material internal conflict found.

- Scope ban on product-writing rules vs candidate engineering constraints (no reflow engine / no default-network expansion / no forced confirm) are different layers; not a conflict.
- “常规发布范围” vs “当次授权” coexists cleanly: scope ≠ automatic permission.

### 3. Stale release state / historical log leakage
Clean.

- No hard-coded current version.
- Points release facts/history to `docs/evidence/README.md` and says historical files are not live instructions.

### 4. Accidental product-writing rules
Clean.

- Explicit ban: product-writing rules must not enter `AGENTS.md`.
- No 文种/语气/套话 rules leaked into the control plane.
- Candidate constraints stay at engineering/runtime/package behavior level.

### 5. Git / testing / anonymous review / DIFF / release / security
Covered with actionable boundaries:

- Git: root/branch/HEAD/worktree, preserve user changes, fixed baseline commit, no unauthorized push/tag/release, no destructive reset, 5-commit pause.
- Testing: risk-proportionate smoke; metadata vs product change matrix; deterministic ablation gate cannot replace real path/quality; real A/B + independent verifier; pre-fixed scoring protocol; anonymous/shuffled judging; no fabricated results.
- DIFF: candidate-vs-fixed-baseline only; shared baseline issues / sampling noise / env failure / candidate-only regressions reported separately.
- Release: per-event authorization, ancestry/diff/version/mirror/clean-pack/fingerprint checks, annotated tag vs peeled commit vs Release separated, Red SkillHub default-deny.
- Security: secrets, least privilege, scope isolation, delivery report fields.

Small gap vs B (not fatal): less explicit “不得择优汇报” and no explicit `unavailable` for missing provenance.

### 6. Hook packaging: SkillHub vs ClawHub
Present and useful:

- SkillHub may carry optional Codex Hook companions under dedicated `hooks/`.
- ClawHub package excludes Hook and delivery-gate assets.
- “包内存在 / 插件安装 / 功能启用 / 信任确认 / 真实执行” treated as five independent facts.

This is a material packaging control that B lacks.

### Line-level notes (non-blocking)
1. **研究 item 2** — “至少三份真实样本”: consider operational exception path for proven single-mechanism high-severity defects; current wording is absolute.
2. **研究 item 6** — split evidence taxonomy from DIFF attribution for scanability.
3. **发行 item 4** — good separation of dry-run/receipt/index; could still add explicit missing-provenance handling (`unavailable`).

---

## Arm B — WARN

### 1. Engineering executability and clarity
Strong, often more explicit than A:

- Clearer “明确同意后才可继续” for material product/toolchain/release changes.
- Better conflict handling: “不得择优汇报”, keep divergence, re-run original samples.
- Provenance missing → record `unavailable`.
- Maintenance hygiene: avoid god-functions/magic numbers.
- Review evidence types and DIFF attribution are separate bullets.

### 2. Duplicated or conflicting rules
No serious internal conflict.

One structural smell, not a logic contradiction:

- Live control plane asserts “当前正式发行版为 `v1.6.0`” while also saying release facts live under `docs/evidence/`. That duplicates the source of truth.

### 3. Stale release state / historical log leakage — concrete issue
**Issue (blocking for PASS):**

- Section **工程控制面**: `当前正式发行版为 v1.6.0` hard-codes release state into the always-on instruction file.
- Effect: every release either updates AGENTS.md or leaves a stale control-plane fact. That is exactly release-state leakage into engineering policy.
- A avoids this by externalizing version/history to evidence only.

### 4. Accidental product-writing rules
Clean, slightly stricter ban language than A:

- No copy/rewrite/summarize/append of writing rules into root.
- No writing conclusions or long release narrative written back into root.

No product-writing pollution found.

### 5. Git / testing / anonymous review / DIFF / release / security
Mostly equal or slightly stronger than A on process rigor.

Still complete on:

- worktree + peeled baseline commits
- unauthorized main/tag/push/release barred
- smoke/minimal verify before delivery
- anonymous shuffled judging
- model votes cannot override deterministic failure
- Red SkillHub default exclude
- secrets / least privilege / out-of-scope isolation

### 6. Hook packaging: SkillHub vs ClawHub — concrete gap
**Issue (main WARN driver):**

- **仓库结构** and later release sections never distinguish:
  - SkillHub optional Hook companion / `hooks/` placement
  - ClawHub exclusion of Hook and delivery-gate assets
  - package presence vs plugin install vs enablement vs trust vs real execution as independent facts
- For a Skill packaging control plane, this is a material omission against the review rubric, not a style preference.

### Line-level issues
1. **工程控制面** — `当前正式发行版为 v1.6.0` → stale-prone release fact in live policy. Move to evidence/index only.
2. **仓库结构 / 发布与回执纪律** — missing SkillHub Hook companion rules and ClawHub Hook/gate exclusion.
3. **仓库结构** — no statement that package-present / installed / enabled / trusted / really-executed are independent verification facts.
4. Secondary (non-blocking): “只修复已归纳的共性机制” is vaguer than A’s sample threshold; either is fine if the other packaging/version issues are fixed.

---

## Head-to-head on required axes

| Axis | A | B | Edge |
|------|---|----|------|
| Executability / clarity | Clear, actionable | Slightly more explicit on conflicts/consent | B slight |
| Duplication / conflict | Clean | Clean, but version fact duplicated vs evidence | A slight |
| Stale release / history leak | Externalized | Hard-coded `v1.6.0` | **A** |
| Product-writing pollution | None | None (stronger ban wording) | Tie / B wording |
| Git / test / blind / DIFF / release / security | Complete | Complete, stronger conflict reporting | B slight |
| SkillHub vs ClawHub Hook packaging | Explicit | Absent | **A** |

---

## Preference

**Prefer A.**

Reasons that matter under the stated rubric:

1. A keeps release state out of the live control plane; B pins `v1.6.0` and will rot.
2. A defines SkillHub/ClawHub Hook packaging and the five independent verification facts; B does not.
3. B’s process refinements (conflict non-cherry-picking, `unavailable` provenance, explicit user consent before material behavior change) are real improvements, but they do not outweigh A’s packaging completeness and anti-staleness design.

If B removed the hard-coded version and added the Hook packaging boundary block from A, the comparison would likely become a near-tie or B-preferred on process precision. As written: **A PASS over B WARN**.


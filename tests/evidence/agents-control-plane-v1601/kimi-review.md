# Review: AGENTS.md control files, Arm A vs Arm B

Both files cover the same engineering plane with near-identical Git, testing, anonymized-review, release, and security rules. The decisive differences are on criterion 3 (stale release state) and criterion 6 (Hook packaging), plus a few executability nits.

## Arm A — PASS

**Criterion-by-criterion:**

1. **Executability/clarity** — Solid. Rules are numbered, scoped, and actionable ("固定基线记录解引用 commit", "分别验证"). Minor nit: the "仓库与发行表面" section packs six surfaces into two dense bullets; Arm B's one-line-per-surface list is more scannable.
2. **Duplication/conflicts** — Mild overlap: "研究、review 与归因" rule 6 (evidence-type separation + DIFF attribution) partially restates "测试与评分" rules 5–6 (anonymization, conflict reporting). No hard contradiction, but the same evidence-discipline idea lives in two sections.
3. **Stale release state / history leakage** — Clean. Release facts are delegated to `docs/evidence/README.md`; "历史文件不是当前指令" is stated without embedding any version number or release narrative.
4. **Product-writing rules in the control plane** — The explicit exclusion statement is good. However, "研究" rule 4 embeds candidate product-behavior constraints ("候选不新增重排版引擎，不扩大默认联网，不默认强制确认，不破坏用户模板和字段式材料") — these are scope/toolchain constraints rather than writing rules, so borderline-acceptable, but they are product-shape decisions frozen into an engineering file. Also rule 2's "只修复**至少三份真实样本**共同指向的机制" is a brittle quantitative threshold: a security fix or a deterministic reproducible bug backed by one sample would be blocked by the letter of this rule.
5. **Git/testing/review/DIFF/release/security boundaries** — Complete and internally consistent: pre-change baseline + authorization check, no floating branch names as baselines, deterministic gate vs. real-chain A/B correctly separated, model votes can't override deterministic failures, tag immutability after release, Red SkillHub default-excluded.
6. **Hook packaging (SkillHub vs ClawHub)** — Present and precise: SkillHub may carry optional Codex Hook companions in a dedicated `hooks/` dir; ClawHub excludes Hook and delivery-gate assets; and "包内存在、插件安装、功能启用、信任确认、真实执行" are five independently verifiable facts. This is exactly the distinction the criterion asks for.

**Line-level issues:**

- 研究 rule 2 — "至少三份真实样本" hardcoded threshold; conflicts with legitimate single-sample deterministic fixes.
- 研究 rule 4 — the "候选不新增重排版引擎…" clause is a product-scope rule living in the engineering plane (shared with B, so not differentiating, but worth flagging).
- 仓库与发行表面 bullet 1–2 — over-dense; surface roles and verification duties merged into long sentences.
- 交付 bullet — reports "实际测试结果" but not "测试命令"; Arm B requires both.

## Arm B — WARN

**Criterion-by-criterion:**

1. **Executability/clarity** — The strongest part of B. Review section splits evidence types (rule 6) from DIFF attribution (rule 7); testing separates conflict-of-evidence handling into its own rule 8-item list with "复现原样本" and "说明最终裁决依据". Release rule 4 adds "来源证明缺失时记 `unavailable`", which A lacks. Repo structure as a definition list is cleaner. "修改与 review" rule 2 ("已归纳的共性机制") avoids A's brittle numeric threshold.
2. **Duplication/conflicts** — Same mild overlap as A between review rules 6–7 and testing rules 5–7. No new conflicts introduced — except the one below.
3. **Stale release state / history leakage** — **Fail on this axis.** "当前正式发行版为 `v1.6.0`" hardcodes a version into the engineering control plane. This contradicts the file's own delegation sentence two lines later ("发布事实和历史入口见 docs/evidence/README.md"), and it goes silently stale the moment any release ships — precisely the historical-log-leakage pattern this review is meant to catch.
4. **Product-writing rules** — Same borderline clause as A (修改与 review rule 4, "候选不新增重排版引擎…"). Otherwise clean exclusion statement, and its phrasing ("不得在本文件复制、改写、概括或追加") is actually stricter than A's.
5. **Boundaries** — Complete, same as A, with slightly better delivery reporting ("实际测试命令与结果").
6. **Hook packaging** — **Missing entirely.** No mention of SkillHub Hook companions, the `hooks/` directory, ClawHub exclusion of Hook/gate assets, or the five-fact verification model. For a file whose stated scope includes 发布 (release discipline), the SkillHub-vs-ClawHub packaging boundary is an uncovered release-critical surface.

**Line-level issues:**

- 工程控制面, line "当前正式发行版为 `v1.6.0`" — stale-prone hardcoded release state; internally inconsistent with the delegation to `docs/evidence/README.md`.
- 仓库结构 — no `hooks/` entry; packaging asymmetry between SkillHub and ClawHub undocumented anywhere in the file.
- 发布与回执纪律 — no rule covering Hook asset inclusion/exclusion per platform, so release rule 2's "清洁包 allowlist、禁入文件" check has no stated Hook policy to check against.
- (Shared with A) 修改与 review rule 4 — product-scope constraints embedded in the engineering plane.

## Final preference: **A**

B is the better-edited file in prose quality — cleaner structure, sharper DIFF-attribution separation, the `unavailable` provenance rule, and no brittle sample-count threshold. But review criteria 3 and 6 are exactly where B has material defects: a hardcoded `v1.6.0` that will silently rot, and total silence on the SkillHub/ClawHook packaging asymmetry that A handles with a precise, independently-verifiable model. A covers all six judged axes without stale state; its flaws are nits, not gaps. Preference: **A**.


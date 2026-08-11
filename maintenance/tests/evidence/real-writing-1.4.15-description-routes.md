# Real Writing Test - 1.4.15 Description Routes

Date: 2026-07-03

Scope: multi-subagent real writing and rewriting tests for the newly strengthened description route terms: 通告、意见、决定/决议、议案、公报、命令（令）, plus rewrite scenarios that must not change the requested genre.

Method:

- Four writer subagents loaded the current canonical skill from `chinese-official-writing/SKILL.md` and relevant references as needed.
- Writers were instructed to produce drafts only and not modify the repository.
- One independent verifier subagent received only the original prompts and writer outputs, then judged PASS/WARN/FAIL for genre, writing relationship, key point placement, prohibited actions, fact boundary, Markdown/placeholders/process leakage, and format issues.

## Results

| Case | Scenario | Verifier Result | Notes |
| --- | --- | --- | --- |
| A1 | 通告: gas pipeline maintenance | PASS | Kept 通告 genre, included scope, time, impact, cautions, and phone number. Minor bridging phrase was acceptable. |
| A2 | 命令（令）: publish management rules | WARN | Did not invent document number, mayor/county head name, or seal, and did not become a work notice. Draft was very short and lacked some ordinary release elements, but this was acceptable under missing facts. |
| B1 | 意见: campus food safety | PASS | Kept 意见 genre, covered 总体要求、重点任务、组织保障, and included all four requested task points. No policy number invented. |
| B2 | 公报: public library statistics | PASS | Public release tone, all four provided data points included, no internal work requirements or extra numbers. Slight evaluative phrasing remained. |
| C1 | 决议: board resolution | WARN | Did not become meeting minutes and included subject, reviewed matter, vote result, and execution requirement. Added unprovided customary facts: `0票反对、0票弃权`, procedure-compliance statement, and effective-date statement. |
| C2 | 议案: submit draft regulation to standing committee | PASS | Kept 议案 genre, did not become 请示 or 方案, and did not invent specific legal clauses. |
| D1 | Rewrite report shell into 通告 | PASS | Corrected report shell to 通告, preserved original facts, no added facts, no notice-style drift. |
| D2 | Rewrite 意见稿 for formal tone | PASS | Preserved three original headings, did not add policy number, and did not change into notice. |

Overall: 6 PASS, 2 WARN, 0 FAIL.

## Common Issues

1. Materials with missing formal elements can push the model toward customary completion.
   - A2 stayed very short to avoid inventing prohibited release elements.
   - C1 crossed into light fact addition by adding ordinary board-resolution wording not provided by the prompt.
   - Next fix, if this repeats, should be a soft prompt-level rule for resolution/decision materials: only include vote splits, procedure-compliance statements, effective dates, and authority clauses when provided or clearly marked as draft placeholders outside正文.

2. Public-release short drafts can become mildly evaluative.
   - A1 and B2 used bridging or evaluative phrases such as safety-conditioned recovery and stable service support.
   - Current impact is WARN-level at most because no concrete extra data was invented.
   - If repeated three or more times, prefer a soft rule: 公报、通告 and similar public-release texts should keep summary judgments close to provided facts and avoid unsupported evaluation.

## Release Field Check Reminder

The 1.4.15 ClawHub publish command accidentally passed quoted values through Windows `npx.cmd`, causing remote JSON to store:

- `displayName`: `"中文公文写作"`
- tag keys such as `"chinese` and `ai-compute"`

Do not overwrite 1.4.15. On the next version, publish ClawHub with equals-form arguments:

```powershell
C:\Progra~1\nodejs\npx.cmd clawhub publish C:\Users\2\Documents\chinese-official-writing\openclaw\skills\chinese_official_writing --slug=chinese-official-writing --name=中文公文写作 --version=<next-version> --tags=chinese,official-document,writing,gongwen,ai-compute --no-input
```

Before declaring the next release complete, inspect raw remote fields:

```powershell
C:\Progra~1\nodejs\npx.cmd clawhub inspect chinese-official-writing --no-input --json
curl.exe -L https://api.skillhub.cn/api/v1/skills/chinese-official-writing
```

Required checks:

- ClawHub `displayName` is exactly `中文公文写作`, without quotes.
- ClawHub tag keys are exactly `chinese`, `official-document`, `writing`, `gongwen`, `ai-compute`, and `latest`, without quote fragments.
- SkillHub `skill.summary`, `summary_zh`, `tags.latest`, and `latestVersion.version` reflect the intended version after review clears.
- Canonical `SKILL.md` remains valid for Codex quick validation; SkillHub-only `slug/displayName` metadata must stay in a temporary publish package, not in canonical frontmatter.

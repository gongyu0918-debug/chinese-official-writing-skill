# Concrete Example Prompt Patch Reverted

Date: 2026-07-08

This records a second failed local attempt after commit `fc54997`. The patch was reverted and was not retained in the skill.

## Attempted Change

The previous abstract soft-rule patch failed. This attempt tried a smaller form: adding only two concrete counterexamples to the main `SKILL.md` common-error list, plus short workflow/review-checklist reminders.

The examples were:

- URL facts should not be generalized when the source already gives version ranges, dates or region scope.
- Completed-check reports should not expand a supplied `not found` conclusion into unsupported terminal checks, abnormal connection checks, daily inspection or risk-prevention actions.

The patch also added deterministic P102/P103 guards. Deterministic ablation against `fc54997` passed:

- baseline `fc54997`: `101/103`, failing only new P102/P103.
- local patch: `103/103`.

## Real Weak-Model Retest

Writer: `gpt-5.4-mini`, low reasoning, loaded the patched skill.

Targeted prompts: Claude Code URL notice, weather URL commuting notice, OpenClaw completed-check report.

Result: `FAIL`.

- Claude Code notice did not retain the concrete affected version range `2.1.91 至 2.1.196`; it wrote a generic `工信部风险提示所涉受影响版本`.
- The same notice added unsupported reporting fields: `排查范围、排查结果、处置情况及联系人信息`.
- Weather notice still generalized the source to `7 月 8 日至 9 日，广西、广东、海南、湖南等地`; it omitted the source warning time and the fuller affected-region scope.
- OpenClaw report added unsupported scope and actions: `办公终端、开发终端及相关工作设备`, `逐台核查`, `重点岗位、重点设备和相关人员使用终端`, `软件安装记录和运行痕迹`, and follow-up `软件安装管理和终端安全检查`.

Independent verifier result: `FAIL`; recommendation was to revert the uncommitted patch.

## Decision

The local prompt/test/mirror changes were reverted with `git restore`. This evidence is retained to prevent repeating the same "add more prompt examples" approach without a different mechanism.

Next useful direction should avoid further prompt bloat. Consider a lightweight external verifier or post-generation revision task that can compare the prompt/source facts against the draft, rather than expecting weak models to self-enforce these boundaries from more prompt text.

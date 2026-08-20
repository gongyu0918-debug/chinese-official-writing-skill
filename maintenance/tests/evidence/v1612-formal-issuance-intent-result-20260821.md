# Formal issuance intent routing A/B result

Date: 2026-08-21
Candidate commit: `8e45c700`
Runtime: WorkBuddy 5.3.13 embedded CodeBuddy CLI 2.115.0; `deepseek-v4-flash`; effort `max`; `bypassPermissions`; `--print --output-format json`; six successful exits (`0`).

Raw runs are preserved in the ignored directory `output/current-verification/v1.6.12-formal-issuance-intent-20260821/`. JSONL SHA-256 is the transcript hash; result SHA-256 is the extracted final answer hash.

| Case | JSONL SHA-256 | Result SHA-256 | Input | Output | Result |
| --- | --- | --- | ---: | ---: | --- |
| base-1 internal situation note | `b958029196f63c482ddcd57412d2e49b9d3b51c7b21a6c96737327f6b30ff36a` | `8869b7bc1a25a3c4ebad266f63e10eea84fa96f1a15d952d234ee32b8f4e89d3` | 95163 | 2715 | Used title “报告” and added `特此报告`; no red-head fields. |
| candidate-1 internal situation note | `2b480211eddb65b513833eece27c9f7029a3dc6cc42f6fc62fe716b20cd58b5e` | `4a7a98bfcc588722ca7fbd458ef6f1f06a9ef9b0e45daf6f399079097be97922` | 95235 | 2724 | No formal shell or report closing; direct-use improvement over base on this sample. |
| base-2 explicit formal report | `7da572b89ac08dd407c18506fbfa9d9becd9b66beb4a4c00c3b335407bc36f88` | `5d4f3b62b3945ec9b8aaecac7a82eb8084c6531dc57a52536f3492ba6a1305ca` | 95204 | 5299 | Formal report structure, no invented fields. |
| candidate-2 explicit formal report | `a546623d9b41b05cccc25e5090d9ef61efb83720f4621c28e7c0a429a2267242` | `5676bd48e69bbc271e3f96285b606ecf9aa5c978ab0a0ce01e9c3895a33956ad` | 99041 | 9413 | Candidate-only postscript says missing fields should be supplied by the user’s unit; violates “只输出正文及必要正式结构”. Hard rollback. |
| base-3 ordinary business letter | `a188d1600cd0b0aa5067ca4427d915fe347FC6B18edc3e4a05dfaee22e5d1fb1` | `ed2b345a4f80bb57c34ef7d101ecff7ad95ca7d5c4f3e9fc25c3856f77e3dc15` | 94745 | 5194 | Parallel business letter; no formal shell. |
| candidate-3 ordinary business letter | `6c428d9df7d29bccd468e21d97d283c174fd0103eae2d2a0d24c1c673f93d1c8` | `172f6cbb899f5c09ca1702916121f72d148c381e0757b9c6a7426b5fc2ebb3e0` | 94729 | 4077 | No formal shell, but adds unsupported “近期”“接口调用过程中” and book-title marks around the title; lower fidelity than base. Hard rollback. |

## Judgment

The candidate demonstrated a useful direction on the internal-material sample, but the explicit formal-report sample produced a candidate-only delivery regression: explanatory metadata was appended outside the requested正文。The ordinary-business-letter sample also added unsupported temporal and process context. These two candidate-only hard rollbacks fail the pre-registered gate. The candidate remains `HOLD`; do not merge or publish. The current main rules already state that working materials must not be forced into a red-head format and that explicit formal issuance keeps the formal route, so no product rule is adopted from this single run.

This is a real writing result, not a claim that the candidate is generally bad: a later atomic experiment may retest the same routing boundary with a stricter “正文 only” output instruction, but must not erase this hard rollback or average it away.

## Verification commands

```powershell
python -B maintenance/tools/assemble_hook_companion.py --host codebuddy --output <ignored-output>
python -B output/current-verification/v1.6.12-source-typing/run_codebuddy_print.py --plugin <plugin> --prompt-file <prompt> --out <run> --session <id>
git diff --check
```

# v1.6.1 本地发布候选

日期：2026-08-11

结论：`LOCAL RELEASE CANDIDATE READY / MERGED TO LOCAL MAIN / NO PUSH / NO TAG / NO RELEASE / NO UPLOAD`

## Git 与范围

- 上一正式发行版：`v1.6.0^{commit}=0f6ec603993d5595e784fa7079837e299d1b0da3`。
- 已验证集成候选：`8c2aeeee5faae143502eb84309ba50e7361b8c50`。
- 本地 `main` 以 `--ff-only` 从 `9abc48794ebf82b8e918c593ebdada8cc080fe61` 快进到集成候选；版本同步提交为 `4cf29dafebef45415b8e52d810c3f25137166d02`。
- `origin/main` 的本地跟踪引用仍为 `9abc48794ebf82b8e918c593ebdada8cc080fe61`；没有推送。
- 没有创建 `v1.6.1` tag、GitHub Release 或平台上传。
- `openclaw/` 相对 `0f6ec603` 零差异，ClawHub/OpenClaw 继续固定在已发布的 v1.6.0。

## v1.6.1 候选范围

1. 通用 `SKILL.md` frontmatter 只保留名称、280字触发描述和标签；新闻稿件在首句前置，机关、企事业单位、学校、新闻机构后置，“个人求职”排除项保留。
2. 非冻结运行面把“顺稿”改为“润色修改”，把“收束”改为结尾、作结、自然结束等普通说法；`先……再……` 只作为通读全文的软线索。
3. SkillHub、Codex、Claude Code 与 WorkBuddy/CodeBuddy 完整包采用 MIT，SkillHub 包以 `LICENSE.md` 携带许可全文；普通纯 Skill 镜像及冻结 OpenClaw 保持 MIT-0。
4. Hook 文件进入 `hooks/`，共享门禁核心保留在 `scripts/review_gate.py`；Codex、Claude Code、WorkBuddy/CodeBuddy 使用宿主薄适配器，均需用户显式启用或信任。
5. Hook 绕过纯审稿任务，修复低于篇幅下限后继续缩短的漏洞，并保护请求中明确给出的负结果及采购决定、审批、责任、期限等对象。
6. 根 README 已改正两处旧描述：不再使用“顺稿”，也不再声称冻结的 OpenClaw 会随 canonical 默认同步。

## 真实写稿与裁决边界

- Hook enabled/disabled 真实矩阵为9对、18次，Token Plan 2 DeepSeek V4 0731、Ollama DeepSeek V4 0731、MiniMax M3各3对，均为 `max`、零重试、技术有效。
- 原始严格裁判和用户业务口径复核同时保留：常规“按计划推进、确保按期完成、按规定程序、按既定安排”不因词面直接计为硬外扩；复核后只剩P009一例完成/在办关系观察，没有在第二个独立配对复现。
- Hook 可作为默认关闭、显式启用的窄域伴随物进入完整包；不宣称整体质量领先。六个 Enabled 写稿均原样发射D0，D1为0，每个写稿 Enabled 多一次 Stop block，存在延迟成本。
- description 的有效样本没有形成跨 provider 重复的候选独有错路由，但也没有建立新闻入口流量提升；该文字按用户明确的人类可读规格纳入。
- 详细证据见 `hook-postfix-real-ab-v1602-postfix-result-20260811.md`、`hook-postfix-business-standard-readjudication-v1602-20260811.md` 与 `v1602-final-integration-result-20260811.md`。

## 工程验证

| 检查 | 实际结果 |
| --- | --- |
| 聚焦单测 | 114/114 PASS |
| 全量 unittest | 521/521 PASS |
| Promptfoo Stub smoke | 20/20 PASS；run `eval-x1r-2026-08-11T13:58:26` |
| 固定 v1.6.0 确定性消融 | v1.6.0 109/111；v1.6.1 RC 111/111 |
| canonical quick validate | `Skill is valid!` |
| OpenAI plugin validator | 仓库根、canonical、SkillHub RC包均 PASS |
| Claude plugin validator | canonical 与 SkillHub RC包均 PASS |
| Claude no-model preflight | 2.1.195；配置未修改；未调用模型；无错误 |
| WorkBuddy/CodeBuddy 2.115 validator | canonical 与 SkillHub RC包均 `Validation passed / valid:true` |
| Python compile | Hook、宿主适配器、lint、review gate、builder、sync、preflight 全部 PASS |
| 镜像同步 | 版本变更后执行两次，提交后再执行两次，均幂等；OpenClaw 未参与同步 |
| OpenClaw 冻结 | 相对 `v1.6.0^{commit}` diff为0 |
| `git diff --check` | PASS |
| 高置信密钥扫描 | 仓库与RC包均0个匹配文件 |

主要命令：

```powershell
python -B -m unittest discover -s tests -p "test_*.py" -q
$env:OFFICIAL_WRITING_EVAL_STUB='1'
npm.cmd run eval:official-writing:smoke
python -B tools\run_real_prompt_ablation.py --baseline-root "F:\Workspaces\chinese-official-writing-skill\output\release-worktrees\release-1.6.0-integration" --baseline-label v1.6.0 --current-root . --out output\release-candidates\v1.6.1-rc-20260811\deterministic-vs-v1.6.0
python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
python -B tools\build_skillhub_package.py --output output\release-candidates\v1.6.1-rc-20260811\publish-package --version 1.6.1
python C:\Users\admin\.skillhub\skills_store_cli.py --skip-self-upgrade publish output\release-candidates\v1.6.1-rc-20260811\publish-package --version 1.6.1 --dry-run --json
git diff --exit-code 0f6ec603993d5595e784fa7079837e299d1b0da3 -- openclaw
git diff --check
```

## SkillHub 清洁候选包

- 路径：`output/release-candidates/v1.6.1-rc-20260811/publish-package`。
- 文件数：46。
- 相对路径与逐文件SHA-256排序清单的整体SHA-256：`16eae2ad2c4fb419ce81ec82666f6409e6685c87605086e6648bdbf585fe788f`。
- `LICENSE.md` SHA-256：`87f8830279bbf5177b417826ab3905a1ef4ccb2dfc151892d380883d9e9521f2`；与当前仓库根 `LICENSE` 字节一致。
- `_meta.json`：slug `chinese-official-writing`，version `1.6.1`。
- Codex、WorkBuddy、Claude三个包内 manifest 均为version `1.6.1`、license `MIT`。
- packaged `SKILL.md` 正文与 canonical 正文一致。
- 禁入项 `LICENSE`、`agents/openai.yaml`、`openclaw/` 均不存在。
- SkillHub CLI dry-run返回：`dryRun:true`、slug `chinese-official-writing`、version `1.6.1`；未执行正式上传。

## 保留的无效尝试

- WorkBuddy隔离验证首跑把普通变量命名为 `$home`，与PowerShell只读变量 `$HOME` 大小写不敏感地冲突；清单验证虽返回成功，但隔离HOME条件无效。改用 `$isolatedHome` 并启用 `$ErrorActionPreference='Stop'` 后，canonical与RC包均有效复跑通过。
- 首次高置信密钥扫描把历史路径中的 `task-...` 子串误识别为 `sk-...`；加入非字母数字左边界后，仓库与RC包均0命中。两次假阳性只涉及历史证据路径名，没有发现凭据内容。

## 未完成与发布边界

- 本候选没有独立自动补字或篇幅兜底；现有Hook只阻止可证明的D1继续恶化篇幅，本轮没有真实D1。
- Hook不是全面事实、文种、要素或篇幅门禁，普通Skill写作规则和只读lint仍承担各自职责。
- 短通知候选及其他HOLD原子没有进入本候选；ClawHub/OpenClaw不随1.6.1更新。
- 旧 `v1602` 证据中的 `1.6.2` 只是当时内部测试坐标，不是已发布版本；本文件确定本地发布候选版本为1.6.1，不改写旧证据。
- 只有收到新的明确授权后，才可推送 `main`、创建tag或GitHub Release、向skillhub.cn正式上传。ClawHub和小红书Red SkillHub仍不在授权范围内。

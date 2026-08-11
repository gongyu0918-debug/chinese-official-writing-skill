# v1.6.2 本地集成候选结果

日期：2026-08-11

结论：`LOCAL CANDIDATE READY / NO MERGE / NO PUSH / NO TAG / NO RELEASE`

## 固定基线与工作区

- 正式发行基线：`v1.6.0^{commit}=0f6ec603993d5595e784fa7079837e299d1b0da3`。
- 本轮固定 main：`9abc48794ebf82b8e918c593ebdada8cc080fe61`。
- 集成分支：`codex/v1602-final-integration`。
- ClawHub/OpenClaw：相对 `0f6ec603` 的 `openclaw/` diff 为0，继续冻结在v1.6.0。

## 已纳入的产品与工程范围

1. 通用 `SKILL.md` frontmatter 只保留 `name`、280字触发 `description` 和 `metadata.tags`；版本、兼容列表、安装路径、平台嵌套字段及 license 不再占用运行入口。
2. description 首句改为“用于中文公文、事务性材料和新闻稿件的起草、改写、压缩和复核”，机关、企事业单位、学校、新闻机构后置，“个人求职”排除项保留。
3. 非冻结运行面将“顺稿”改为“润色修改”，将“收束”改成结尾、作结、自然结束等普通说法；`先……再……` 只作为全文通读的软线索，不作词表禁令。
4. canonical 与 `skills/` 完整包采用 MIT；`.agents`、`.qwen`、Hermes 与冻结 OpenClaw 纯 Skill 面采用 MIT-0。SkillHub 清洁包以 `LICENSE.md` 携带根 MIT 全文。
5. AGENTS 工程控制面完成归档、去重和三模型匿名审查；Kimi K3、Grok4.5、Qwen3.8-max 清洁复放均偏好候选，第一次受污染的 Qwen 审查原样作废。
6. Hook 生命周期文件进入专属 `hooks/`；共享 `review_gate.py` 仍在 `scripts/`。Codex、Claude Code、WorkBuddy/CodeBuddy 使用宿主薄适配器，普通 Skill 安装不自动启用或修改用户配置。
7. Hook 收窄了纯审稿触发，删除未决转进行态预放行，修复低于篇幅下限后继续缩短的漏洞，并保护请求中明确给出的负结果及采购决定、审批、责任、期限等对象。`原因尚未查明` 与 `正在核查` 没有被机械判成互斥状态。

## description 真实路由边界

最终280字候选共做三轮、48次正式调用。Ollama 4/4配对、Alibaba `alibaba-token-plan-2` 4/4配对有效；MiniMax 最终只有2/4配对有效，另外两对读取 Windows KnownFolder 的用户级 `.agents` 同名 Skill，按预注册作废。有效样本没有形成跨 provider 重复的 Candidate 独有错路由，但三 provider 严格门没有建立，也没有新闻入口流量提升证据。该文字按用户明确的人类可读入口规格纳入，不宣称路由质量提升。

## Hook enabled / disabled 真实写稿

- 9对、18次全部技术有效；Token Plan 2 DeepSeek V4 0731、Ollama DeepSeek V4 0731、MiniMax M3 各3对，均为 `max`，外层重试0。
- SOL 主裁判原判为 Enabled 1胜、Disabled 7胜、1难分；Kimi、Grok均为 Enabled 2胜、Disabled 5胜、2难分。Qwen3.8-max 确认使用 `alibaba-token-plan-2/qwen3.8-max`，正式裁判在1200秒超时，记 INVALID，不补跑。
- 原始严格口径把 P003、P009 的常规后续工作措辞同时计为 Enabled 独有状态外扩，形成 `HOLD`；原判完整保留。
- 用户随后明确业务口径：不新增具体主体、期限、制度或决定状态的“按计划推进、确保按期完成、按规定程序、按既定安排”等正式材料衔接，不作硬外扩。复核后 P003 与 P002 不再计硬失败；P009 仍因补入具体程序事实并把已经更新完成的42项元数据写成继续推进而保留一例硬观察。
- 同机制不再跨两个独立配对重复，预注册硬停线在用户业务口径下通过。Hook 可作为默认关闭、显式启用的可选伴随物进入 MIT 完整包；不宣称整体质量领先。
- 三家纯审稿均无 transaction、无 Stop block、无代改。六个 Enabled 写稿均原样发射 D0，D1为0；每个写稿 Enabled 多一次 Stop block，存在延迟成本，且没有证明 D1 或篇幅改稿收益。Hook 不能描述为全面事实、文种、要素或篇幅兜底。

## 宿主与清洁包

- Claude Code 2.1.195 已通过第三方 Anthropic-format gateway 验证 UserPromptSubmit、PostToolUse:Read、Stop 与D0发射；不登录 Claude。Bash 与真实D1仍未验证。
- Codex 与 WorkBuddy/CodeBuddy 分别使用 `${PLUGIN_ROOT}`、`${CODEBUDDY_PLUGIN_ROOT}` 的独立 Hook command surface；真实配置子进程均完成 UserPromptSubmit→Read→Stop，Codex返回 `decision:block`，WorkBuddy返回 `continue:false`。
- OpenAI plugin validator 对 canonical 与清洁包通过；本机 WorkBuddy 5.3.8 内置 CodeBuddy 2.115.0 对 canonical 与清洁包均 `Validation passed / valid:true`。这些验证不等于真实交互式 Codex/WorkBuddy 模型生命周期。
- SkillHub 测试坐标 `1.6.2` 清洁包：46文件；manifest SHA-256 `071b7dfd885e616d8215ead37f2d9a369ad74a62047c6198cf4bdfd4b3c4c656`；`LICENSE.md` SHA-256 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`。
- SkillHub CLI 2026.8.5 dry-run 返回 `dryRun:true`、slug `chinese-official-writing`、version `1.6.2`；未上传。仓库插件与 README 正式版本面仍为已发布1.6.0，发布前必须另做1.6.2版本同步提交。

## 最终实际验证

| 检查 | 结果 |
| --- | --- |
| 全量 unittest | 521/521 PASS |
| Promptfoo stub smoke | 20/20 PASS，run `eval-K0o-2026-08-11T13:41:31` |
| 固定 main 消融 | main 109/111；current 111/111 |
| Skill quick validate | PASS |
| Codex plugin validator | canonical 与清洁包 PASS |
| WorkBuddy/CodeBuddy validator | canonical 与清洁包 PASS，`valid:true` |
| Python compile | Hook、适配器、lint、review gate、builder、sync、preflight 全部 PASS |
| 镜像同步 | 连跑两次均无 diff |
| OpenClaw 冻结 | 相对v1.6.0 diff为0 |
| `git diff --check` | PASS |

## 保留的失败与无效记录

- description 证据提交前曾误写一个 unittest 方法名，产生1个 loader error；用源码中的正确方法名复跑3/3通过。
- SkillHub 专用 frontmatter 被误送入通用 `quick_validate`，因平台字段不同被拒；canonical quick validate通过，发布包改用SkillHub CLI、builder与插件 validator验证。
- Windows 下直接执行无扩展名 Bash `skillhub` wrapper曾静默退出或无输出，非JSON调用又持续无输出并在约60秒终止；直接调用其实际 Python CLI 后dry-run正确返回JSON。
- CodeBuddy 2.115.0 不支持 `plugin validate --json`；该错误调用未计通过，去掉 `--json` 后隔离 HOME 复跑成功。
- 暂时排除 Hook 发布包后，首次全量521项有3个旧契约断言失败；用户业务口径复核撤销排除提交，最终全量521/521通过。
- Qwen3.8-max 补充盲审使用 Token Plan 2，但1200秒超时，无终稿、零重试，记 INVALID。

## 未完成与不夸大项

- 没有独立自动补字或篇幅兜底；现有 Hook 只保证可证明的D1不进一步恶化已知篇幅偏差，本轮没有真实D1。
- 短事务稿稳定功能仍以短单项采购为主；短通知候选因标题和复杂路由缺口继续HOLD，未混入本候选。
- `draft-body / gap-note-allowed` 路由、评价强度规则删除及其他未通过原子没有进入发布组合。
- 规则文本中仍有必要的真实顺序“先……再……”；没有做机械全局替换，也不把正常公文工作安排视为AI味。
- 尚未确定或同步正式发行版本，未合并main、未推送、未打tag、未创建GitHub Release、未向SkillHub或ClawHub上传。

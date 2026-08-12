# v1.6.2 Hook 真实写稿与 v1.6.0 DIFF 冷审预注册

## 固定对象

- 候选产品根：`0d53b3656e351020600b3754d1fe06ff2fc26ddd`；正式调用前记录预注册提交，产品面不得再改。
- 固定上一发布基线：`v1.6.1` 产品根 `2135fba6e05ee9a3d9c9f931237a9eb01b0cc107`。
- 完整变更冷审基线：`v1.6.0^{commit}=0f6ec603993d5595e784fa7079837e299d1b0da3`。
- 真实 Hook 宿主：从候选静态源组装、校验但不安装的 Claude Code companion。两臂唯一命令差异为是否传入 `--plugin-dir`。
- 未纳入篇幅补写 Hook；不得从历史 length/under-length worktree 复制任何实现。

## 写稿矩阵

三条 provider lane，每条内部串行，合计 9 个配对、18 次调用，零重试、只取第一次终稿、每臂上限 1200 秒：

调度实现使用恰好 3 个 provider worker；每个 worker 只处理一家 provider 的 T1→T2→T3 及各题两臂，不在同一家内并发。最终 manifest 按 pair/slot 重新排序，不以返回先后改变匿名映射。

| Provider | 精确模型 | 用例 |
| --- | --- | --- |
| OpenCode Go | `opencode-go/deepseek-v4-flash-0731` | T1、T2、T3 |
| Ollama | `ollama-cloud/deepseek-v4-flash-0731` | T1、T2、T3 |
| Alibaba Token Plan 2 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | T1、T2、T3 |

所有调用使用 `max`，通过本机 `127.0.0.1:10100` 第三方网关接入 Claude Code，不登录 Claude。正式启动前须对三个 provider 跑只读连接检查和精确 `/v1/messages/count_tokens` 路径探针。

- T1：180—260 字接口异常情况说明，覆盖时间、时长、核查范围、否定结果与原因未决。
- T2：650—850 字制度正文，覆盖职责边界、程序、紧急事项和试行未决状态；禁止补期限起算、复提、重新计算和材料义务。
- T3：900—1200 字活动新闻稿，覆盖新闻事实与边界；不得补领导、口号、嘉宾、签约、成效评价、后续计划或引语。

每个配对采用 AB/BA 交错顺序。每臂使用独立 `CLAUDE_CONFIG_DIR`、临时目录和插件数据目录，移除真实 Claude/OpenAI 凭据；同题两臂 prompt、模型、工具权限和规范化环境必须一致。

## 技术有效性

共同条件：rc=0、未超时、恰好一个成功终态、非空终稿、模型三处绑定一致、API key source 为 none、读取声明的精确 Skill、无 Skill 根外读取、隔离 auth 显示未登录、JSONL 可解析。

- Hook off：不得注册 companion，不得出现 Hook start/response，不得产生门禁数据。
- Hook on：companion 已注册；UserPromptSubmit、PostToolUse、Stop 均有 start/response；至少保存一个 adapter turn；起草任务须形成 gate transaction。记录 Stop block、D0/D1、终稿 hash 和耗时。
- 任一臂无效则整对无效，不补跑。有效覆盖要求至少 6/9 对、每 provider 至少 2 对、每文体至少 2 对；否则只报技术不足。

## 匿名盲审与准入

仅技术有效配对进入匿名随机盲包。解盲前冻结 packet、mapping、manifest 和哈希。Kimi K3、Qwen3.8-max、Grok4.5 分别只读同一盲包；模型路径为 `kimi/k3`、`alibaba-token-plan-2/qwen3.8-max`、`xai/grok-4.5`，均为 max、单次上限 1200 秒、零重试。任一裁判超时、空终稿、路径不符或污染即 INVALID，保留原始记录。

逐稿检查 facts/state/length/output scope、要素完整、自然度、可直接采用成本；硬边界覆盖文风票。启用臂若出现同一硬维度两次独有失败，写稿结论 HOLD。由于两臂为独立模型采样，票数只作整体非劣观察；Hook 实际收益必须结合 on 臂内部 D0/D1 和事件链归因，不能把随机 on/off 胜负直接称作 Hook 修稿收益。

## v1.6.0 全量 DIFF 冷审

另生成不匿名的自包含 DIFF packet，至少列明：

1. v1.6.0→候选的 canonical `SKILL.md`、references、scripts、Hook 产品差异；
2. 纯目录迁移、许可证/README/发行包变化与真实行为变化分栏；
3. 新闻/新闻评论入口和叶子；
4. Hook 能力、默认关闭、任务 opt-out、无 Hook 闭环、三宿主静态适配、数据与知情边界；
5. 孤儿文件、断链、魔法数字/大字典/上帝函数与已登记技术债务；
6. 篇幅补写 Hook 未进入候选；
7. 工程测试和真实写稿结果。

Kimi K3、Qwen3.8-max、Grok4.5 分别冷审该 packet，给 P0/P1/P2、误报、品牌文案过度承诺和是否可进入本地候选。只采纳 packet 可复现且能回到源码、diff、测试或日志交叉验证的结论；不因多数票自动修改产品。

## 停止条件

- 候选产品根在正式调用后漂移；
- 发现外部 Skill/记忆/AGENTS 污染；
- 组装包链接、manifest、宿主变量或事件 smoke 失效；
- 任何篇幅补写实现进入当前树；
- 真实写稿门槛不足或重复启用臂硬失败；
- 冷审发现可复现 P0/P1；
- 任何发布、推送、tag、安装或真实宿主配置修改。

满足停止条件即 HOLD，不能追加样本、重试失败调用或择优删除不利结果。

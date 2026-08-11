# AGENTS 工程控制面精简结果（2026-08-09）

## 结论

根 `AGENTS.md` 已从产品写稿规则和逐版发布流水中隔离出来，只保留仓库开发、Git/worktree、测试、回归、评分、匿名盲审、DIFF 归因、发布回执和安全纪律。候选经工程回归与真实写稿对照后 fast-forward 合入本地 `main`；未推送、未发布。

- 精简提交：`99f63d87`。
- 实时安全门补充：`1780c421`。
- 原文件：122091 bytes。
- 合入文件：6947 bytes，减少约 94.31%。
- 原始历史按字节保存在 `docs/evidence/AGENTS-history-through-v1.5.39.md`，历史不是当前运行指令。
- canonical Skill、references、脚本、评测数据和发行镜像没有产品差异。

## 实时安全门修补

首版候选把第三方采纳、核心行为扩面和落地后消融纪律只留在历史快照。冷审后把以下内容恢复到实时根控制面，并让边界测试直接检查当前 `AGENTS.md`：

- 第三方实现只能作为线索，不直接誊抄代码、脚本或大段 Prompt；
- 不新增重排版引擎，不扩大默认联网或默认强制确认；
- 不破坏用户模板；
- 候选落地后继续做基线对比、消融和回归。

## 不显式读取 AGENTS 的真实对照

两臂的 Skill 产品内容相同；唯一宿主差异是旧 122KB 与精简 AGENTS。任务没有要求写手读取 AGENTS，也没有泄露测试目标。

### S1 稀疏情况说明

| Provider | 旧 AGENTS | 精简 AGENTS | 结果 |
| --- | --- | --- | --- |
| Alibaba DeepSeek V4 Flash 0731 high | `019fe227-4210-7313-be68-e094d904fc69` | `019fe227-46d5-7c20-b717-ca0d25d5246f` | 旧臂把“接口恢复”补强为“恢复正常”；精简臂保留“恢复”。 |
| Ollama DeepSeek V4 Flash 0731 high | `019fe227-420f-7e63-a3ea-c33d89a82805` | `019fe227-447b-73e2-8bb3-1ce65f92c7a4` | 同样由“恢复正常”回到材料原词“恢复”。 |
| Luna high | `019fe227-42dd-7691-89d2-7638c226fdb2` | `019fe227-447b-73e2-8bb3-1d0795c9b2a8` | 两臂最终正文均准确。 |

### M1 未决事项纪要

| Provider | 旧 AGENTS | 精简 AGENTS | 结果 |
| --- | --- | --- | --- |
| Alibaba DeepSeek | `019fe227-441f-7823-b809-c4be3ab3333e` | `019fe227-4ea7-7c30-a752-74ee14190bc9` | 旧臂保留“下次会议时间未定”；精简臂单次写成“另行确定”。 |
| Ollama DeepSeek | `019fe227-441f-7823-b809-c498557f8f8d` | `019fe227-4ea9-7d03-932b-9db7fb9136dc` | 两臂均保留未决状态。 |
| Luna | `019fe227-4422-7ba3-9d3b-4ca9161c4e4a` | `019fe227-4ea7-7c30-a752-74c16959b12a` | 两臂均保留未决状态。 |

Alibaba 同题补做两次逐字复放：旧/精简分别为 `019fe228-e7ca-77a0-ac09-dc3ce9ca7592` / `019fe228-e7e2-71d1-95f4-9d5b20365348`、`019fe228-e7cb-77d0-a243-50f30cd88344` / `019fe229-00c5-7010-9891-cbff987ec907`。四稿均保留“下次会议时间未定/未确定”，首轮单次偏移未复现；且 AGENTS 差异不含任何会议状态写作规则，按生成噪声处理。

## 工程验证

- focused boundary：1/1 PASS。
- full unittest：454/454 PASS；合入 `main` 后再次 454/454 PASS。
- Promptfoo smoke：20/20 PASS；合入后 eval `eval-Aa7-2026-08-08T16:31:20` 仍为 20/20。
- 固定确定性消融：main 111/111，Candidate 111/111。
- skill-creator quick validate：PASS。
- `git diff --check`：PASS。

首次在桌面已回收的残缺临时 worktree 复跑曾出现 83 error、9 failure；换到完整物化的同提交 worktree后全部通过。该次只记环境失败，不计候选回退。

## 边界

这组证据支持工程控制面隔离及上下文减载，不证明 AGENTS 精简本身普遍提升写作质量。旧 AGENTS 是绝对表现的混杂因素，但同一 A/B 两臂共享它时，不能把无关差异都归因于 reference；后续真实 Prompt 实验继续记录宿主上下文并只评价与 DIFF 有直接语义或读取轨迹联系的回退。

# v1.6.13 后公开原子本地 main 集成回执

日期：2026-08-23。

状态：`INTEGRATED_LOCAL_MAIN_NOT_RELEASED`。本文件随最终净差异以 squash 方式进入本地 `main`；未推送 `origin/main`，未修改 v1.6.13 tag，未创建 Release，未上传 SkillHub.cn 或 ClawHub。

## 固定基线与净范围

- 已发布产品 tag：`v1.6.13^{commit}=c4ea80a6146a2c672fdec8aeb8de13ed547f33f9`。
- 发布回执基线：本地 `main` / `origin/main@4b51fd8242850e5c35fe86406216f6cfd26f49c0`。
- 集成研究分支：`codex/v1614-next-atomic`；最终产品差异 fingerprint：`5654f2b237d4bed53ca5e231ebe121a6047da0dd`。
- 净产品文件10个：4个 Hook 实现/配置文件、Hook README、canonical `information-selection.md` 与四套普通镜像；description、版本 manifest、Red SkillHub、付费分支和 `output/` 净差异均为0。

最终只接入四类已验证原子：

1. `UL-005`：删除已完成事项遗留的 `known_hold`，不改变 under-length 运行语义。
2. `OV-001`：校准超长语义判定；只在具体事实、状态、主体、关系、文种功能或直接可用性风险成立时失败，不把更短、单句成段或一般措辞偏好本身当作失败；repetition observer 的删除目标和保留目标都必须是 sentence，保留目标不得为 tail。
3. `HK-008`：终态清理插件数据目录内的事务文件、原始请求、D0、观察包和选择稿，只保留 hash、计数、阶段、选择与交付状态；异常中断、宿主日志和未知字段仍按明确风险保留。
4. `WR-014-R3`：能力或选项“可安排、可开展”保持“可”；明确“拟、计划、将”保持原强度。

## 被淘汰而未进入产品的原子

- `MT-005c` 193字受众合并在第一次全量门触发 P058“description missing 学校”。
- 196字最小回补的学校、协会正向均读取公文 Skill，社媒没有误触发；但两份正向正文分别新增“另行通知/试用安排”和把“每家可报1名”升级为“请安排1名”。最终恢复已发布204字 canonical 与四镜像。
- `WR-018` 五路三文种为13/15硬通过、0/15功能性过薄，因此不新增字数门、固定段数、统一扩写流程或新闻效果模板。

## 真实写稿与生命周期

- `OV-001`：五路采购请示222—251字且完整；三题五路语义判定15/15方向一致；CodeBuddy 两稿分别328→236、496→229，均一次压缩、`semantic_pass`、D1/hash闭合；Kimi K3、Grok 4.6、Qwen 3.8 Max、SOL 对两个匿名案例均4/4选择达标稿。
- `WR-014-R3`：原始“可安排”反例五路有效稿5/5保持“可”；明确“拟于”正向控制四路有效稿4/4保持“拟”和未决审核，OpenCode 两次 provider stream 失败只记技术失败。
- `HK-008`：CodeBuddy 2.115.0 真实采购申请在终态保持 D0 逐字交付，`raw_artifact_delete_failures=0`，原始事务数据移除。
- `WR-018`：采购申请、异常报告和活动新闻五家 provider 共15稿；MiniMax A 状态升级、Ollama C 重复/旁白为真实残余风险，其余13稿通过，六个 Desktop 任务提取后已归档。

## 合并门实际结果

| 检查 | 结果 |
| --- | --- |
| 第一次全量 unittest | 660项、1项失败：P058 缺少“学校”；用于淘汰 MT-005c，不记通过 |
| 恢复204字后的全量 unittest | `660/660 PASS` |
| 最终 OV/HK/WR/链接聚焦 | `69/69 PASS`；此前 description/真实 prompt/边界聚焦 `95/95 PASS` |
| Promptfoo 本地 stub smoke | `20/20 PASS`，Skill 10胜、baseline 0胜、judge consistency 1.0；未调用付费模型 |
| 固定 main/current 确定性消融 | `111/111` 对 `111/111` |
| Skill Creator quick validate | `Skill is valid!` |
| Python compileall | PASS |
| `sync_adapters.py` 二次执行 | 无净 diff |
| JSON | host capabilities 与三宿主 manifest 均可解析 |
| SkillHub 本地清洁包 | 61文件，slug `chinese-official-writing`，version 仍为 `1.6.13`；只作构建检查，不上传 |
| ClawHub 包 | 33个 tracked 文件，Hook/outline/paid 路径与文本命中0；只作检查，不上传 |
| 禁入与版本 | paid/outline 路径0、Red SkillHub diff 0、output diff 0、manifest/version diff 0 |
| `git diff --check` | PASS，仅 Windows 换行提示 |

## 冷审

独立只读冷审先发现并阻断两项状态问题：OV-001 已接入代码但缺少本轮证据文件；WR-014/HK-008 仍写“候选、未合入 main”。补入仅含公开 OV 原子的五路 writer、15/15 verifier、两次 CodeBuddy 生命周期和四方盲审摘录，并更新 coverage、待办、roadmap 后，复审确认：

- 两个 blocker 已解除，全部相对链接可达；
- 最终产品只有 UL-005、OV-001、HK-008、WR-014 四类原子；
- MT-005c 产品净差异为0；
- 没有付费提纲 Hook/coordinator、章节/hash 实现、output、版本或发布变化；
- 可以把最终净差异 squash 到本地 main。

## 剩余风险

- Hook 继续默认关闭、按单能力窄启用；单次真实压缩仍可能需要约4分钟和较高 cache-read。
- D0 回退只证明安全，明确篇幅未达标时不能冒充成功。
- HK-008 不能清理宿主自己的 debug/trace；终态前异常退出和未来未知原始字段仍需精确检查。
- 真实官方稿通常拥有更多政策依据、附件、方法、责任和办理链；当前稿件篇幅差距不能靠补造内容弥合。

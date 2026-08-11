# 方案叶与新闻路由组合验证记录（2026-08-03）

## 结论

以发布基线 `14fae4c8e5f12b91fe88b02214f847dca538acde`（1.5.34）为对照，本地 `main` 仅合入两项经隔离真实写稿验证的修改：

1. 方案、实施方案、建设方案叶改用自适应骨架，与权威文种路由对齐；
2. 权威文种路由补齐新闻消息、新闻评论定义，评测 provider 的只审新闻任务按文种加载既有专项叶。

组合回归通过。未改版本号，未打 tag，未推送或发布。

## 主线提交

- `76bf541c`：方案叶自适应骨架；
- `8f02e667`：新闻权威路由与只审加载覆盖。

方案叶最终规则为：

> 以目标、主要任务和实施路径为主线，责任、进度、保障、验收与风险控制按材料和用户模板落位。

这条规则不强制把七类要素逐项拆节，不修改 `SKILL.md` 路由、reference 加载条件、事实边界、篇幅规则、复核顺序或发布链。

新闻修改只增加权威文种定义和 review-only provider 加载；canonical `SKILL.md`、新闻消息叶、新闻评论叶与 1.5.34 逐字一致，未把复核规则前移到起草阶段。

## 被拒绝的实现

### 方案骨架 R1

R1 将方案固定为“目标与范围—主要任务—实施路径—责任分工—进度安排—保障措施—验收与风险控制”。两题盲审均判基线胜，主要回退是进度、任务、验收和保障内容重复。该实现保留在隔离分支，不合并：

- 产品提交：`330f723c`；
- 结果提交：`5d3b62b1`；
- 结果记录：`tests/evidence/plan-skeleton-authority-v1534-r1-result-20260803.md`。

### 新闻路由 R1

R1 同时把“起草/成稿复核”段放入新闻起草可见上下文。有效样本出现整组事实复述，另有运行不对称样本不能作为质量证据。该实现保留在隔离分支，不合并：

- 产品提交：`bf825083`；
- 结果提交：`86bf615f`；
- 结果记录：`tests/evidence/news-authority-review-v1534-r1-result-20260803.md`。

## 隔离真实写稿证据

### 方案叶 R2

产品提交 `94c5e3bf`。两题复用逐字一致原始任务和固定 1.5.34 基线稿，Candidate 各取首个技术有效输出，writer 与盲审分离：

| 任务 | 盲审 | 硬项 | 主要结果 |
| --- | --- | --- | --- |
| P01 窗口服务实施方案 | Candidate 胜 | 通过 | 990 字，验收标准嵌入验收阶段，减少步骤、任务和验收重复 |
| P02 统一认证建设方案 | Candidate 小胜 | 通过 | 1044 字，任务衔接较完整；保留两处轻微阶段衔接套话观察项 |

四稿均无事实、数字、日期、主体、状态、文种或输出范围硬伤。完整记录在隔离分支 `7a166121` 的 `tests/evidence/plan-skeleton-adaptive-v1534-r2-result-20260803.md`。

### 新闻路由 R2

产品提交 `5a208be1`。N03 为未直接点名文种的门户会议公开稿任务：Candidate 读取入口、信息选择、权威文种路由和新闻消息叶，一次首稿判为新闻消息；明确事项作为已发生事实报道，未转成纪要责任清单或通知办理要求。

- Candidate：586 个非空白字符；
- 固定 1.5.34：420 个非空白字符；
- 两稿 lint：无 findings；
- 匿名盲审：Candidate 胜；
- 硬项：事实、数字、主体和状态通过。

Candidate 距“约 600—800 字”下限 14 字，并有轻度任务链重复和责任清单感，继续作为观察项。完整记录在隔离分支 `7333b3cc` 的 `tests/evidence/news-authority-review-v1534-r2-narrow-result-20260803.md`。

## 组合工程验证

在包含 `76bf541c` 和 `8f02e667` 的本地 `main` 实际运行：

- `python -m unittest discover -s tests`：442/442 通过；
- `$env:OFFICIAL_WRITING_EVAL_STUB='1'; npm run eval:official-writing:smoke`：20/20 通过；
- `python tools/run_real_prompt_ablation.py --baseline-root <固定1.5.34工作树> --baseline-label 1.5.34 --current-root . --out <结果目录>`：baseline 111/111、current 111/111；
- `C:\Users\admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`；
- 方案叶六套镜像 SHA256 均为 `2F13151FA09A565813143986CF19473D2F179F165152420BE423233DA459AB14`；
- 权威文种路由六套镜像 SHA256 均为 `069E1771BCD01D4ACB0A0506E0A9CD76D4299ADDB45B4B89E7B9B83B9D715308`；
- `git diff --check 14fae4c8..HEAD`：通过。

确定性消融摘要位于 `output/research-evals/plan-news-main-integration-20260803/summary.md`。该消融不调用 LLM，只作为路由和工程支撑证据；真实写稿质量结论以上述独立 A/B 与盲审为准。

## 后续研究项

以下三项只登记，不在本轮实施、组合或预先加补丁：

1. 述职专叶：只处理述职，研究“职责—履职—问题—改进”结构；
2. 叶内“使用方式”说明压缩：先选单叶做短句归并，不新增公共 reference；
3. Candidate H：只复验解除重复段内公式，不带入后续失败的篇幅救援或段落展开 Prompt。

## 剩余风险

- 方案 P02 仍有两处轻微阶段衔接套话，当前未在三次正常场景复现，不作共性修复；
- 新闻 N03 仍略低于约定下限，并有轻度任务链重复，后续扩大新闻样本时继续观察；
- 本轮验证了新闻起草文种判断和评测 provider 的加载逻辑，没有把只审任务的语言质量另行扩成模型矩阵；
- 本轮未重复生成 true No-Skill 对照，结论限于相对固定 1.5.34 的冲突修正与功能覆盖。

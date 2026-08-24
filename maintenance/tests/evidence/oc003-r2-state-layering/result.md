# OC-003-R2 可研事实状态与条件建议分层结果

日期：2026-08-25。

## 结论

`VALIDATED_INTEGRATION_CANDIDATE / READY_FOR_LOCAL_MAIN_MERGE / NOT_RELEASED`。

本轮把上一候选的绝对保护改为两层：事实层不得把未决事项写成已启动、已确定或既定程序；建议层允许条件态的一层方案比较、技术指标、风险控制和运行验证意见。正向可研起草三条 Candidate 均保留完整事实、未决状态和条件建议；显式激活的反向审稿在一次单句修复后，Luna、Ollama、Alibaba 三稿都只恢复或删除失实状态，不再补另一套程序。

候选由此完成上一轮 `MINIMAL_SCOPE_REPAIR_REQUIRED`，可以进入本地 main 集成检查。它尚未发布，不改变 v1.6.15 tag 或任何平台版本。

## 真实写稿与审稿

### 正向可研起草

| provider | Baseline | Candidate | 裁定 |
| --- | --- | --- | --- |
| GPT-5.6 Luna | 2844字符；事实、状态和条件建议完整 | 3176字符；事实、状态、同口径比较、技术指标、风险和运行验证完整 | `NON_REGRESSION_PASS`；两臂均有长篇展开，Candidate 没有过度保护 |
| Ollama DeepSeek V4 Flash 0731 | 4502字符；生成过程旁白、重复两版正文，并在第二版把2800/35万元写成2808/34万元 | 816字符；完整保留2800/2744/56、42/6/95、月3万/12月/36万、三组报价和全部未决状态，条件建议成立 | `TARGET_GAIN_PASS`；自动漏项是“每月处理3万张/处于可行性研究阶段/尚未明确”的短语变体误报 |
| Alibaba Token Plan 2 DeepSeek V4 Flash 0731 | 1395字符；保留核心事实，但加入22个工作日、10个工作日/每日1小时等材料外情景假设 | 977字符；保留事实状态与条件建议，不写成已启动程序 | `TARGET_GAIN_PASS` |

Ollama Candidate 使用“三组供应商初步报价”这一不够严谨的搭配，材料原词是“三组初步报价”；它没有明确写出三家供应商或供应商已确定，作为措辞警告保留，不按过严判准否决整稿。Luna Candidate 的7200张人工复核量和报价差额均明确标为情景测算，计算可由已给比例、年量和报价直接复核，不冒充实绩。

### 反向只审

首轮自动路由中，Alibaba 两臂有效并安全；Luna 两臂读取用户级同名 Skill，Ollama 两臂没有读取隔离 Skill，四个臂均记 `TECH_INVALID`。显式激活控制保留相同材料、现稿和裁判，只增加当前工作区 Skill 读取要求，六个 A/B 臂全部技术有效。

显式控制的三个 Baseline 已能识别全部状态升级。第一版 Candidate 中 Luna、Alibaba 通过，Ollama 在删除“已具备立即采购条件”时又写“尚不具备采购条件”，属于 Candidate 独有反向结论。R2C 只增加“尚未形成决定不改成不具备/暂不具备条件”一句；最终三条 Candidate 都删除该结论并止于“尚未形成采购决定”等材料原状态，3/3通过。

## 调用与证据

- 首轮 A/B：两题×两臂×三路，共12次；8次技术有效、4次自动路由技术无效。汇总 SHA-256 `58d62ef26966f3e332542c3b9191a9222334ee45ff21f471854bff4627ecd2e2`。
- 显式激活反向 A/B：6次，6/6技术有效。汇总 SHA-256 `468065ffc42b1be8709f568f58b461b793e85622d0fcfcd05903981be386c756`。
- R2C Candidate-only：3次，3/3技术有效、3/3人工硬边界通过。汇总 SHA-256 `e2a5ea9ad2f1f5bd9c3d342a3f24b6816be1aaa638fb4c1caf11f99f2722f41d`。
- 合计21次 Codex CLI 调用，17次技术有效；无质量重抽。原始 final、trace、stderr、usage、fixture 和 summary 位于三个忽略目录 `output/oc003-r2-state-layering*`、`output/oc003-r2c-condition-state/`。
- Baseline Skill：71文件，fingerprint `39542c6037d84c72668636267ebdc8e0928aadd4e9fe0523749e53464f955d6b`。
- 首版 Candidate：71文件，fingerprint `f507f48b2fdc3b417b50146ee9a74af7193496be5ca34486a16e1648dc887927`。
- R2C 最终 canonical Candidate：71文件，fingerprint `267f2b7da306b2db8ce69bd80101f1c9c692bc150103793714d0c664ec26834b`。

## 产品与工程边界

产品只改四个近场 reference：`ai-compute-docs.md`、`argument-chains.md`、`workflow.md`、`genre-checklist-feasibility-review.md`，并逐字同步 Agent Skills、Hermes、OpenClaw、Qwen Code 四套普通镜像。没有修改入口 description、信息选择通用规则、Hook、adapter、版本号或付费分支。

五提交暂停检查确认产品差异仍限上述四个 canonical reference；消融证据是修复前同一 Ollama Candidate 把“未形成决定”改成“尚不具备采购条件”，修复后三条 Candidate 均不再出现该结论。直接验证结果：

- `python -m unittest ...` 五项 reference 路由/边界测试：5/5通过。
- `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- OC-003 语义与镜像测试加既有全镜像测试：3/3通过。
- 新测试首跑因 `ROOT` 多取一层父目录产生2个 `FileNotFoundError`；既有镜像测试当时通过。提交说明已改为真实失败，随后单独修正路径并重跑3/3通过。

当前分支未合入 main、未 push、未创建 tag/Release、未上传平台。合入本地 main 后仍需运行一次合并门并把规格中的旧 `MINIMAL_SCOPE_REPAIR_REQUIRED` 回填为已完成、未发布。

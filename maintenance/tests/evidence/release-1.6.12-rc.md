# v1.6.12 本地候选基线

日期：2026-08-21

状态：`READY_LOCAL_CANDIDATE`。本文件绑定本地发行候选；正式发布回执完成前，不表示 GitHub、SkillHub.cn 或 ClawHub 已存在 v1.6.12。

## 固定对象与范围

- 当前公开版本：`v1.6.11^{commit}=15af538adfb5ec6a711770d67ec265498ec7127d`。
- 当前远端发布回执：`origin/main@b0952c0e8a7a143ac23c1bb98cbbec1a66bbf62c`。
- 本轮候选内容基线：`main@0b8f4d6a844fd52275968286a511e2531789c0bf`。
- 本地候选分支：`codex/release-v1.6.12`。
- 版本准备提交：`e10e2cbf2283ab95b5259577e513790ad0a48ce5`。
- 消融断言修正提交：`06bf8b247481162d7df66238f87224bcdc92c6ee`。
- 目标版本：`1.6.12`。
- 候选包含本地 main 已合入的 description 原子减载、状态收口和研究证据；各 HOLD 或已撤回实验的产品改动不在候选内。
- 公开包仍不包含本地付费提纲能力；`codex/paid-outline-review` 不反向合入本候选。

## 发布内容

1. 删除 description 中已由上位公文类别或正文边界覆盖的重复负向句和文种细项，降低每次发现阶段的上下文开销。
2. 保留“公文、事务性材料、新闻稿件”三个正向入口，以及申请、请示、报告、通知、函、纪要、制度、方案、工作要点、讲话、致辞、可研、审查材料和 AI 算力等已验证原子。
3. 制度、函件、讲话致辞、受众合并等出现候选独有硬回退的较大减载方案均未进入本候选。
4. `UL-005`、`OT-001` Stop 收紧、`OT-002`、`WR-010` sidecar 和 `OV-001 × AH-001` 后续关系实验均继续 HOLD，不进入公开产品。

五条模型路线用于扩大有效样本和抵御单一路线技术失败，不按票数放行。技术失败记为 `INVALID`；任一有效稿中的事实、状态、文种、指令或直接可用性硬回退均保留为风险。

## 真实写稿与消融

- 各 description 减载原子已按正向触发、相邻非触发和真实成稿逐项 A/B；通过项才进入 main。
- 5路线×基线/候选×学校/新闻机构/家人群的受众合并共30稿和30份读取回执；候选独有地把“8月28日”补成“2026年8月28日”，因此193字合并候选撤回，当前发布204字已验证版本。
- 固定 v1.6.11/current 消融首次暴露7个旧 description 字面断言；修正为“上位类别＋叶子路由”和“排除或完全省略”双态契约后，两边均为111/111。

## 发布门

- 版本面定向测试87/87通过；canonical、Agent Skills、Qwen Code、Hermes 四个普通入口通过 quick validation。
- 全量测试首次639/640，唯一失败是 `test_real_prompt_ablation` 仍要求 description 原样包含“采购公告”；更新为“公告”上位入口并继续检查“采购公告”叶子路由后，单项1/1、最终全量640/640通过。
- `sync_adapters.py` 同步后镜像一致；发布前仍须做最终二次执行无差异检查和 `git diff --check`。

## 候选包与平台坐标

- SkillHub.cn 清洁包61文件，本地规范化文件树指纹 `62764bf3bff9e2f5e0c7829252997462efd101678f4873ab1d9c5752de89479a`；slug `chinese-official-writing`，展示名“中文公文写作”，现有条目为 `@user_f3d82da7/chinese-official-writing`。dry-run 返回 `dryRun=true`、version `1.6.12`。
- ClawHub 使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 包，本地规范化文件树指纹 `620ccd494314d240d2e2a4e76bf031b6c35c9679f885834f1b0275eed52b870d`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中均为0。
- ClawHub 坐标固定为 owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`。有效 dry-run 返回 `would-publish`、latestVersion `1.6.11`、fileCount `33`、平台 fingerprint `c118b2be2518c68115399d4569db9eac9538bddbee2cb65c4ae4f0b413b9981d`。
- 第一次 ClawHub dry-run 的 `source-commit` 未先由 Git 解引用，只用于本地预览并作废；随后以 `git rev-parse HEAD` 的真实40位提交重跑，正式发布还须绑定最终 tag 提交再执行一次 dry-run。
- 两包许可证与根 MIT `LICENSE` 的 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`。

## 当前发布边界

- 用户已明确授权发布 GitHub、SkillHub.cn 和 ClawHub；ClawHub 必须继续使用上述33文件无 Hook 包。
- 本文件写入时尚未推送 main、创建 tag 或 GitHub Release，也未正式上传 SkillHub.cn 或 ClawHub。
- 正式外部写入前仍需 fetch 并核对远端 main/tag 无漂移，以最终产品提交重跑包体、slug、展示名和 dry-run 检查。

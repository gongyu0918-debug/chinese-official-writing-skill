# v1.6.23 本地候选记录

日期：2026-08-31。

状态：`PUBLISHED / SEE release-1.6.23.md`。下文保留正式发布前的冻结快照；最终回执与传播状态见 [`release-1.6.23.md`](release-1.6.23.md)。

## 候选边界

- 固定产品基线为 `main@a6764b7e61c5939c3dd098d556bf3e8d36a298a3`，版本坐标提交为 `6a6ededa`，分支为 `codex/release-v1.6.23`。
- 上一公开产品仍是 `v1.6.22^{commit}=4b135c506b4b4d61f49115298bc78564b5ec8f50`。本记录只冻结本地候选；未创建或移动 tag，未推送，未创建 GitHub Release，也未向 SkillHub.cn、ClawHub 或其他平台提交。
- 相对 v1.6.22 的产品增量包括：`UL-006-CONTRACT-R1 / HK-009-STOP-BUDGET-R1` 的事故入口契约统一、单 Stop 共享预算、可信恢复和有限失败脱敏；`MT-004b-REVIEW-DIRECT-LEAF-R1/R2` 的点名只审轻页与五套公开镜像。对应目标反例、真实生命周期、五路真实审稿和主线合入证据见 [`post-v1622-hook-contract-r1/result.md`](post-v1622-hook-contract-r1/result.md)、[`post-v1622-hook-contract-r1/main-merge.md`](post-v1622-hook-contract-r1/main-merge.md) 与 [`reference-slimming-r3-current/result.md`](reference-slimming-r3-current/result.md)。
- 建议反馈语气、共性归并和 Word 小标题修复继续在独立分支验证，不是本候选祖先，不进入本次包体。付费提纲、Pro Hook 和红头 DOCX 仍在独立边界。

## 本次工程门

- `git merge-base --is-ancestor v1.6.22 6a6ededa`：通过；固定上一 tag 是候选祖先。
- 版本坐标后的聚焦回归：`python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_hook_layer_contract maintenance.tests.test_status_ledger_consistency`，101/101 通过。
- 产品坐标提交上的一次全量回归：`python -m unittest discover -s maintenance/tests -p "test_*.py"`，756/756 通过，耗时 112.841 秒。其后只增加本记录、状态登记和对应状态测试，不改产品字节。
- 固定 `v1.6.22` 与 current 的确定性真实用户式 Prompt 消融均为 111/111，双方起草失败和改稿失败均为 0；该门不调用 LLM。
- `OFFICIAL_WRITING_EVAL_STUB=1` 的 Promptfoo smoke 为 20/20，Skill 10 胜、baseline 0 胜、平票 0、无效 0、需人工复核 0，judge consistency 为 1.0；该门不调用真实写稿模型。
- canonical、Agent Skills、QwenWork、Qwen Code、Hermes 五套 Skill Creator `quick_validate.py` 均通过；170 个 tracked Python 文件完成编译，167 个 tracked JSON 文件完成解析。PowerShell 对较大的 `maintenance/package-lock.json` 解析受限，另以 `python -m json.tool` 原样验证通过。
- `sync_adapters.py` 复跑后 tracked blob 无差异；`assemble_hook_companion.py --help` 正常列出九个宿主和六项能力；`git diff --check` 通过。

## 本地包预检

- SkillHub.cn 清洁包为 83 文件，规范化文件树 fingerprint 为 `3c40dad50434d9f297c7b844357de72f5f439e0b1b932ce7903be926404ccf9a`；slug 为 `chinese-official-writing`、展示名为“中文公文写作”、版本为 `1.6.23`，含 `LICENSE.md`，排除根 `LICENSE` 与 `agents/openai.yaml`。
- ClawHub 发行目录为 34 文件，规范化文件树 fingerprint 为 `f0f69ba6322889643fa53654734e7c2293128f3e42738fddcce8f933d57edda8`；目录继续使用 `chinese_official_writing`，元数据版本为 `1.6.23`。Hook 路径、Hook 内容、`agents/openai.yaml`、付费提纲和红头实现命中均为 0。
- 两类包只在本地预检，没有 dry-run 或正式平台写入。平台 slug、展示名、owner、分类和话题未被本轮改动。

## 剩余边界

- 本候选已按用户明确授权从冻结分支和上述精确包面发布；最终 GitHub、SkillHub.cn 与 ClawHub 回执及传播状态见 [`release-1.6.23.md`](release-1.6.23.md)。
- 为运行 pinned Promptfoo stub 执行 `npm ci --ignore-scripts`，npm 对维护期开发依赖报告 36 项 audit finding（2 low、16 moderate、18 high）；`node_modules` 不进入产品或发行包，锁文件未改，本轮不以 `npm audit fix --force` 扩大范围。

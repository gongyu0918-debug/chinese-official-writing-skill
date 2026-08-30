# v1.6.22 本地候选记录

日期：2026-08-31。

## 候选边界

- 固定产品基线为 `main@736eca124b1dd8d1f95f6ce475b820ae2ead46cf`，版本坐标提交为 `4b135c506b4b4d61f49115298bc78564b5ec8f50`，分支为 `codex/release-v1.6.22`。
- 上一公开产品仍是 `v1.6.21^{commit}=8086ff255f04df8b080ef1a0488236295bf2cb8d`。本记录只把当前已验证主线登记为 `1.6.22` 本地候选；未创建或移动 tag，未推送，未创建 GitHub Release，也未向 SkillHub.cn、ClawHub 或其他平台提交。
- 相对 v1.6.21 的产品增量包括：`UL-006` 阶段性事故通报的无显式下限近转写兜底、短通知主体/日期关系边界、`WR-023` 申请原因与材料缺口边界、`WR-024` 请示缘由与材料缺口边界。对应真实写稿和联合留出分别见 [`ul006-incident-only-r1/result.md`](ul006-incident-only-r1/result.md)、[`post-v1621-validated-atoms-r1/result.md`](post-v1621-validated-atoms-r1/result.md)、[`wr021-application-reason-r1/result.md`](wr021-application-reason-r1/result.md) 与 [`wr024-request-reason-r1/r3-result.md`](wr024-request-reason-r1/r3-result.md)。
- 公开 README 和平台回执仍只陈述已发布的 1.6.21。付费提纲、Pro Hook、红头 DOCX 继续留在独立边界；本轮冷审发现的 under-length 契约漂移、终止路径清理和 Stop 超时预算另建下一版本候选，不混入本基线。

## 本次工程门

- `git merge-base --is-ancestor v1.6.21 HEAD`：通过；固定上一 tag 是候选祖先。
- 聚焦回归：`python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_hook_layer_contract maintenance.tests.test_status_ledger_consistency`，99/99 通过。
- 产品坐标提交上的一次全量回归：`python -m unittest discover -s maintenance/tests -p "test_*.py"`，746/746 通过，耗时 116.615 秒。其后只增加本记录、状态登记和对应状态测试，不改产品字节；不重复运行全量冒充新的产品验证。
- 固定 `v1.6.21` 与 current 的确定性真实用户式 Prompt 消融均为 111/111，通过数、起草失败和改稿失败分别为 111、0、0；该门不调用 LLM。
- `OFFICIAL_WRITING_EVAL_STUB=1` 的 Promptfoo smoke 为 20/20，Skill 10 胜、baseline 0 胜、平票 0、无效 0、需人工复核 0，judge consistency 为 1.0；该门不调用真实写稿模型。
- canonical、Agent Skills、QwenWork、Qwen Code、Hermes 五套 `quick_validate.py` 均通过；166 个 tracked Python 文件完成内存编译，163 个 tracked JSON 文件解析通过。
- `sync_adapters.py` 复跑后 tracked diff 为空；`assemble_hook_companion.py --help` 正常列出九个宿主和六项能力；`git diff --check` 通过。

## 本地包预检

- SkillHub.cn 清洁包为 82 文件，规范化文件树 fingerprint 为 `6b97bb1ef28789360004b1a580ee724fef2c97f4758ebd2a9bf141a378457ed2`；slug 为 `chinese-official-writing`、展示名为“中文公文写作”、版本为 `1.6.22`，含 `LICENSE.md`，排除根 `LICENSE` 与 `agents/openai.yaml`。
- ClawHub 发行目录为 33 文件，规范化文件树 fingerprint 为 `0ce2f2e2b3929d65e9970b73d0c31d67f69ce36e09dedc59538cf434db754427`；目录继续使用 `chinese_official_writing`，元数据版本为 `1.6.22`。Hook 路径、Hook 内容、`agents/openai.yaml`、付费提纲和红头实现命中均为 0。
- 两类包只在忽略的本地输出目录预检，没有 dry-run 或正式平台写入。平台 slug、展示名、owner 和分类等公开坐标未被本轮改动。

## 剩余边界

- `1.6.22` 当前是已完成工程门的本地主线登记，不是已发布版本；若后续需要公开发布，仍须另行固定最终 main、创建 tag 并按三个平台各自包面重新执行发布前核对。
- under-length README/host capability 与运行时事故入口存在声明漂移；历史情况说明和通知隐式入口还留有不可达常量/指导语；异常 Stop 中多个子进程各自最多 20 秒，静态最坏值可能超过宿主 30 秒。上述问题不推翻 1.6.22 已验证写稿增量，但必须在独立下一版本候选中原子修复和验证。

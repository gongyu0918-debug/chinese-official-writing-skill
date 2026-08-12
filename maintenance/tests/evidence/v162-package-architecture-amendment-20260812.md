# v1.6.2 插件、Hook 开关与可达性修订预注册

## 修订原因

在 `727a14df` 固定的首轮结构候选完成后，用户进一步明确：三套 Codex、WorkBuddy/CodeBuddy、Claude Code companion 的职责是适配可选 Hook，应归入 canonical 的 `hooks/`；仓库还必须检查孤儿脚本、孤儿 Markdown 和孤儿叶子，并保证用户关闭 Hook 或宿主不支持 Hook 时，普通 Skill 仍能像 v1.6.1 一样独立闭环。

只读复现还发现一个确定性缺口：已启用插件收到“请关闭 Hook”或“本次不要用 hooks”后，当前 core 仍会保存请求、在读到 Skill 后建立 transaction，并在 Stop 阶段返回 block。现有纯审稿旁路不能覆盖用户显式关闭。

## 新的候选边界

1. 三套自包含插件根从 `plugins/<host>/` 移至 `hooks/plugins/<host>/`。每个宿主目录仍是直接交给宿主安装或 `--plugin-dir` 的根，manifest、`skills/`、`hooks/` 和适配脚本不得跨出自身根。
2. `hooks/README.md` 说明插件属于 Hook companion，并写清目标收益、耗时、启用方式、逐任务旁路、D0 回退、未验证项和当前没有自动补字。
3. 用户在本轮首个请求中明确写出“关闭/禁用/停用 Hook”“本次不使用 hooks”或“不启用交付门禁”时，core 记录 `bypass=user_requested`，不建立 transaction、不调用 review gate、不阻断 Stop、不替换原稿。
4. “不要关闭 Hook”“继续使用 Hook”“不要用脚本”“不要过度复核”等不得触发旁路。事务已经建立后不做静默关闭；仍按有限状态回退 D0，避免丢失已保存原稿。
5. 普通 Skill 安装、宿主不支持 Hook、插件未启用和用户显式旁路四种情况，都必须保留 `SKILL.md -> references -> 可选 prose_lint -> 正文交付` 的无 Hook 闭环。
6. 新增确定性可达性门：29 个 reference 必须由普通 Skill 或 Hook 专用入口接引；产品脚本、Hook 叶子、宿主 manifest、事件配置、适配器和插件内 Skill 必须有上游；`maintenance/` 与 `packages/` 必须有索引，新增维护脚本或评测入口未登记即失败。

## Hook 适用性口径

- 启用目标：通过一次额外、有限的交付复核，提高已覆盖的事实、状态和结构错误被发现并安全回退的机会。
- 成本：增加 Hook 事件、Stop 阶段和生成时延。
- 不得宣称：所有文体稳定变好、全面事实核验、篇幅兜底、自动补字或替代人工审稿。既有真实 A/B 未证明普遍质量收益，D1 有效交付仍不足。
- 技术矩阵：三宿主 × 普通起草/改写/只审不改 × 短中长输出，覆盖插件未启、插件启用、启用后用户旁路。逐格检查 transaction、Stop block、D0/D1、终稿哈希、协议泄漏和额外步骤；本轮先完成不调用模型的确定性生命周期矩阵，真实写稿另以冻结题面和独立盲审执行。

## SkillHub 分类审计

只读核验当前公开 API 的 `category=professional`、子类为“政务服务”。v1.6.1 上传包没有 `categories` 字段；当前 SkillHub CLI 发布 payload 也不发送分类，只发送名称、摘要、描述、tags、license、homepage 和 changelog。因此本轮记录期望分类为“效率提升/内容创作”，但不伪造 CLI 不支持的字段，也不进行平台写操作。线上分类若需调整，必须使用平台管理入口或客服后台能力另行处理。

## 验收与停止条件

1. 三套插件在 `hooks/plugins/<host>/` 自包含，包内无 `../`，官方/本地 validator 与三事件子进程 smoke 通过。
2. 显式旁路在三宿主均为 allow、零 transaction、零 Stop block、零 D0/D1 替换；负向控制不误旁路。
3. 无 Hook 的 canonical 与四套纯 Skill 镜像可运行 `prose_lint.py` 并直接交付，运行上下文不含 Hook 协议。
4. 可达性门、聚焦测试、全量 unittest、Promptfoo stub、quick validate、py_compile、sync 二次幂等、SkillHub 清洁构建和固定 v1.6.1 确定性消融通过。
5. 若旁路误匹配、插件越界、普通闭环依赖 Hook、出现孤儿产品文件或写作规则相对固定产品基线发生非条件接引变化，停止合入。
6. 本轮仍不合入历史篇幅 Hook，不发布、不推送、不移动 tag、不修改 SkillHub 分类。

# 保护性否定句尾 lint 原子验证结果

日期：2026-08-03。

## 结论

PASS。该原子可以合并：平台最小包中的 `prose_lint.py` 新增三类 `draft-body` 专用中等级提示，成稿后复核规则对每个命中执行一次“保留、进行态改写、删除”语义选择。脚本不自动改稿，不按单个否定词判错，也不形成循环。

## 基线与修改

- 研究底座：`96d689582aaebcc55feac1a9204d7a8439041db4`。
- 固定发行基线：`v1.5.33=1ea3f5b6ccccd5ef772803e264087adcf2fb5515`。
- `prose_lint.py`：新增 `protective-negative-inference`、`unresolved-conclusion-tail`、`negative-boundary-tail`；仅在 `delivery_mode="draft-body"` 启用，严重度均为 `medium`。
- 局部正则窗口使用具名常量；阶段模式在 `prepare_pattern_sets()` 中一次组装，没有新增万能字典或上帝函数。
- `final-review-layers.md`：命中后只处理命中句及必要衔接；材料明示且文种需要的边界保留，本单位核心未决事项改为进行态，外围保护性解释删除；只复扫一次，保留项不循环。
- 全标签接引审计：82 条静态模式和 10 类动态结构提示均自带 `advice` 或 `excerpt`；总审增加一条通用消费动作，高、中风险逐条选择保留、局部改写或删除，低风险只在有明确质量收益时处理。

## 定向检测

- 冻结及补充正例：11/11 命中预期标签，包括“不能证明”“不能形成结论”“尚未形成决定/安排”“不直接等同于”和事实后“不构成”等完整结构。
- 明确豁免：8/8 不命中新标签，包括“尚在办理”“正在调查”“未发现数据丢失”“不得迟报”“待确认”和独立法律判断。
- clean corpus：12/12 未新增三类 `medium` 提示。
- 阶段隔离：同一句在 `generic`、`review-only`、`gap-note-allowed` 均不触发，只在 `draft-body` 触发。
- CLI 只读：`--strict --fail-on medium` 能返回风险退出码，扫描前后原稿字节一致。

## 脚本到语义层短链路

独立只读验证使用三组既有风险形态，没有生成长稿：

| 场景 | 初扫 | 选择 | 结果 | 复扫 |
| --- | --- | --- | --- | --- |
| 材料只确认系统于10:20恢复，初稿追加“不足以证明始终正常” | `protective-negative-inference` | 删除 | 只保留恢复事实 | 0 命中 |
| 材料确认调查已启动并分析日志，初稿写“尚未形成正式结论” | `unresolved-conclusion-tail` | 进行态改写 | 改为原因正在调查、正在分析日志 | 0 命中 |
| 材料逐字载明法律顾问意见“事实已经查明，但不构成合同违约” | `negative-boundary-tail` | 保留 | 来源、事实状态和法律结论不变 | 仍命中；按已判定保留项停止，不循环 |

三类脚本结果均获得了明确语义响应；数字、日期、主体、责任和状态没有升级。

## 独立代码审查

独立 reviewer 首轮发现 `unresolved-conclusion-tail` 漏掉预注册中的“安排”，且没有把该标签限制在句尾。实现已补入“安排”和句末锚定，并增加一正一反回归：

- `会议尚未形成具体安排。` 应命中；
- `会议尚未形成决定，下一步继续研究。` 不按句尾收束命中。

定向测试 7/7 通过，reviewer 复核结论为 `CLOSED`。其余可维护性、阶段隔离、复核有界性和平台包边界无发现。

## 工程验证

- `python -m unittest discover -s tests`：440 项通过。
- `npm run eval:official-writing:smoke`：20/20 通过；10 个 skill 对照均通过，judge consistency 100%。
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.33 detached worktree> --baseline-label v1.5.33 --current-root . --out output/protective-negative-tail-lint-v1533-r1-ablation-handoff-final`：current 111/111；固定 `v1.5.33` 110/111，基线唯一失败为标签后新增的 P098 调用链覆盖，不是本候选回退。
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：`Skill is valid!`。
- canonical 与五份发行镜像的 `prose_lint.py` 只有一个 SHA-256：`B752C2A2D0B44B523A8F2072DED58ABA9074AA5472DC9E727264A342BDC6F8AF`。
- canonical 与五份发行镜像的 `final-review-layers.md` 只有一个 SHA-256：`73737D1E6E78E832EAF635D1F4FA8E38714FA104D7EE7E61AD0C8073C0FE3D20`。
- OpenClaw 最小包实际包含 `scripts/prose_lint.py`，继续排除 Codex 专用 gate runtime；新提示不依赖 `review_gate.py`。
- `git diff --check`：通过。

## 剩余边界

- 正则只定位完整高置信结构，不能判断一句话是否由原材料明确支持；最终保留、改写或删除仍由 Agent 对照材料和文种语义决定。
- 为控制误报，独立的“未、不能、不构成”及主语插入较多的变体不会全部命中；这些仍由既有总审规则覆盖，不扩成宽词表。
- 本轮证明了脚本命中后的三路处理能够闭合，没有证明所有宿主都会自然调用脚本；支持脚本的宿主可直接使用平台包内的 `prose_lint.py`，不支持时仍依赖成稿后语义复核。

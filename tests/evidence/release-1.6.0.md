# 1.6.0 发布证据

## 当前状态

1.6.0 已完成产品组合真实复放和最终人工语义裁决，正在执行发布前工程门与三平台发布。固定上一发行版为 `v1.5.41`；小红书 Red SkillHub 不在本次授权范围内。

## 本轮产品改动

相对 1.5.41，本版包含以下已进入本地 `main` 或通过组合复放的运行时改动：

1. 删除入口中边界已经明确的“闲聊回复、通用翻译”排除示例，并把七个未完成占位示例下沉到办理要素与终稿复核叶；入口仍保留不得残留未完成占位、日期、主送和签发要素边界。
2. 短单项采购申请使用一至两个自然段承载品名规格、数量和金额；多品类、分项核算、比价验收、技术附件和明确长篇任务转入完整办理链，字段表格保持原结构。
3. 信息选择规则明确总量与子项差额只用于合计校核，不把未说明的差额自行归入某一类别。
4. anti-AI 空泛套话列表删除同叶已有多处承载的 `持续推进` 重复示例，保留资格和处理机制。
5. 入口交付范围改为正向、自然的成品边界表达；通用 playbook 删除不属于其实际加载范围的报告块；五个文种叶删除与入口同载的模板优先重复句；Hook 删除重复的“未决转进行态不算新增动作”预放行。

相对 1.5.41 的 canonical 运行时产品共改动 12 个文件，新增 9 行、删除 24 行；版本同步不计入该统计。

## 真实写稿与组合裁决

- 四原子组合固定 Baseline `b91f25cc49cc8ca1379804a81a1d6e5a4eab987c`，Candidate 产品冻结 `23a89114`。
- Alibaba Token Plan 与 Ollama Cloud 的 DeepSeek V4 Flash 0731 均使用 `max`；W1—W3 写稿与 H1—H2 Hook 共 10 对，10/10 技术有效，20 份首个 final，零模型重试。
- projectless SOL `max` 在 mapping 解盲前完成匿名裁决。解盲后 Candidate 8 胜、Baseline 0 胜、2 难分。
- 严格机械停止记录、原始 SOL 裁决和产品所有者最终语义裁决分别保留在：
  - `release-1.6.0-combination-real-result-20260811.md`；
  - `release-1.6.0-combination-real/sol-blind-review.md`；
  - `release-1.6.0-combination-final-adjudication-20260811.md`。
- `原因尚未查明`、同事项的“正在核查”或在短稿中省去原因状态，按本轮产品语义均可接受；该口径不外推到责任、采购决定、期限和整改安排。附件字段位置与独立列示差异继续作为格式风险监测，不为单次样本恢复重复规则。

## 本版明确不包含

- 不包含 delivery-mode 的 `draft-body / gap-note-allowed` 路由候选。
- 不包含 review_gate 肯否关系与未决强度机械保护候选。
- 不包含 official-style 评价强度规则删除候选。
- 不包含尚未完成真实验证的政治人物讲话联网核验、短通知紧凑形态和其他隔离研究分支。

## 发布前验证

| 验证 | 实际结果 |
| --- | --- |
| `python -B -m unittest discover -s tests -p "test_*.py"` | 475/475，通过 |
| `OFFICIAL_WRITING_EVAL_STUB=1` 的 smoke | 20/20，通过；0 failed、0 errors；eval id `eval-YYX-2026-08-11T03:11:32` |
| 固定 v1.5.41 确定性消融 | v1.5.41 为 110/111；current 为 111/111；唯一差项是旧版没有本轮新增语义锚 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -B -m py_compile ...` | `prose_lint.py`、`review_gate.py`、`sync_adapters.py`、`deterministic_capture.py` 通过 |
| 镜像同步与 diff | `sync_adapters.py` 重跑前后 diff object hash 均为空对象 `e69de29b...`；六份运行包版本同步；`git diff --check` 通过 |

版本准备提交为 `fbbe3ec7c84ca7cddcad0321d72c707ad5951248`。确定性消融和 Promptfoo stub 只作为工程门，不替代上述真实写稿与独立裁决。最终发布提交、annotated tag、发行包 fingerprint 和三平台回执在上传完成后以单独维护提交补入，不移动发布 tag。

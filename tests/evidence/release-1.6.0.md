# 1.6.0 发布证据

## 当前状态

1.6.0 已完成产品组合真实复放、最终人工语义裁决、发布前工程门，以及 GitHub、ClawHub、skillhub.cn 各一次正式提交。GitHub `main`、annotated tag `v1.6.0` 和正式 Release 的产品提交均为 `0f6ec603993d5595e784fa7079837e299d1b0da3`；本回执提交继续推进 `main`，不移动发布 tag。ClawHub 与 skillhub.cn 的公开正文索引仍显示 1.5.41，属于正式回执后的异步传播，不重复发布。固定上一发行版为 `v1.5.41`；小红书 Red SkillHub 未调用。

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

版本准备提交为 `fbbe3ec7c84ca7cddcad0321d72c707ad5951248`。确定性消融和 Promptfoo stub 只作为工程门，不替代上述真实写稿与独立裁决。下列发布提交、annotated tag、发行包 fingerprint 和三平台回执由发布后维护提交补入，发布 tag 保持不动。

## 发布提交与 tag

- 产品发布提交：`0f6ec603993d5595e784fa7079837e299d1b0da3`。
- 远端 `main`：`0f6ec603993d5595e784fa7079837e299d1b0da3`。
- annotated tag object：`231b1cb8ef5fb50ce4dbca4a7d252088c097eb34`。
- `v1.6.0^{}` 解引用提交：`0f6ec603993d5595e784fa7079837e299d1b0da3`。
- 上一发行 tag `v1.5.41^{}`：`b2bc25da6b31fb6d6057affc02e3e7b72d18d26c`，为本次发布提交祖先。

## 发行包与平台回执

### ClawHub

- 发行目录：`openclaw/skills/chinese_official_writing/`；32 个文件，禁入门禁文件、缓存和 `.pyc` 为 0。
- dry-run：`ok=true`、`status=would-publish`、版本 1.6.0、32 个文件、fingerprint `5cbf26d2dd451a4212afcd81a57fe4488dd65e0fa0921bb7457236c58e6e04ba`。
- 正式提交：`ok=true`、`status=published`、版本 1.6.0、32 个文件、versionId `k977r9dggxa1rmcdxgtmjfvf0d8c8fcr`、fingerprint `ec6a7015c776e3786f14f3d9402a0410a55709f377e42807ad15bd95a6ae5e69`。
- dry-run 使用 release worktree，正式提交使用同一 Git commit 的根 `main`。两目录 32 个文件中仅 `agents/openai.yaml` 的原始 CRLF/LF 字节不同；Git blob 与规范化内容相同，导致平台 raw-byte fingerprint 不同。正式提交已被接受，不重复上传。
- 首次公开回读：精确 1.6.0 返回 `Version not found`；默认详情仍显示 `latestVersion=1.5.41`，当前 `clean` 扫描也对应 1.5.41，不能写成 1.6.0 已完成传播或扫描。

### skillhub.cn

- 首个本地包因 SkillHub frontmatter 的 `homepage` 与 `name` 少一个换行而作废，未进入 dry-run 或正式提交；作废包保留，不计发行包。
- 有效清洁包：`output/skillhub-release-1.6.0-20260811T0322/publish-package/`；31 个文件，缺失 0、禁入 0；Skill 正文与 canonical 完全一致。
- 内容清单 SHA-256：`2A1D4AB0B2B85825CED330EAC28D948A4FCA3AB0556E26CEAE4D0426AC703261`。算法为相对 POSIX 路径排序，每行 `path<TAB>SHA256(file)`，UTF-8、LF、末尾一个 LF。
- shell 包装器 `skillhub` 启动后 60 秒无输出，已终止且无平台状态变化；随后直接使用同一安装目录的 `skills_store_cli.py` 2026.8.5。
- dry-run：`dryRun=true`、slug `chinese-official-writing`、version `1.6.0`。
- 正式提交：`ok=true`、skillId `70149`、versionId `229000`、31 个文件、fingerprint `f45b3fa4fcce2bd286c4111cab5ca0d630daaac81c3ecfbb698fa8b83dec25cc`、`tags.latest=1.6.0`；review、security scan 与 content audit 均为 `pending`。
- 首次公开 API 回读：`tags.latest=1.6.0`，但 `latestVersion.version=1.5.41`；公开安全报告仍对应旧内容，不能推断 1.6.0 已完成审核或扫描。

### GitHub

- 正式 Release：非草稿、非 prerelease，`publishedAt=2026-08-11T03:21:04Z`。
- `targetCommitish=main`；产品事实以 tag 解引用提交 `0f6ec603993d5595e784fa7079837e299d1b0da3` 为准。
- 地址：`https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.0`。

平台正式回执取得后，即使公开 latest、审核或扫描异步滞后，也不重复提交。

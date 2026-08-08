# 1.5.39 发布证据

## 当前状态

1.5.39 已完成版本面同步、精简可复验证据包、发布前工程门和两家商店 dry-run。本文件首次提交时尚未推送产品提交、创建 `v1.5.39` tag、GitHub Release 或向 ClawHub、skillhub.cn 发起正式提交；实际发布提交与平台回执在动作完成后补写，不能由 dry-run 推断。

## 本轮改动

- 自然化“只要正文/改后稿、不解释、限定文后提示”等输出范围表达，保留原交付边界。
- Word、docx、GB/T 9704 的字体字号细则下沉至 `format-gbt9704.md`，入口只保留按需读取和 DOCX/document 交接；发布前真实复验发现正文对齐方式 3/3 缺失后，在格式 reference 最小补入“一般两端对齐”，修复后 2/2 通过。
- 删除“出现单位名称不触发搜索单位样文”的入口冗余句，默认不联网和明确核验路由继续由统一规则承载。
- 终稿正文检查增加 `final-review-layers.md -> draft-body` 自然选择指针；脚本仍只提示、不自动改稿。
- 统一起草、改稿、复核（默认只审不改）、排版交付模式词，并明确起草、改稿、压缩或合稿先读取 `information-selection.md`，再判断轻量卡。
- canonical、Codex、Claude Code、Qwen、Hermes、OpenClaw 镜像及展示元数据统一到 1.5.39。

本版不改变文种路由条件、事实边界、篇幅规则、复核顺序、修订次数、回退方式、Hook 或发布链。

## 基线与提交

- 固定 1.5.38 产品基线：`c3fa2128ef9426b4ebb135986a7e19feccf08421`（annotated tag `v1.5.38` 解引用提交）。
- 五原子归并：`77988f51`；成本与质量记录：`d9b7cefc`。
- Word 对齐修复预注册：`68fc4e01`。
- 1.5.39 最终产品提交、tag object 和 tag 解引用提交在正式发布后补写。

## 发布前验证（2026-08-08 实跑）

| 验证 | 实际结果 |
| --- | --- |
| `python -m unittest discover -s tests` | 442/442，通过 |
| `npm run eval:official-writing:smoke`（`OFFICIAL_WRITING_EVAL_STUB=1`） | 20/20，通过；0 failed、0 errors |
| 固定 1.5.38 确定性消融 | v1.5.38 111/111；current 111/111 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -m py_compile ...` | `prose_lint.py`、`review_gate.py`、`sync_adapters.py` 通过 |
| `python tools/sync_adapters.py` | 重复执行后 0 语义漂移 |
| `git diff --check` | 通过 |

Promptfoo 使用本地 stub，只证明评测入口和结构未回退，不作为真实写作质量证据。

## 真实写稿与独立裁决

此前五原子单项和归并证据仍保留。本次发布前另建立一份自包含精简包，覆盖稀疏正文、Word 版式和只审不改 lint 三题：

- R1：固定 1.5.38 为 PASS，Candidate 原始首稿因漏标题为 WARN；Candidate 两次逐字复放均保留标题，累计 1/3，未升级为共性回退。
- R2：固定 1.5.38 为 PASS，Candidate 原始首稿为 WARN；Candidate 逐字复放达到 3/3 漏“两端对齐”，触发格式 reference 最小修复；修复后两名新 writer 为 2/2 PASS。
- R3：两臂均为 WARN，Candidate 排在固定基线之前；两臂均只审不改、未联网，合法否定句均未误报。

综合判定：`PASS / RELEASE-READY AFTER REPAIR`。完整原稿、映射、writer id、实际读取路径和命令见 `v1539-compact-repro-pack-20260808.md`；对齐修复结果见 `v1539-format-alignment-repair-result-20260808.md`。

## 发行包

### ClawHub

- 发行目录：`openclaw/skills/chinese_official_writing/`；
- 文件数：32；
- dry-run：`status=would-publish`，公开基线 1.5.38，目标版本 1.5.39；
- fingerprint：`a90a449c3702ab3b6a57a0ed553c46af49ffee7c0ece2cd092165226fa5b95b8`。

### skillhub.cn

- 清洁包：`output/skillhub-release-1.5.39-20260808/publish-package/`；
- 文件数：31，禁入文件 0，共享内容哈希不一致 0；
- 排除 `agents/openai.yaml`、`delivery-review-gate.md`、`gate_stop_hook.py`、`review_gate.py`，加入平台 `_meta.json` 和 SkillHub 专用 frontmatter；
- `SKILL.md` 正文与 canonical 逐字一致；
- 内容清单 SHA-256：`86a67e19a9c1416c096fbc8c086f5d3671a9bb591a189eb211c60a06c0cd411a`。算法为：相对路径按序排列，每行 `relative_path<TAB>file_sha256`，UTF-8、LF、末尾保留 LF 后取 SHA-256；
- dry-run：精确返回 `chinese-official-writing@1.5.39`。

## 剩余风险

1. 本轮自包含真实 A/B 为三题；能够核验五原子的直接交互和修复闭环，不能据此宣称所有文种、模型或 Word 文件的统计性提升。
2. R1 Candidate 首稿出现一次标题遗漏，两次定向复放未再现；该负例继续保留观察。
3. R3 两臂均为 WARN，主要是联系方式、日期和正式发文缺项的风险粒度不同；合法否定句、只审不改和不联网边界均通过。
4. writer 回执未暴露可独立核验的具体模型标识，故本轮精简包模型字段为 `unavailable`。
5. R2 用普通文本展示版式清单，没有生成或渲染 DOCX；本轮只证明格式 reference 的要素承载和正文事实边界，不能替代真实 OOXML/逐页视觉验收。

## 发布边界

GitHub、ClawHub、skillhub.cn 在收到正式提交回执前均记为未发布。平台一旦返回 accepted、published、pending 或其他提交回执，不因公开 latest、审核、扫描或索引传播延迟重复提交。小红书 Red SkillHub 不在范围内，不调用其 CLI。

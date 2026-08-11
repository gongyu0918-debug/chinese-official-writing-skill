# 入口减负原子组合验证结果

日期：2026-08-01

固定发布产品基线：`v1.5.31=e8c077cb1d6c6fe02bec71634140793aeeba5a5b`

集成起点：`main=2a52613790f466e6a999280cc8697ec3bb8aab21`，技能产品文件与固定发布提交一致

隔离分支：`codex/entry-relief-integration-v1531`

## 集成范围

按下列顺序只摘取三个已经分别验证的产品提交，不带入各研究分支的预注册、原稿或运行产物：

1. `a9460ff034d660fa03dcf00217fdfd58e7133553`：将入口“三层使用原则”改为使用顺序导航，把两项独有承重语义迁入 `information-selection.md`。
2. `5f0c920c50c56e03ea16199b38ec6286d0f42a52`：从非适用任务列举中删除“模型训练”；AI 算力专项叶中的正常业务字段继续保留。
3. `e4d15c5668e58e255edcabb5caabda9cae30f9e7`：删除 `workflow.md` 内与入口重复的联网搜索条件指针。

前两项在 `SKILL.md` 相邻区域修改，但语义互补；第三项只改 `workflow.md`。摘取第二项时仅 `tests/test_skill_boundary.py` 发生同位置断言冲突，人工保留了两组互补断言；产品文件自动合并，没有语义冲突。

## 字符减载

统一将换行规范化为 LF 后，canonical 文件相对固定 1.5.31 的字符变化为：

| 文件 | 基线 | 集成后 | 变化 |
| --- | ---: | ---: | ---: |
| `SKILL.md` | 11286 | 10805 | -481 |
| `information-selection.md` | 454 | 559 | +105 |
| `workflow.md` | 6077 | 5984 | -93 |

- 每次触发必读的入口减少 481 字符。
- 起草常用的 `SKILL.md + information-selection.md` 净减 376 字符。
- 同时读取 `workflow.md` 的完整路径净减 469 字符。

本组合不改变任务路由、reference 加载条件、文种规则、输出模式、复核顺序、脚本、FSM、版本号或发布链。

## 实际验证

- `python -m unittest discover -s tests`：395/395 通过，用时 17.451 秒。
- `npm run eval:official-writing:smoke`：20/20 通过，0 failed、0 error、judge consistency 1.0。
- `python tools/run_real_prompt_ablation.py --baseline-root ...news-commentary-v1531-e8c077cb --baseline-label v1.5.31-e8c077cb --current-root . --out output/entry-relief-integration-ablation-20260801`：固定基线 110/110，集成候选 110/110。
- `python C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing`：通过。
- `python tools/sync_adapters.py --help`：脚本不解析 `--help`，实际执行了一次同步；同步后重新暂存核验，没有形成实质 diff。
- 逐文件 SHA-256：`skills/`、`.agents/`、`.qwen/` 三个通用镜像各 29 文件，与 canonical 0 missing、0 extra、0 changed。Hermes 仅保留预期的专用 frontmatter 差异；OpenClaw 仅保留专用 frontmatter、README 和既有发行边界差异，均由同步脚本生成。
- `git diff --check main...HEAD`：通过。

确定性消融不调用 LLM，只证明包、路由、检查入口与既有用例未回退。三个原子此前已分别完成与其变量相称的真实运行核验；本组合没有新增语义规则，因而不再以语言随机胜负追加阻断性 A/B。

## 交互风险与结论

未发现组合后丢失事实边界、AI 算力专项字段或公开来源路由。`information-selection.md` 增加的两项承重语义抵消了入口长段删除可能造成的边界缺失；联网核验仍由入口直接指向 `external-research.md`，不依赖已删除的 workflow 重复指针。

结论：`PASS / MERGEABLE`。本分支只具备进入主线合并评审的资格，未合并 `main`、未改版本号、未发布。

维护观察：`tools/sync_adapters.py` 当前忽略未知参数并直接执行同步；本轮没有修改该脚本，后续可单独补 `--check` 或显式参数解析，不能与本次 Prompt 减负混合归因。

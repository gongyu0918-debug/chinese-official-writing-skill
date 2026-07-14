# 中文公文写作 1.5.13 发布证据

## 发行范围

- 上一发行基线为 annotated tag `v1.5.12`，解引用提交 `f87b6be990e1314442b5532ae7441f21c8d4d34f`。
- 1.5.13 纳入 `62ea0fa` 的两处“缺项说明放正文外”减负，以及 `8495599` 的否定式反例正向事实锚定修复；许可与 README 的后续修正提交一并进入 GitHub 主线历史。
- 产品改动只涉及 `SKILL.md`、`references/workflow.md`、`references/official-style.md` 的句级约束和对应镜像、测试、证据；任务路由、reference 加载条件、三级复核顺序、输出模式、修改次数、默认联网和发布链未改变。
- 小红书 Red SkillHub 明确排除；未同步 `redskill/`，不调用 Red CLI、dry-run、登录或上传。

## 真实写稿与冷审

- 固定 `62ea0fa` 基线的两名 writer 在 4 个真实阶段报告 prompt 中有 6 份输出出现保护性边界自证；两名候选 writer 的 8 份分稿均为 0，且现场复核后定结论、7 月 15 日核验、7 月 25 日统一验收和 8 月评审议程等必要状态全部保留。
- 两名 writer、两名 verifier 的本地 `turn_context.model` 均核验为 `gpt-5.6-sol`，未使用 MiniMax。原 prompt、匿名稿、映射、模型 ID、两份 verifier 报告和派生统计补测见 `tests/evidence/negation-rule-dedup-20260714.md` 及同名 writing 目录。
- 一名候选 writer 出现跨异常类型计算总体恢复率和覆盖人数折算人均事项量的 WARN；另一名候选 writer及随后同题基线/候选补测均未复现，不满足共性或候选独有回退门槛，未为此新增规则。
- 独立 diff 冷审未发现 P0/P1/P2，确认核心工作流和配置未漂移，`publish_blocking=false`。

## 发布前验证

- `python -B -m unittest discover -s tests -v`：152/152 OK。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.12-for-1.5.13 --baseline-label baseline-1.5.12 --current-root . --out output\release-1.5.13\real-prompt-vs-1.5.12`：baseline 104/108，current 108/108；baseline 只在 P036、P039、P046、P094 的本版新增守卫失败。
- `npm run eval:official-writing:smoke`：20/20 PASS，skill 10 胜，judge consistency 1.0。一次执行申请因审批超时未启动，重试后实际运行通过；未把未启动的尝试写成测试通过。
- `python -B tools/run_real_article_eval.py --out output\release-1.5.13\real-article`：skill 10 个样本缺失要素 0/61、关键词命中率 100%，格式风险、重复事项和反 AI 风险均为 0；9 个匿名占位标签样本仍只作人工线索。
- 完整数据集 27 批最大上下文 `24502`，低于仓库 `<25000` 门槛；canonical quick validate、镜像一致性和 `git diff --check` 通过。

## 发行包预检

- ClawHub 发行目录为 19 个文件，违规缓存、finalizer、detector、repair 文件为 0；`SKILL.md` 版本为 1.5.13，包内许可继续为 MIT-0。
- skillhub.cn 临时包为 19 个文件，违规文件为 0；17 个共享文件与 canonical 逐文件 SHA-256 一致，平台专用 `SKILL.md` 正文与 canonical 正文一致，版本为 1.5.13，dry-run 返回精确 slug `chinese-official-writing`。
- GitHub 仓库许可继续为 MIT；ClawHub 和 skillhub.cn 包继续维持 MIT-0，不追溯改写历史版本。

## 发布状态

- GitHub：待发布。
- ClawHub：待发布。
- skillhub.cn：待发布。

## 剩余风险与停止条件

- 真实写稿样本不能证明所有弱模型、3000 字以上长文、多附件或 compact 后稳定性；本版不扩大相关能力承诺。
- 任一平台正式提交成功后若客户端报错，先只读 inspect，不重复提交；公开索引延迟、moderation 或审核 pending 与提交失败分开记录。
- 任一旧硬边界回退、目标改善丢失、上下文达到或超过 25000、发行包或镜像不一致，停止发布并回退对应提交。

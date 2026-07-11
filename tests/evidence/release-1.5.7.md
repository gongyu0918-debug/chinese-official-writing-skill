# 1.5.7 窄修复发布记录

日期：2026-07-11

## 固定状态与发布范围

- 上一发行版：`v1.5.6` / `7e485700a49a924abf973656d2bb0e9630054890`。
- 干净发布分支：`codex/release-1.5.7`，从 `afc85dcfecb80d294f12ca8e92d8fa28ce756c3e` 创建；候选在版本同步前为 `356a44d8d7f9b7b08e2dd643e713edada4d70c02`。
- 发布修复来自 `8a0144d1f359e3f77e1c1618f87a06b79e5d7f4d`：删除容易诱发材料旁白的“从已给材料看，问题集中于……”，改为直接列明已确认问题的对象、数量和状态；无法支持的结论仍放正文外待确认。
- 保留 `afc85dc` 和 `356a44d` 的只读实验结论记录；`55edc71`、`5f2a214` 等误跟踪实验输出不是发布分支祖先，`output/` 也未被跟踪。
- 版本同步只修改 canonical、适配器入口、插件和市场元数据。未加入 finalizer、detector、repair、embedding、外部依赖、自动清洗、二次修改候选 prompt 或新写稿工作流。
- ClawHub 发行目录 `openclaw/skills/chinese_official_writing` 为 19 个文件，无 `.pyc`、`__pycache__`、finalizer、detector 或 repair；SkillHub 临时包 `output/skillhub-release-1.5.7/publish-package` 也是 19 个文件，并显式排除 canonical 工作目录下的 ignored Python 缓存。

## 发布前验证

- `python -B tools\sync_adapters.py`：通过。
- canonical `SKILL.md` 与 Codex/Qwen/shared 镜像 SHA-256 一致；5 组 `references/` 镜像逐文件比较为 0 mismatch。Hermes 和 OpenClaw 入口保留其平台 frontmatter 差异。
- `python -B -m unittest tests.test_revision_instruction_eval tests.test_skill_boundary tests.test_review_regressions tests.test_real_prompt_ablation tests.test_promptfoo_eval -v`：123/123 通过。
- `python -B -m unittest discover -s tests -v`：123/123 通过。
- `python -B tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.6 --baseline-label release-1.5.6 --current-root . --out output\release-1.5.7\deterministic-vs-1.5.6`：`release-1.5.6 101/102`，`current 102/102`；唯一差异为 P046 对直接列明问题对象、数量和状态的新增守卫。
- `python -B tools\run_real_article_eval.py --out output\release-1.5.7\real-article`：skill 路径 10 个样本关键要素 61/61，关键词命中率 100%，格式、重复和反 AI 风险均为 0；9 个匿名占位标签风险样本仍只作人工复核线索。
- `python evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：沙箱外发布级 provider 20/20 通过，skill 10 胜，judge consistency 1.0。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：通过，仅有 Windows 行尾转换提示。

## 真实 subagent sanity

4 个独立 `gpt-5.6-luna` writer 分别加载当前 1.5.7 skill，不读取评分结论：

- 问题清单型报告：`019f50bc-99b7-7ef0-bde6-de0fb0963eb3`。6 条记录、2 条标签不一致、1 条待复核均保留，无材料读取旁白或未给责任/原因/整改结论；篇幅明显低于约 500 字。
- 只输出正文通知：`019f50bc-adec-7b73-94df-7dfe1fa83fd6`。日期、范围和检查重点保留，无待确认、自证或未给联系人/发文单位。
- 字段式采购材料：`019f50bc-c20a-77b1-a41e-bdca1d0eb661`。字段名、顺序和值逐项保持，两个空字段仍为空，无新增字段或事实。
- 只审不改：`019f50bc-d60c-7d81-bb4c-73c188bed925`。只给位置、风险层级和修改建议，没有重写、评分或 Markdown 加粗包装。

独立 GPT-5.5 verifier `019f50bd-e5f1-7173-b8a2-8d5e6f844107` 判定 3 PASS、1 WARN、`publish_blocking=false`。WARN 为问题清单稿篇幅不足，且“除上述情况外，本次抽查未形成其他可确认事项”略接近无法支持的边界性概括；未发现旁白、事实编造、字段/情态漂移或其他严重功能回退。按窄发布约束，本轮只记录，不追加 prompt。

## Cold review

- 独立 reviewer：`019f50bf-64f7-7a63-9eb5-d029feccbceb`。
- 首轮确认 prompt 变化范围、镜像同步、版本字段、全量 unittest 和 1.5.6 消融均无异常，但发现两个发布链阻断：`openclaw/README.md` 的 PowerShell tags 示例没有把整个参数引用为单一 token；canonical `scripts/__pycache__` 有 ignored `.pyc`，不能直接递归作为市场包。
- 最小修复：只把 README 示例改成 `'--tags=chinese,official-document,writing,gongwen,ai-compute'` 并补边界测试；不删除本地缓存，不从 canonical 工作目录直接打包，改用上述两个已核对的 19 文件干净目录。
- 仓库根目录 `pytest-cache-files-8y_vrpl7/` 因 ACL 不可读，`git status` 会给权限警告；它不在 Git diff、ClawHub 目录或 SkillHub 临时包中，作为本机非阻断残留记录。
- 同一 reviewer 修复后复核确认两个 P1 均已解决：两个市场目录均为 19 个文件、违规文件 0；全量 unittest 123/123，1.5.6/current 消融 101/102、102/102，`git diff --check` 通过。最终结论为 `resolved=true`、`publish_blocking=false`。

## 发布状态

待发布前 cold review 通过后补录 GitHub、ClawHub 和 SkillHub 实况。

## 继承风险

- 稀疏材料要求较长篇幅时，模型可能选择克制短写，也可能用近义重复补足篇幅；本轮 sanity 已出现篇幅不足 WARN。
- 600—800 字和 3000 字以上稿件仍可能偶发材料读取旁白、自我解释、篇幅不足或语义空转；1.5.7 只移除一处诱发性推荐句，不宣称彻底解决。
- 弱模型仍可能发生事实、责任、范围和情态外扩；确定性 lint 不能覆盖全部语义问题。
- finalizer、自动 repair 和用户触发二修候选均未进入发行包；精确回滚仍应依赖宿主快照，而不是让模型重新生成原稿。

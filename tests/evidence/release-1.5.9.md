# 1.5.9 论文叶隔离与发布记录

日期：2026-07-13

## 发布边界

- 上一发行基线为 `v1.5.8=bde04db86fe59dbc374742f53e67bfa0d4800376`；本轮产品提交为 `c5d81ce19bcc9337817850f74bcaf79662cfae17`。
- 仓库名、GitHub 项目、ClawHub/SkillHub slug、小红书 `skill_identifier` 和展示名均不修改。
- 公文仍为主入口；普通论文、开题报告和独立文献综述仅在用户明确要求相应交付物时进入独立专项叶。每次只加载公文、普通论文、开题或独立综述中的一个叶子。
- 公文原有文种路由、办理要素、输出模式、渐进加载、由小至大复核、默认联网和回退边界完整迁入 `references/official-writing.md`。
- 论文叶采用正向、自包含规则，不再用“不要像公文”一类对照措辞；正文只使用用户材料和已核验检索结果，材料不足时宁可短写，构造建议放正文之后。
- 未新增生成器、finalizer、检测器、硬清洗、默认多 Agent、默认联网、重排版引擎或 AIGC/查重规避能力。

## 发布前工程验证

- `py -3 -B tools\sync_adapters.py`：六组镜像和市场元数据同步成功；首次未提升权限运行在 `.agents` 目录被 Windows ACL 拒绝，随后在仓库授权范围内完整重跑通过。
- `py -3 -B -m unittest discover -s tests -v`：150/150 通过。首次及仓库临时目录重跑出现 8 个临时文件权限错误；提升权限、仍将临时文件限定在仓库发布目录后，150 项全部通过，无断言失败。
- `py -3 -B tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.8 --baseline-label baseline-1.5.8 --current-root . --out output\release-1.5.9\deterministic-vs-1.5.8`：baseline 111/113，current 113/113；基线只在新增开题和独立综述守卫失败。
- `py -3 -B evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，0 fail/error，skill 10 胜，judge consistency 1.0。未提升权限时 Promptfoo 无法启动 Python 子进程，提升权限后原命令通过。
- `py -3 -B tools\run_real_article_eval.py --out output\release-1.5.9\real-article`：skill 路径 10 个样本关键要素 61/61、关键词命中率 100%、格式/重复/反 AI 风险为 0；匿名占位标签仍只作人工复核线索。
- `py -3 -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 完整数据集 27 批最大上下文 24947，低于仓库 `<25000` 门槛；普通论文、开题、独立综述单路由分别为 4322、2802、2898 字符。
- `git diff --check`：通过，仅有 Windows 行尾转换提示。

## 真实写稿与独立复核

- 三名独立 writer 处理 6 个未见 prompt，覆盖公文起草、普通论文提纲、开题报告、独立文献综述、公文改稿和论文改稿；均按任务只读取 canonical 路由和一个选定叶子，未使用 MiniMax。
- 独立 verifier 只读取原 prompt 与成稿，A—F 全部判为 PASS：给定事实进入正文，未补造事实、数据或文献，开题计划状态和综述证据强度保持准确，公文与论文结构未互相混入，过程说明未进入成稿。
- 运行环境未暴露可核验精确模型 ID，因此本组只称独立真实写稿 sanity，不宣称完成指定 Spark/5.4/5.5 跨模型矩阵或统计显著性。
- 原始样稿和判定保存在 `tests/evidence/release-1.5.9-routing/`。

## 发行包预检

- canonical 按 `git ls-files chinese-official-writing` 白名单共 22 个文件；未递归复制物理目录中的缓存。
- ClawHub 目录 23 个文件，为 canonical 22 个文件加市场 `README.md`。
- skillhub.cn 临时包 `output/skillhub-release-1.5.9/publish-package` 为 23 个文件，为 canonical 22 个文件加 `_meta.json`；summary 使用“公文优先、明确论文任务按需进入专项叶”的表述。
- Red 专用副本 22 个文件，仅比 SkillHub 包删除 CLI 不支持的 `agents/openai.yaml`；预期和实际文件各 22 个，缺失、额外和 SHA-256 mismatch 均为 0。
- 三个发行目录无 `.pyc` 或 `__pycache__`。
- skillhub.cn dry-run 返回 `dryRun=true`、`slug=chinese-official-writing`、`version=1.5.9`。
- Red CLI 0.1.1 dry-run 返回 `status=dry_run`、`skill_identifier=chinese-official-writing`、`name=中文公文写作`、无引号版本 `1.5.9`、`original=true`、`content_tag_ids=[1002,1004]`、bundle SHA-256 `075ee9802061389794fbeeed26d70536e7bd87b0049a563a08be6d20eca29c0b`、96618 bytes。

## 独立冷审

- 产品冷审结论为功能级 BLOCKER 0：公文核心流程完整，四条路由互斥，论文三叶无公文对照词，公文叶和共用复核资料无论文规则，OpenClaw 可执行正文与 canonical 短路由一致。
- 版本同步前的发布面 BLOCKER 已处理：全镜像升至 1.5.9、SkillHub 包按白名单重建、Red 副本由新包同步并补齐三个新叶。
- 剩余非阻断风险：最大上下文距 25000 门槛仅 53 字；本版本不再扩充运行时 Prompt。真实 writer/verifier 模型 ID 不可核验，不作指定模型矩阵声明。

## 发布状态

- GitHub、ClawHub、skillhub.cn 和 Red SkillHub 的真实提交、审核与公开状态在正式发布后补记；提交成功、审核通过和公开索引切换分别表述。
- Red 1.5.8 曾在上传完成后被服务端以“Skill ID 已被占用”拒绝；1.5.9 保持原 identifier，不换新 identifier 绕过。只有终态 `RESULT_JSON.status=submitted` 和新回执才记为发布成功。

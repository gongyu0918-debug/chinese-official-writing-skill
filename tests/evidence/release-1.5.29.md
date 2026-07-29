# 1.5.29 发布证据

## 范围

1.5.29 以 `v1.5.28=f7570d4df5064582946732d283d30e86063ef142` 为固定发布基线，只发布一项紧急原子修复：

> 已选入正文的事项，直接陈述该事项已给的业务事实和当前状态。

该句加入 `references/information-selection.md` 第一条，用于降低已给事实后的来源自述、无锚定结论限定和解释性尾句。任务路由、reference 加载、文种规则、事实和状态边界、复核顺序、输出模式、修改次数、脚本、FSM 与回退方式保持不变。

## 真实写稿与判定边界

- R1 两道自然任务均未出现 Candidate 独有的事实、数字、日期、主体、状态、文种、格式、篇幅或输出模式硬回退。
- 异常通报中，Candidate 压低了固定 1.5.28 基线的“材料所述”来源泄露和“不作其他结论”无锚定否定；工作总结中的自证和解释性尾句也较少。
- R1 的两臂实际 reference 集合不完全一致，实际模型和 thinking 未从原始 rollout 闭环，因此只作为探索性真实写稿证据，不宣传为严格因果胜率或全面领先。
- R2 固定了两臂 reference 清单，但 Candidate 写手使用第 2、3 次输出，基线两稿又明显低于篇幅要求；两对均技术无效，不进入匿名排序、胜负统计或发布门分母，也没有补抽。
- 用户将本次紧急更新门调整为：相对当前稳定 1.5.28 不劣化，且对目标 P0 有可验证正向，即可进入发布回归，不要求每题明确胜出。

原始预注册、匿名结果、运行审计、R2 无效边界和独立裁决见：

- `candidate-direct-fact-state-v1528-preregister-20260729.md`
- `candidate-direct-fact-state-v1528-result-20260729.md`
- `candidate-direct-fact-state-v1528-run-audit-20260729.md`
- `candidate-direct-fact-state-v1528-r2-preregister-20260729.md`
- `candidate-direct-fact-state-v1528-r2-result-20260729.md`

## 发布级验证

- `python -m unittest discover -s tests`：390/390，`OK`。
- `python tools/run_real_prompt_ablation.py --baseline-root <release-1.5.28> --baseline-label v1.5.28 --current-root . --out output\release-1.5.29-ablation`：固定 1.5.28 为 110/110，Candidate 为 110/110。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：20/20，0 failure，0 error；Skill 10、baseline 0、tie 0，judge consistency 1.0。
- `python <skill-creator>\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `python tools/sync_adapters.py`：重复运行结果稳定；canonical 与 Codex、Agent、Qwen 的 29 个发行文件逐文件一致，Hermes 除适配 frontmatter 外共享文件一致；OpenClaw 为 27 个文件，三个非 OpenClaw 门禁文件均未进入包。
- `git diff --check`：通过。

Promptfoo 首次在沙箱内运行时，Node 无权启动 Hermes Python；改用显式系统 Python 后，仍因同一 Windows ACL 无法由 Node 创建子进程。按仓库既定环境噪声口径在沙箱外复跑后 20/20 通过，不把前两次环境错误写成产品失败或测试通过。

## 发行包与平台状态

- GitHub 产品提交、annotated tag 和 Release：发布后补录。
- ClawHub：先核验 27 文件 dry-run，再正式提交一次；回执与公开传播分开记录。
- skillhub.cn：使用 26 文件清洁包，排除 `agents/openai.yaml`、`delivery-review-gate.md`、`gate_stop_hook.py`、`review_gate.py`、tests、output、缓存和 `.pyc`；先 dry-run，再正式提交一次。
- 小红书 Red SkillHub 不在本次发布范围，不调用上传 CLI。

## 剩余风险

- 目标句只能降低保护性外扩概率，不能消除 P0；稀疏材料为满足篇幅时仍可能出现重复和自证尾句。
- R1 只有两道自然任务且运行证据不完全对称，不能外推为跨文种稳定胜率。
- R1 曾观察到一次“口径”复用增加，未达到共性修复门，不作一例一修。
- 平台发布、公开 latest、审核、扫描和 provenance 分别核验，不用一个字段替代其他字段。

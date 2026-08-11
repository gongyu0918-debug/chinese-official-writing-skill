# 1.5.25 发布证据

## 范围

1.5.25 以 `v1.5.24=f9d38c9755cf6188df2767dcfbf5bdaf659f1d1c`
为固定产品基线，只发布已经独立验证通过的改动：

1. 完整请示、申请从通用 `genre-playbooks.md` 直达
   `references/genre-playbook-request.md`；
2. 从通用 `review-checklist.md` 删除一条已由
   `format-gbt9704.md` 承担的来源模板重复说明；
3. 在 `review_gate.py` 内把五项文档不变量提取为同文件纯函数，公共行为、
   D0/D1 选择、reason、CLI、JSON、状态、哈希和回退方式不变。

信息选择、事实边界、文种功能、用户模板、篇幅预算、复核顺序、Hook、FSM、
输出模式、修改次数和回退链保持不变。第三项只作为可维护性改进，不作为写作
质量宣传点。

对应原始记录：

- `candidate-request-leaf-draft-ab-result-20260726.md`
- `candidate-word-template-line-v1524-result-20260725.md`
- `review-gate-document-invariant-extraction-result-20260725.md`

## 可复核净收益

请示/申请按实际路由选择的文种 reference 由 3928 字符降至 551 字符，减少
3377 字符，约 85.97%。规则正文从通用文种集合原样迁入独立叶子，没有删减
请批事项、行文关系、结构要素、状态或信息选择边界。

Word 复核只删除一条跨文件重复说明：

> Word 格式是否保留来源模板；正式红头格式是否有用户模板或明确要求。

`format-gbt9704.md` 继续承担来源模板优先规则，其他 Word 要素核对、正式格式
缺项和 Markdown 清理规则保持不变。

## 真实写稿

请示/申请正确路由 A/B 使用三组日常自然任务，Candidate 与固定 main 使用逐字
一致输入，各取首个技术有效输出，不补抽。Candidate 实际读取
`genre-playbook-request.md`，Baseline 实际读取 `genre-playbooks.md`。

- Judge 1：Candidate 3 胜、0 负；
- Judge 2：Candidate 2 胜、0 负、1 难分；
- 六稿事实、数字、日期、主体、待批状态、文种、格式和输出模式全部 PASS；
- 无空稿、标记残留、材料外事实、材料外程序承诺、自证边界、外围未决或 P0
  保护性外扩；
- 六稿 `prose_lint.py --structure --format` 均无风险提示。

Word 原子减负覆盖一题正式通知直接改稿和一题企业内部模板只审不改，两题匿名
盲审均由 Candidate 小胜，两侧硬边界全部通过。

本轮不重复生成 true No-Skill；发布结论只比较 1.5.25 与固定 1.5.24。精确模型
名与 thinking 档位在部分运行回执中不可用，相关字段保持 `unavailable`。

## 工程验证

- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe -m unittest discover -s tests`
  - 结果：370/370，`OK`。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`
  - 结果：20/20，0 failure，0 error，judge consistency 1.0。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe tools\run_real_prompt_ablation.py --baseline-root <v1.5.24-worktree> --baseline-label v1.5.24 --current-root . --out output\release-1.5.25-ablation`
  - 结果：Baseline 108/108，Candidate 108/108。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`
  - 结果：`Skill is valid!`。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe tools\sync_adapters.py`
  - 结果：canonical、五套发行镜像、README、OpenClaw 卡片和 Claude 插件版本面
    同步到 1.5.25。
- `git diff --check`
  - 结果：通过。

全量 unittest 与 Promptfoo 直接使用已知可运行的系统权限环境，避免把 Windows
沙箱临时目录 ACL 和 Node 启动系统 Python 的环境噪声重复计为产品失败。

## 发布包预检

- ClawHub dry-run：`status=would-publish`、25 文件、fingerprint
  `da7ca4d56ecc7571aab2f702ae23e1a47667861c769a1ece0865872a867966ff`；
- skillhub.cn dry-run：`dryRun=true`、`slug=chinese-official-writing`、
  `version=1.5.25`；临时包 24 文件，清单 SHA-256
  `e60c8de86b27c2d32acc5e7f517469ec41e1a7245eefe5bae1f390f3ac6b80e3`；
- 两个发行面均不携带 `delivery-review-gate.md`、`review_gate.py`、
  `gate_stop_hook.py`、tests、output、tmp、缓存或 `.pyc`。

首次 ClawHub dry-run 因只给 `source-repo`、未给尚不存在的发布提交而拒绝；去掉
dry-run 阶段来源字段后通过。首次 skillhub.cn dry-run 直接使用 canonical 时因
缺平台专用 `slug` 拒绝；按既有分面方式构造临时包后通过。两次都属于发布参数
预检，不是 Skill 产品失败，也没有触发正式提交。

## 发布状态

- 产品发布提交：`776a32e60f7bb0afe37f439b2710b6d0b43d40e8`；
- annotated tag object：`b21797f7a0c9f58f369f3ecb26aaea3ca42724b0`；
- GitHub `main`、`v1.5.25` 解引用提交和正式 Release 均指向产品发布提交；
  Release 为非 draft、非 prerelease：
  <https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.25>；
- ClawHub 只正式提交一次，回执为 `status=published`、
  `versionId=k977qfz5ev2c9fkbtn54hv955s8b9pd3`、25 文件、fingerprint
  `da7ca4d56ecc7571aab2f702ae23e1a47667861c769a1ece0865872a867966ff`。
  回执中的公开 `latestVersion` 仍为 1.5.24；首次公开查询也仍为 1.5.24，
  精确查询 1.5.25 返回传播中的 `Version not found`。旧公开版 moderation 为
  `clean`，不能据此推断 1.5.25 的审核状态；
- skillhub.cn 只正式提交一次，回执为 `skillId=70149`、
  `versionId=171636`、24 文件、fingerprint
  `b807f2439fb1e1c7368eebcaa846e6fa348410b720bfeb8854d1354b136bbd46`、
  `tags.latest=1.5.25`；review、security scan 和 content audit 均为
  `pending`。首次公开查询已显示 `tags.latest=1.5.25`，但
  `latestVersion` 和安全报告仍对应 1.5.24；
- 平台异步传播只记录现状，不触发重复发布。

## 剩余风险

- 新增真实写作证据集中在短篇请示、申请和两种 Word 复核场景，不能外推为复杂
  长篇、严重缺项或全部 DOCX 视觉矩阵。
- 本轮没有新增 true No-Skill 对照；质量结论限于相对固定 1.5.24。
- Review gate 职责提取行为等价，但 `evaluate_candidate` 和
  `detect_transaction` 仍是后续可继续拆分的维护点，本版不扩大范围。

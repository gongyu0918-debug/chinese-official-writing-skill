# 入口专项规则减负与 Word 回归（2026-07-22）

## 范围

- 固定基线：`v1.5.21` 发布提交 `9a98dac`。
- 变量：把仓库责任说明、低命中禁用范围和 Word 缺项长清单移出运行入口；通用事实边界继续常驻。
- Word 路径保留一条高频短锚点：命中 Word、docx、GB/T 9704 或正式版式时读取 `format-gbt9704.md`，无模板时明确标题、正文和页码的常用参数。
- `format-gbt9704.md` 承接正式要素核对、Markdown 清理、标题多行排布、页码和“排版不改正文字符”规则。

入口把 CRLF 和 LF 统一为 LF 后由 10,631 字符降至 10,366 字符，减少 265 字符，约 2.49%。PowerShell `Get-Content -Raw` 直接统计会把两侧不同换行符也计入差值，因此不作为减负结论。

## 实施中的回退与拆分

首次完整迁移 Word 长规则后，两个 Word 题都正确读取格式叶，但匿名盲审分别发现页码缺失、标题字体和页码位置回退。责任说明和低效禁用范围没有随之撤回；Word 路径单独拆分：

1. 入口恢复版式短锚点，不恢复缺项长清单。
2. 格式叶补齐无模板时的 2 号小标宋标题、标题词意换行和 4 号半角宋体一字线页码。公开依据见[教育部公文处理规定](https://www.moe.gov.cn/srcsite/A01/s7048/201309/t20130927_171853.html)和[平凉市发展改革委实施细则](https://fgw.pingliang.gov.cn/gzzd/art/2022/art_58cb4a2b5abe4509a554bc7951638496.html)。
3. 文档工具曾把用户给定的时间连接号改成 ASCII 连字符，格式叶增加“排版不改已定稿正文的用词、数字、标点和字符”通用不变量。

每次拆分后只复测受影响的 Word 题，没有重新生成固定基线，也没有用新增题稀释失败。

## 真实写稿 A/B

writer 与 judge 使用独立 subagent。基线和 Candidate 接收逐字一致的自然语言任务，均继承同一主线程模型并使用 high reasoning；协作接口没有返回可核验的具体模型名，因此模型标识记为 `unavailable`。每个运行只取首个技术有效输出。

| 任务 | 对照 | 最终盲审 | 硬检查 |
| --- | --- | --- | --- |
| T01 导视牌更新情况报告，正式 Word，五项正式要素缺失 | 最终 Candidate vs 固定 1.5.21 | Candidate 胜 | 事实、数字、日期、缺项、A4、页边距、标题、正文、落款和页码无回退 |
| T02 周末服务时间调整通知，正式 Word，无红头文号 | 最终 Candidate vs 固定 1.5.21 | Candidate 胜 | 事实、时间连接号、禁项、A4、页边距、小标宋标题、仿宋正文、落款和动态页码无回退 |
| T03 阅览室照明巡检报告，只输出正文 | Candidate vs 固定 1.5.21 | Candidate 胜 | 事实、数字、状态、输出模式和正文格式无回退 |

最终 3/3 均无事实、数字、日期、主体、状态、文种、输出模式或明确格式回退。Word 视觉渲染因本机缺少 LibreOffice 为 `unavailable`；实际核验了 DOCX 正文、OOXML、字体、字号、段落、节、页边距、落款和页码字段。

原始产物位于忽略目录 `output/entry-word-relief-real-ab/`，不进入发行包。

## 工程验证

- `python -m unittest discover -s tests`：353/353 通过。沙箱内 `tempfile` 受 ACL 拒绝，使用已核验的系统 Python 在沙箱外复跑；该首次失败记为环境噪声。
- `python evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，0 error。
- `python tools/run_real_prompt_ablation.py ...`：固定 1.5.21 为 108/108，current 为 108/108。
- `quick_validate.py chinese-official-writing`：通过。
- `tools/sync_adapters.py`：canonical 已同步到各发行镜像。
- `git diff --check`：通过，仅有既有 LF/CRLF 转换提示。

## 结论与剩余风险

本批可保留。它证明责任说明、低命中禁用范围和 Word 缺项长清单无需常驻入口；Word 仍需要少量高曝光版式参数，完全只留 reference 在真实测试中不稳定。

LibreOffice 缺失使最终分页观感、字体替换和垂直位置未做图像级复核。本批之后，AI 算力专项句已另经真实 A/B 通过；字段式材料和网页复制稿迁移均因质量回退撤回。文种结尾等尚未测试的承重规则仍需独立验证，不以本批结果代替。

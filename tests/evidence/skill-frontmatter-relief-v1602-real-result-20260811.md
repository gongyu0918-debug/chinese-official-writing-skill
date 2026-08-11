# SKILL frontmatter 元数据减载真实结果（v1.6.2）

结论：`REAL NON-INFERIOR METADATA RELIEF / ENGINEERING PASS / ELIGIBLE FOR LOCAL INTEGRATION`。

## 产品差异

- 固定基线：`d17cb8853274ba6dec4d686171daf4f8972a0ec8`。
- 产品提交：`83afc6d250f55733fbc08f12f71792fa038367b1`。
- 六个运行面 frontmatter 顶层只保留 `name`、`description`、`metadata`，且 `metadata` 只含 tags；删除 license、版本、兼容 Agent 列表、安装路径和平台展示字段。
- 六个可执行正文逐字等价；canonical/`skills` 各减 685 字符，`.agents`/Qwen 各减 687，Hermes 减 552，OpenClaw 减 610。
- SkillHub clean allowlist 排除 `agents/openai.yaml` 与包内 `LICENSE`；根许可证及插件 manifest 不变。

## 真实执行

- 写手：Alibaba Token Plan DeepSeek V4 Flash 0731 max、Ollama Cloud DeepSeek V4 Flash 0731 max、MiniMax M3 max。
- 18/18 次完成，9/9 对技术有效；三家各 6 次，首个 final、零重试。
- 18/18 return code 0，final 非空，并通过 trace 实际读取对应 `SKILL.md`；技术失败、缺 exact read、非零退出和缺 final 均为 0。
- 盲包：`C:\Users\admin\Documents\Codex\runtime-evidence\skill-frontmatter-relief-v1602\run-20260811\blind-packet.md`。
- 盲包 SHA-256：`76B1E77CE4B6E6657362A3E0DC4FCD22C833865C24A1ECADFE07E4CC22583480`。
- manifest SHA-256：`159E859B8C31C03A2C6FBC421C871A3AC8DA725B3E402C044200AD516F496A14`。
- mapping SHA-256：`73D3150154231D7EFA29FE6BA940D710488EE4287A76D6DAC492FD2826A9134B`；完整文件保留在运行目录，冻结 SOL 判词提交 `39a9eef8` 后才读取。

执行前有三次本地预备失败：merge-base API 参数误用、CRLF/LF 正文比较误判、日志父目录不存在。三次均发生在模型调用前，没有 final；修复预检后只启动一次 18-call 正式矩阵，未覆盖原错误记录。

## 盲审与解盲

SOL 只读取盲包并先核验哈希；原始判词见 `tests/evidence/skill-frontmatter-relief-v1602/sol-blind-review.md`。

| 结果 | Candidate | Baseline |
| --- | ---: | ---: |
| 配对胜 | 4 | 5 |
| PASS | 2 | 1 |
| WARN | 3 | 2 |
| FAIL | 4 | 6 |

- Candidate 胜：B003、B004、B006、B007；Baseline 胜：B001、B002、B005、B008、B009。
- 两臂正文均未泄露 license、兼容 Agent、安装路径、仓库或平台元数据，目标硬回退为 0。
- 长篇稀疏材料补写流程/责任/下一步、运行命令旁白、只审不改项目膨胀均在两臂出现，没有形成同 provider、同机制、Baseline 为 0 的 Candidate 重复回退。
- 短通知中“核对抽检记录”被误写为“抽检整理记录”出现两次，但分别落在 Candidate 与 Baseline；属于共性解析风险。
- Candidate 单次多写“提前做好相关准备”、单次审查膨胀和单次运行旁白均未重复，也与删除发布元数据没有直接语义机制。

因此配对票数 4:5 不能推翻确定的字符减载，也不能宣称质量提升；按预注册裁决为真实非劣元数据减载。

## 五提交暂停复核

- `python -B -m unittest discover -s tests -p 'test_*.py'`：492/492 PASS。
- `OFFICIAL_WRITING_EVAL_STUB=1 npm.cmd run eval:official-writing:smoke`：20/20 PASS，run `eval-r5w-2026-08-11T10:17:56`。
- 固定基线确定性消融：baseline 111/111，current 111/111。
- `quick_validate.py chinese-official-writing`：PASS。
- Codex plugin validator：PASS；Claude plugin validator：PASS，保留既有 author warning。
- harness 与同步器 py_compile：PASS，pycache 写入系统临时目录。
- `sync_adapters.py` 连续两次 diff hash 均为 Git 空树 hash `e69de29b...`，幂等。
- `git diff --check`、工作树清洁检查：PASS。

## 剩余风险

- 真实样本再次确认长篇稀疏材料的流程幻觉和输出旁白是跨臂共性风险；本原子不修复它们。
- SkillHub 专用发布 frontmatter 仍需保留 CLI 强制的 slug/version/displayName；该减载由独立 clean-package 构建器处理。

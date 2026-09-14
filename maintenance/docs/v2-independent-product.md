# 中文公文写作 2.0：独立产品准备

2026-09-14 用户确认：产品名称为“中文公文写作 2.0”，独立标识为 `chinese-official-writing-v2`。与 1.x 分线维护，不合入 1.x main、不覆盖原平台条目；本轮验证与准备，不实际发布。目标日期为 2026-09-15，是否具备条件以本轮真实写稿、增量冷审及最终报告为准。

2.0 源线为 `codex/reference-rewrite-20260912`，本轮候选在 `codex/v2-independent-readiness-r31`。1.x 发布线程不受本轮操作影响。已有 1.x 和其 Hook 的 MIT 授权继续有效，2.0 独立包没有 Hook，保留普通篇幅与文稿扫描脚本；Pro 接续另行处理。

本轮对照先保持两臂相同的安装目录名和相同题面，避免把产品改名与写作规则变化混为一谈。独立发行通过 `maintenance/tools/build_v2_preview.py` 从被冻结的 2.0 canonical 制作，只替换 SKILL 的 name/显示标题及 README 产品说明；references、scripts 逐字节保持一致。打包目录和 ZIP 均含新标识，包清单和 SHA-256 在输出目录 manifest 中保存。旧 `packages/` 中 1.x 标识的兼容包不用于独立产品上传。

预览包含 SKILL.md、README.md、LICENSE、67 个 references 和两个 scripts，共 72 文件。没有复制可选 `agents/openai.yaml`，因其默认 prompt 仍指向旧标识；此文件不承载正文规则。Word 能力仍由宿主文档工具完成。预览须作一例使用真实新目录名和新 name 的原生调用；成功前只称包结构通过，不能称新产品已真实使用通过。

完整预登记与结果位于 `maintenance/tests/evidence/v2-independent-readiness-r31/`。规则量、实际加载量、模型 input/缓存/输出、耗时、正文质量分别报告。正式替代 1.0、全面优于 1.0、普遍更快更省均须另有相应证据，不从静态减载比例推导。

2026-09-14 R31 已完成 40 次原生调用，39 次技术有效；选择性采用 Markdown 修复，独立产品公开发布建议 HOLD，见[最终报告](../tests/evidence/v2-independent-readiness-r31/results.md)。最终预览 SHA-256 为 `17fbcb54eba56aba636b6f6034bfb0c743e17c304733c5cbc12d7f6c1c6c59a2`。新标识已完成原生读页与 Word 文件生成；两版最终文件链接均失效，因此只确认新标识可加载，不称完整下载交付通过。包未发布。

# R25 证据归档工程冷审

结论：本次限定范围内的工程问题已关闭；未发现仍需修改的阻塞项。已完成的 MiniMax 实际归档及匿名副本保持上一轮通过结论；新增 invalid 分支的整体验证由主代理最终归档验证确认。本报告不评价稿件质量，不覆盖运行中的 Qwen。

最终审查版本：`run_real.py` SHA-256 `024bc76fe893f3a1732bca97f190079e033cd6b840e7ff53f6f5352191c33a3a`；`archive_actual.py` SHA-256 `38c3067fa1fb0f539b7062a979e68ed6b40c16e1ad8473e1461e6b726a532a62`，115 行。以下行号均指该版本；MiniMax 字节核验沿用上一轮已完成结果，未重新建包或复核整批。

## 最终复核状态

- **receipt 路径缺口已关闭**。`archive_actual.py:12` 统一使用 FORBIDDEN；`:56–57` 在保存 compact 前扫描序列化字节；`:87–92` 在加入 scope_audit 后、保存完整 receipt 前再次扫描。failure 和 scope 自由文本因此都经过盘符路径检查。内存检查确认两处断言存在：含合成正斜杠 failure 路径、反斜杠 scope 路径的 JSON 均被识别；安全的 TimeoutExpired/相对范围摘要通过。没有扩大扫描范围。
- **final/work 修复已复核**。`:25–30、49–52` 只替换本 lane runtime/work 前缀，源 final 与归档 final SHA、替换次数分列；`:39` 工作稿命中禁入模式直接阻断，未命中保留原字节。上一轮正/反斜杠路径替换及盘符、私钥头、Authorization Bearer 三种合成阻断检查通过。本轮脚本内存 compile 再次通过，没有调用归档函数或读取 Qwen 文件。
- **无效分流和中断边界已复核**。`:67–83、86–92` 先确认 provider 六份 receipt 与 scope 源哈希齐备，再将 scope 或 runner 无效的 lane 分流，最终有效性取两者相与。`:27、34–44、53–55` 只保留当前 work 内文件，拒绝解析到边界外的路径，将 runner 失败残稿标为 interrupted_working_file_not_final_delivery。残稿不得补成 final、有效样本或质量票。主代理报告的隔离 runtime/claude-config 越界记忆文件不作为工作稿导入；本次未读取这些文件。

## 已完成的只读核验

用 `python -B -X utf8 -` 内联核验：实际归档 28 个 manifest 条目、匿名包 17 个条目的精确文件集合、字节数及 SHA-256 全部通过。六个 MiniMax session 唯一；六份原始 final、receipt 所列三份本 lane work 文件与实际归档逐字节相同。归档 final 同时符合 receipt 的源字节哈希、归档哈希及换行归一化后的逻辑哈希，六份均无脱敏替换。

九份匿名交付副本与对应实际 final/文件逐字节相同；三份匿名 materials 与归档 prompt 相同，且符合 freeze 中 prompt 哈希。delivery.json 没有漏掉 receipt 所列的 written_text 文件。六份紧凑 receipt 的 scope 内容与 scope-audit 相同，并逐一绑定原始 receipt SHA；六份均 runner/scope 有效，所以本批没有无效 MiniMax 样本可验证剔除分支。

两臂各 41 个规则文件，manifest 仅两处 overlay 不同；四份 overlay snapshot 均符合各自 manifest。`run_real.py:32–35` 将复用 runner/extractor 顶层源码按 LF 归一化绑定到既定 commit；本轮不重新审核传递依赖。旧 Claude receipt 没有 prompt_sha256，不能将共享 prompt/freeze 一致说成每次调用都具有独立 prompt 哈希证明；调用内容的比较依赖提取阶段 invocation 检查，本次未扩读 invocation。

实际/匿名文件集合未夹带 stream、invocation、runtime 或凭据文件。对已归档 TXT/JSON 的绝对盘符路径、显式 think 包裹和常见凭据模式扫描无命中；这不替代任意秘密的完备检测。第一次路径正则误命中了 HTTPS 的 `s:/`，修正为盘符边界后重跑全部检查通过。两份脚本在内存中 compile 通过，未生成 pycache。本次末轮仅复核新增 invalid 脱敏代码，没有重做以上 MiniMax 字节核对。

## 未覆盖与最小后续验证

不等待、不读取、不操作运行中的 Qwen；本审查者未运行新增 invalid 分支，也未重新建包。主代理另报告：两个 invalid 实际源归档 smoke 已通过，原始 failure 为 null/TimeoutExpired，scope 文字已人工核准无绝对路径；这些是主代理提供的结果，本次未独立复跑。最终两处 receipt 扫描后的归档验证由主代理继续执行，不能把本次静态与内存检查写成该整体验证已通过。不需要新增模型调用或审查框架。

本次仅写本报告，没有修改产品、脚本、冻结归档或匿名包，没有执行 Git 操作。实际归档 manifest SHA-256：`fe58f3de5c37f41d8caebb105bd8ce6ca8b10eecc5370db793ddb60043948038`；匿名 manifest：`3f72948c491a9b94f23f23be79a9580fd45d5cf1b2e7f14b6b2086c4ae1b537d`。

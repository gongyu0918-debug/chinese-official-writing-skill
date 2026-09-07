# 实际写稿证据

本次归档 14 次已完成调用：技术有效 14 次、技术无效 0 次。技术有效不等于写稿质量通过。

`runs/` 分开保留最终回复、脱敏 receipt 和实际工作稿；后者由 Read/Write/Edit 的路径核验为该次隔离工作目录内的文件，再读取最后落盘字节，不能用生成文件摘要冒充正文。缺失工作文件 0 份；未完成调用见 [汇总](summary.json)，不算有效样本。

final 副本仅将该次已核准的工作目录前缀替换为 `<isolated-work>`，共 1 处；receipt 分列原文件与归档副本 SHA-256、替换数量。其余字节及实际工作稿不改。Skill 工具的启动确认单列记录；没有 Read SKILL 不等于没有加载，CLI 未回显正文时不能声称已直接观察完整正文。

超界且已有明确工具错误响应的 Read 仅登记为 `unresolved_failed_read`，保留参数哈希与响应观察，不读取范围外文件，不计入包曝光或文稿；本次共 3 次。成功或响应不明的超界读取仍拒绝归档。

`prompts/` 保留调用原提示；`manifests/` 保留冻结包清单；`snapshots/` 保留 SKILL.md、handling-elements.md 与 argument-chains.md 的实际冻结版本。本次验证 205 项包文件哈希。未复制 runtime、授权、原始流、原 argv、shell 参数或输出、绝对机器路径。

[SHA-256 清单](archive-manifest.json) 覆盖本目录除清单自身外全部文件。运行 `python -B -X utf8 maintenance/tests/evidence/application-materials-r13/archive_actual.py --verify-only` 复核；暂存后可用 `--verify-index` 核验 Git 索引字节。重新归档仅处理现存 receipt。首次归档时可用 `--arms baseline candidate` 限定 R13；已有后续轮次归档时须不带 `--arms`，不得缩小已归档范围。

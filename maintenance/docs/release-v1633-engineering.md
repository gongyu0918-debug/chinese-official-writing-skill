# v1.6.33 工程与制品记录

## 目的与范围

本版优化正式词语的语义审校：有明确对象、专业含义或必要强调时保留，空泛表述按已有事实压实，避免机械换词。唯一写作规则改动是 `anti-ai-patterns.md` 的“高频正式词”段，LF 字符量从 5409 降至 5340，减少 69；首页保持 7930 字符，不把该段减量等同于整次调用减载。

公开基线为 `v1.6.32`（`236784efe2a7a0bf9acd3a49f1d3ad0cff1586a8`），实稿冻结为 `dded78a783aaac897a024ca77a331de6eefe9809`。加入必要版本工程后的固定产品提交为 `5d84c5d3e52dac0b006d6c6aa5a06d32e080d2b0`，canonical tree 为 `bc9f538eab44cf8d83d3e6af33018c52bd24d658`。

canonical 的 90 文件集合不变，只有目标叶和七个宿主 adapter 的版本字段变化；七份 JSON 去掉 `version` 后与基线相等。其他写作规则、首页、路由、Hook 实现及脚本保持公开基线内容。必要工程同步了 README、安装版本、生成包说明、同步脚本 VERSION 和既有版本断言；兼容包继续按需生成。详情见[范围记录](../tests/evidence/release-v1633-engineering/scope.json)。

## 验证

真实写稿在独立冻结输入上完成 12 次调用、11 份有效终稿、5 组同档完整对照（4 组 max、1 组 high）。四组双臂读取目标叶，一组为旁路。主审未发现候选单侧事实、状态、文种功能或完整正文硬退化；定向审校的过程说明及不准确的“自指”理由、普通说明多出的“特此说明”均保留，不宣称整体写作更好。详见[实稿报告](release-v1633-writing-validation.md)。

工程命令使用 Hermes 环境 Python，与实稿驱动的 Python313 入口分别记录：

```powershell
& 'C:/Users/admin/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability maintenance.tests.test_real_prompt_ablation
& 'C:/Users/admin/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -m unittest discover -s maintenance/tests -p 'test_*.py'
```

- 相关最小检查：116/116 通过，exit 0，unittest 1.656 秒，实际墙钟 2.236 秒。见[记录](../tests/evidence/release-v1633-engineering/related-checks.json)。
- 最终全量：827/827 通过，exit 0，unittest 139.924 秒，实际墙钟 140.995 秒。只执行一次，运行 HEAD 为固定产品提交 `5d84c5d3`；没有版本断言失败或补跑。见[完整记录](../tests/evidence/release-v1633-engineering/full-engineering.json)和[封存日志](../tests/evidence/release-v1633-engineering/archive/final-full-suite.txt)。
- canonical 与 Agent Skills、Qwen Code、QwenWork、Hermes 四个生成目录的 `quick_validate.py` 共 5 项通过。逐项实际命令、路径与输出见[快速验证记录](../tests/evidence/release-v1633-engineering/quick-validation.json)。OpenClaw 保留平台需要的 `category`，沿用既有工程边界检查，不冒用普通 frontmatter 快检。

## 制品及字节边界

[构建编排](../tests/evidence/release-v1633-engineering/build_release_artifacts.py)复用 `sync_adapters.py` 和 `build_skillhub_package.py`，GitHub canonical 从固定提交的 Git blob 生成。最终目录为本工作树下 `output/release-v1633-artifacts-final/`，不包含维护证据、评测缓存、付费内容或本机 Pro 安装。

| 制品 | 文件数 | 相对 v1.6.32 的范围 |
| --- | ---: | --- |
| GitHub canonical | 90 | 目标叶及七个 adapter 版本字段 |
| SkillHub | 90 | 文件集合不变；精确 10 个文件变化：目标叶、SKILL 版号、`_meta.json` 版号及七个 adapter 版号 |
| ClawHub | 40 | 文件集合不变；精确 2 个文件变化：目标叶及 SKILL 版号；继续排除 Hooks 和不可用门依赖 |

首轮包清单断言发现 `reference-index.md` 的意外字节差异：旧平台包为 LF，本工作树复制后为 CRLF，Git blob 和规范化内容完全相同。首轮输出原样保留在 `output/release-v1633-artifacts/`；最终目录复制已完成构建后，仅将生成包中的这个未改页恢复为对应 Git 原字节，再以原来的精确差异集合完成清单和 ZIP 验真，没有扩大允许集合，没有修改产品或既有构建器，也没有重复全量或快速验证。见[首轮及收尾记录](../tests/evidence/release-v1633-engineering/packaging-first-attempt.json)。

三个 ZIP 均通过 CRC、精确成员集合和逐成员 SHA-256 核对。各目录逐文件清单、目录内容哈希的定义、ZIP 路径及 SHA-256、清单 SHA-256 和 `SHA256SUMS.txt` 均记录在[制品清单](../tests/evidence/release-v1633-engineering/package-manifests.json)。GitHub 使用 Git 字节，两个平台使用其既有包生成边界；不要求不同平台的同名文件逐字节相同。

本工程阶段已完成本地制品准备，未执行 push、tag、Release、平台上传、main 合并或本机 Pro 同步。对外发布由主任务另行执行并记录，不能把此处的本地 ZIP 验真当作平台提交回执。

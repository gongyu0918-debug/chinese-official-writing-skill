# post-v1.6.10 维护可达性审计

## 范围

本轮检查 canonical、Hook、维护工具、评测入口、兼容包、轻量规格和当前维护索引。历史发布包、冻结盲审 packet、裁判原文和归档快照保留原始内容，不以当前目录重写历史证据。

## 结果

- 28 个活动 Python 脚本均至少由 SKILL、Hook 配置/组装器、维护索引、评测入口或其他真实调用者接引，零孤儿脚本。
- 21 个含 `__main__` 或 argparse 的 CLI 入口均有非测试入口；零“只有单测知道如何调用”的 CLI。
- 189 份非入口活动 Markdown 均由 SKILL、README、规格索引、包索引或维护索引接引，零孤儿 Markdown。
- 根 README、AGENTS、canonical、全部 packages、maintenance README、轻量规格、待办和维护证据索引共195份活动 Markdown，本地相对链接零失效。
- 全部990份 tracked Markdown 的宽扫描发现17个旧路径：2个来自迁移后的 `AGENTS-legacy-20260819.md`，本轮已改为有效相对链接；其余15个位于冻结历史 evidence/匿名 packet/裁判原文，保持原始证据，不作为当前入口，也不回写。

## 固化检查

`maintenance/tests/test_repository_reachability.py` 继续覆盖 canonical reference/script、Hook 资产、package/maintenance 子目录与根 README；本轮增加：

- 轻量规格每个文件必须由 `maintenance/specs/README.md` 索引；
- 产品、评测和维护 CLI 必须有非测试入口；
- 195份活动 Markdown 的本地相对链接必须真实存在。

实际命令：

- `python -B -m unittest maintenance.tests.test_repository_reachability -q`：7/7 PASS；
- 与共享硬锚、篇幅能力及 Hook 边界合跑：39/39 PASS；
- tracked 文件入链扫描与 Markdown 本地链接扫描（只读）：990份 Markdown 中只剩冻结历史 evidence 的15个旧路径，活动面为0；
- `sync_adapters.py` 后 packages 零差异，quick validation PASS，`git diff --check` PASS。

历史 evidence 中的旧路径仅用于还原当时目录，不应复制成当前运行命令；需要现行入口时从 `maintenance/README.md`、`maintenance/specs/README.md` 或 `maintenance/docs/evidence/README.md` 进入。

# QwenWork（Qwen 办公）适配

本目录保留 QwenWork 普通 Skill 的安装说明，不保存产品副本。写作内容从仓库 canonical `chinese-official-writing/` 机械同步，不包含交付 Hook。

从仓库根目录先运行 `python .\maintenance\tools\sync_adapters.py --host qwenwork`，生成 `output/compatibility-packages/qwenwork/skills/chinese-official-writing/`。

## 个人安装

将生成的 `output/compatibility-packages/qwenwork/skills/chinese-official-writing/` 整个目录复制到：

```text
~/.qwenworkcn/skills/chinese-official-writing/
```

安装后目录中的入口应为 `~/.qwenworkcn/skills/chinese-official-writing/SKILL.md`。

## 组织上传

上传 ZIP 时，压缩包顶层只放一个 `chinese-official-writing/` 目录；该目录内包含 `SKILL.md`、`references/`、`scripts/` 和 `LICENSE`。顶层目录名与 `SKILL.md` 的技术名称一致。

QwenWork 与 Qwen Code 是两个宿主。本目录只适配 QwenWork 的静态 Skill；Qwen Code 普通包按 `packages/qwen-code/` 的说明构建，已验证 native Hook 位于 `chinese-official-writing/hooks/adapters/qwen-code/`。

QwenWork 官方 Hook 文档目前没有公开完整 Stop 成稿字段或可绑定的当前回合记录，因此本包不声明写后交付门禁 Hook 可用。普通起草、改稿、压缩和复核可直接使用本 Skill。

构建命令（已有输出时使用新的 `--output-root`）：

```powershell
python .\maintenance\tools\sync_adapters.py --host qwenwork
```

官方说明：[Skills](https://qwenwork.cn/docs/features/skills) · [组织 Skill 包](https://www.alibabacloud.com/help/en/qwenwork/skills-management) · [Hooks](https://www.alibabacloud.com/help/en/qwenwork/hooks)

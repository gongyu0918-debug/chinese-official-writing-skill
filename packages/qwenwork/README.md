# QwenWork（Qwen 办公）适配

这个目录提供 QwenWork 可安装的普通 Skill 包。写作内容从仓库 canonical `chinese-official-writing/` 机械同步，不包含交付 Hook。

## 个人安装

将 `skills/chinese-official-writing/` 整个目录复制到：

```text
~/.qwenworkcn/skills/chinese-official-writing/
```

安装后目录中的入口应为 `~/.qwenworkcn/skills/chinese-official-writing/SKILL.md`。

## 组织上传

上传 ZIP 时，压缩包顶层只放一个 `chinese-official-writing/` 目录；该目录内包含 `SKILL.md`、`references/`、`scripts/` 和 `LICENSE`。顶层目录名与 `SKILL.md` 的技术名称一致。

QwenWork 与 Qwen Code 是两个宿主。本目录只适配 QwenWork 的静态 Skill；Qwen Code 的 Skill 包和已验证 native Hook 分别位于 `packages/qwen-code/` 与 `chinese-official-writing/hooks/adapters/qwen-code/`。

QwenWork 官方 Hook 文档目前没有公开完整 Stop 成稿字段或可绑定的当前回合记录，因此本包不声明写后交付门禁 Hook 可用。普通起草、改稿、压缩和复核可直接使用本 Skill。

同步命令：

```powershell
python .\maintenance\tools\sync_adapters.py
```

官方说明：[Skills](https://qwenwork.cn/docs/features/skills) · [组织 Skill 包](https://www.alibabacloud.com/help/en/qwenwork/skills-management) · [Hooks](https://www.alibabacloud.com/help/en/qwenwork/hooks)

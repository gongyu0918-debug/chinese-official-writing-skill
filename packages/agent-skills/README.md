# 通用 Agent Skills 安装包

普通 Skill 从唯一 canonical 产品按需生成，不在此目录保存副本：

```powershell
python .\maintenance\tools\sync_adapters.py --host agents
```

从仓库根目录执行后，复制 `output/compatibility-packages/agent-skills/skills/chinese-official-writing/` 到宿主的 Skill 安装目录。该包不含交付 Hook；可选 Hook 仍使用独立适配及组装流程。所有生成选项见[兼容包索引](../README.md)。

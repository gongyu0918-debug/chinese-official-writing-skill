# 兼容包构建与安装

写作规则和脚本只维护在 `chinese-official-writing/`。本目录保留安装说明；普通 Skill 副本、上传包和 Hook companion 均按需生成到 `output/`，不提交 Git。生成器不修改 canonical，也不覆盖已有输出。

从仓库根目录运行：

```powershell
python .\maintenance\tools\sync_adapters.py
```

默认生成 `output/compatibility-packages/` 下五种目录。只需一种时使用 `--host openclaw`（可重复）；再次构建时以 `--output-root output/compatibility-packages-next` 指定新的输出目录。

| 说明目录 | `--host` | 生成目录及用途 |
| --- | --- | --- |
| `agent-skills/` | `agents` | `agent-skills/skills/chinese-official-writing/`；通用 Agent Skills，包括 MiniMax、GLM、ZCode、Kimi Code CLI、TRAE 等 |
| `qwen-code/` | `qwen` | `qwen-code/skills/chinese-official-writing/`；Qwen Code 普通 Skill |
| `qwenwork/` | `qwenwork` | `qwenwork/skills/chinese-official-writing/`；个人复制安装或组织 ZIP |
| `hermes/` | `hermes` | `hermes/skills/chinese-official-writing/`；Hermes 普通 Skill |
| `openclaw/` | `openclaw` | `openclaw/skills/chinese_official_writing/`；OpenClaw 安装与 ClawHub 发布输入 |
| `red-skillhub/` | — | 旧平台副本已归档，不作为当前产品或自动生成目标 |

普通包保留原目录、名称和平台元数据转换，并排除 Hook。使用通用安装器时仍可直接安装仓库的唯一 canonical Skill；需要普通无 Hook 副本时复制相应生成目录。

## 发布和 Hook

SkillHub.cn 从 canonical 构建，发布者显式指定版本和新的输出目录：

```powershell
python .\maintenance\tools\build_skillhub_package.py --version 1.6.32 --output output/skillhub-release
```

ClawHub 的包输入是 `output/compatibility-packages/openclaw/skills/chinese_official_writing/`。打包不代表发布；实际平台写入仍须当次授权。历史证据中的旧 `packages/.../skills/` 命令只描述当时冻结树，不用于当前发布。

可选 Hook 的唯一核心及静态宿主适配保留在 [hooks](../chinese-official-writing/hooks/README.md)，各宿主的注册、事件协议和目录差异不合并删除。仍由现有组装器生成，例如：

```powershell
python .\maintenance\tools\assemble_hook_companion.py --host codex --output output/codex-hook
```

这些生成产物都不含 `maintenance/`。同一组生成规则也供测试在临时目录使用，不要求先生成或恢复仓库副本。

## 旧副本恢复

六套旧副本在删除前已按公开提交 `0721297298b72be7a37b93c6598172791b58e421` 的原始 Git blob 存成仓外 ZIP，逐文件回读核验；清单摘要见 [archived-copies.json](archived-copies.json)。恢复到新的临时目录后可核对旧发布字节，不要把旧副本恢复为当前产品源。公开 Git 历史中的该提交同样保留原文件。

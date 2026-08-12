# v1.6.2 Hook capability-first 与知情启用修订

## 固定基线

- 产品基线：`2135fba6e05ee9a3d9c9f931237a9eb01b0cc107`
- 分支：`codex/v162-package-architecture`
- 本修订不改变写稿规则，不纳入篇幅补写 Hook，不授权发布、推送或修改远端平台。

## 用户确认的结构

源码按能力和协议分层，不长期跟踪三份完整插件：

```text
chinese-official-writing/hooks/
  README.md
  core/
  adapters/
    codex/
    codebuddy/
    claude-code/
```

- `core/` 是唯一门禁核心。
- `adapters/<host>/` 只保存宿主 manifest、事件配置、薄适配器和宿主说明。
- adapter 是静态兼容文件，不在用户侧附带自动构建器。用户明确要求启用后，Agent 按对应 README 的固定清单预览并组装胶水层；仓库维护测试可以在临时目录复放同一清单，但维护工具不进入 SkillHub 用户包。

## 知情与执行边界

1. 下载或安装普通 Skill 不执行 adapter、不生成文件、不安装插件、不启用 Hook。
2. 组装 companion 必须由用户明确要求；宿主、源文件、目标目录和拟写入清单在执行前可见。
3. 组装只复制仓内静态文件；不扫描已安装 Agent、不读取用户稿件、不联网、不修改宿主配置。
4. 组装、安装、启用和信任确认是独立步骤。完成组装后必须明确报告尚未安装、尚未启用，不得顺带继续安装。
5. Hook 启用后只处理当前宿主传入的请求、Skill 读取事件、D0、门禁状态和输出哈希，并写入宿主提供的本地插件数据目录；不得上传或汇总 Agent 清单。
6. 用户在当前任务中明确说“关闭 Hook”“本次不要用 Hook”或“跳过交付门禁”时，记录 `bypass=user_requested`，不创建事务、不阻断输出。否定关闭、继续启用以及“不要用脚本”等泛化表述不得误触发。
7. 未安装、未启用、不受宿主支持或被用户旁路时，普通 Skill、references 与 `prose_lint.py` 必须保持和 v1.6.1 一样独立闭环。

## 验证门

- 三宿主 companion 的维护期临时组装均使用同一 canonical 和静态清单，包内只有一个宿主 manifest、无 `../`、无外部链接和 symlink，且包含完整 Skill、门禁核心、必要脚本与 MIT LICENSE。
- SkillHub 用户包中不得出现自动构建、自动安装、网络探测或宿主配置写入代码。
- 三宿主事件 smoke 覆盖普通启用、明确旁路、否定旁路、纯审稿和无 Hook 五条路径。
- 可达性测试覆盖 SKILL→references/scripts、Hook README→core/adapters/builder、adapter manifest→生成包运行链；未接引文件阻断交付。
- 工程门通过后再执行用户授权的三 provider Hook on/off 真实写稿 A/B；真实测试不纳入篇幅补写功能。

## 最终冷审与真实模型门

1. 冻结 `v1.6.0^{commit}`、当前候选、完整 DIFF 与分类清单。目录/许可重排、写稿规则变化、Hook 行为变化分别审计，不能用净行数替代语义归因。
2. Hook on/off 真实写稿固定使用 OpenCode Go、Ollama、Alibaba Token Plan 2 的 `deepseek-v4-flash-0731`，reasoning 为 max；provider 和 model 必须精确 probe，不得回退同名旧 key。
3. 冻结匿名写稿包后，解盲前分别交给 Kimi K3、Alibaba Token Plan 2 的 Qwen3.8-max、Grok4.5 冷审。三名裁判读取同一哈希材料，零重试；超时、配额、编码、污染或缺少完整 final 原样记 INVALID，不补抽。
4. 冷审重点包括相对 v1.6.0 的新增 Hook、新闻与新闻评论能力、目录/兼容层、无 Hook 闭环、事实状态边界、AI 味和额外生成成本。模型票数不得覆盖确定性断链、数据越界或用户 opt-out 失败。

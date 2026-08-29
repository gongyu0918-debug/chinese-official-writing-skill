# HK-004-QWENWORK-R1 预注册

## 目标与边界

- 目标：为 QwenWork 增加可直接安装的中文公文写作 Skill 静态包，不改变 canonical 写作规则、description、references 或 Hook 核心。
- 官方安装面：个人 Skill 使用 `~/.qwenworkcn/skills/<skill-name>/`；组织上传 ZIP 的顶层目录名与 `SKILL.md` 中技术名称一致。
- Hook 边界：QwenWork 官方 Hook 文档列出 `UserPromptSubmit`、`Stop` 等事件，但没有公开说明 Stop 输入中存在完整最终正文或可绑定的当前回合记录。本轮不增加 QwenWork Hook adapter，也不声称写后门禁生命周期可用。
- 本轮不安装或控制 QwenWork GUI，不修改用户配置，不合并、不推送、不发布。

## 固定候选

1. 新增 `packages/qwenwork/skills/chinese-official-writing/`，由 canonical Skill 机械同步，沿用 MIT，排除 Hook、`delivery-review-gate.md` 和 `review_gate.py`。
2. 新增 `packages/qwenwork/README.md`，明确个人安装目录、组织 ZIP 顶层目录、Qwen Code 与 QwenWork 的区别及未验证的在线生命周期。
3. 仅扩展同步器、包索引、仓库说明和包体边界测试；不修改产品正文语义。

## 真实结果优先

- 在隔离、只读、无 Hook 的 CLI 运行目录中，把 QwenWork 包复制为唯一项目级 `.agents/skills/chinese-official-writing/`，使用一条已登记低成本写稿模型、`max` 思考完成一份真实事务性稿件。
- 提示词不提供目标答案；要求模型自主加载项目级 Skill。有效样本必须能从 trace 证明读取该隔离包，并交付可直接使用正文。
- 合理的一层原因、作用、总结或常识推断不算事实外扩；只有材料外数值、具体用途、程序、责任、日期、完成承诺或状态升级算硬回退。
- 该样本只证明静态包内容可加载并能写稿，不冒充 QwenWork GUI、自动触发或 Hook 生命周期证据。

## 确定性验收

- 同步后包内相对文件和字节与 canonical 的无 Hook allowlist 一致；MIT 一致；无不安全路径；ZIP 顶层只有 `chinese-official-writing/`；压缩包不超过 10 MB。
- `packages/qwenwork/` 不含 Hook、门禁脚本或 Hook 路由文字。
- 直接相关单测、链接/状态测试、Python 编译、`git diff --check` 通过。
- 技术失败不算质量失败；若静态包写稿出现候选独有硬回退，先停止候选，不用工程门掩盖。

## 风险登记规则

若真稿暴露 canonical reference 的问题，只登记与样本直接相关的单一原子：固定一类文种、一个状态/事实边界和一个最小修改，再用新题真实写稿验证。不得把合理归因、常识推断或有限影响误判为外扩，也不得借 QwenWork 包支持顺带修改产品 reference。

## 官方来源

- QwenWork Skills：<https://qwenwork.cn/docs/features/skills>
- QwenWork 组织 Skill 包：<https://www.alibabacloud.com/help/en/qwenwork/skills-management>
- QwenWork Hooks：<https://www.alibabacloud.com/help/en/qwenwork/hooks>
- QwenWork 专家套件：<https://qwenwork.cn/docs/desktop/expert-kits>

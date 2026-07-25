# 请示/申请叶子拆分预注册

## 目标与固定基线

- 固定基线：`faba4c1f410b3007d60671b3d2ead6d78a2ea8a4`
- 研究分支：`codex/1.5.25-candidate-request-leaf-v1524`
- 目标：减少请示、申请起草阶段无关文种规则的加载量，同时保持现有事实边界、文种功能、格式、输出模式和直接使用成本。
- 本候选只代表独立减负研究，不改版本号、不发布。

## 精确 diff

1. 新增 `references/genre-playbook-request.md`，采用现有独立文种叶子的简短使用约定，并原样迁移 `genre-playbooks.md` 中“请示/申请”的适用、骨架、风险和补充读取四条规则。
2. 从 `genre-playbooks.md` 删除“请示/申请”目录项和对应区块；其余文种规则不改写。
3. 调整 `SKILL.md`：
   - 普通请示、申请需要常规或完整骨架时，直接读取新叶子；
   - AI 算力请示在 `ai-compute-docs.md` 基础上叠加新叶子；
   - 采购、可研、审查、公告、通知、函、方案等仍读取原通用 playbook。
4. 更新 reference 表、确定性路由测试和发行镜像。

## 起草加载对照

| 场景 | 改前 | 改后 |
| --- | --- | --- |
| 普通请示/申请 | `SKILL.md` → `information-selection.md` → `genre-playbooks.md` | `SKILL.md` → `information-selection.md` → `genre-playbook-request.md` |
| AI 算力请示 | `SKILL.md` → `ai-compute-docs.md` → `genre-playbooks.md` | `SKILL.md` → `ai-compute-docs.md` → `genre-playbook-request.md` |
| 其他通用文种 | `SKILL.md` → `genre-playbooks.md` 对应小节 | 不变；通用文件仅删除请示区块 |
| 定稿复核 | 按既有触发条件读取复核材料 | 不变 |

## 明确不修改

- 不修改信息选择、事实锚、P0 边界、ANTI-AI、段内公式和篇幅预算。
- 不修改任务卡、改稿模式、用户模板、Word 交付、复核顺序和输出模式。
- 不修改检测器、正则、脚本门禁、FSM、修改次数、回退方式和发布链。
- 不新增文种特例，不改写现有请示规则措辞，不顺手整理其他文件。

## 验证

### 工程门

- 全量 `unittest`
- Promptfoo smoke
- 固定基线确定性消融
- `quick_validate`
- canonical 与发行镜像一致性
- `git diff --check`

工程门失败时停止真实写稿。

### 真实写作 A/B

固定三题：

1. F06：采购 4 台办公电脑，预算 24000 元，经费从年度信息化预算列支；缺主送、申请单位和成文日期。
2. F13：以当前底稿为唯一事实主线修改请示，检查旧金额、旧主送、旧服务期和旧结论是否回流。
3. T4：AI 算力租赁请示，月 8000 万 Token、峰值并发 40、12 个月、60 万元，并写明 SLA、数据安全和验收。

Candidate 与固定基线使用同模型、同 thinking、逐字一致的自然语言原始任务，各取首个技术有效输出，不补抽。写手和匿名评审分离；先检查事实、数字、主体、状态、文种、格式和输出模式，再比较重复解释、机械化程度和直接修改成本。

True No-Skill 仅在物理隔离且运行证据确认没有读取任何 Skill/reference 时纳入；无法确认时记为 `unavailable`，不以“不要读取 Skill”等提示伪造对照。

## 验收

- 三题均无 Candidate 独有的事实、数字、主体、状态、文种、格式、输出模式或 P0 回退。
- 任一题 Candidate 的直接修改成本不得高于固定基线；减负实验允许持平。
- 实际路由必须读取新叶子，T4 还须读取 AI 算力专项叶。
- 满足工程门和真实 A/B 后才可合并；否则保留证据并冻结本候选。

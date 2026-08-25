# v1.6.16 本地候选基线

日期：2026-08-25。

状态：`READY_LOCAL_CANDIDATE / NOT_PUBLISHED`。本文件绑定本地发行候选；正式发布回执完成前，不表示 GitHub、SkillHub.cn 或 ClawHub 已存在 v1.6.16。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.15^{commit}=762b84d49c35cb956ce464fa8aab5dd08f1ad113`。
- 本轮内容基线：`main@ec7709fff0ac7e821b3b26a4f8eded182fc48956`。
- 本地发行分支：`codex/release-v1.6.16`；目标版本：`1.6.16`。
- 公开产品增量只包含已在 main 清洁合入的 `OC-003`：算力可研的未决状态、条件性建议边界和用户点名完整性审查窄路由。没有新增 Hook、自动测算门、程序模板、数值阈值或统一篇幅门。
- `WR-014-R5` 采购状态层级只登记当前产品能力和判定边界，没有修改 Skill、reference、Hook 或 adapter；短稿、完整日期和讲话稿实验也不冒充本版产品增量。
- `codex/paid-outline-review` 的提纲与红头 DOCX 能力不反向进入公开版。ClawHub 继续使用 `packages/openclaw/skills/chinese_official_writing/` 的无 Hook 普通包。

## 真实写稿依据

- `OC-003-R2` 把“可形成条件性建议”与“不得升级为已启动、已确定或必须履行的程序”分开；候选通过正向建议、状态升级反例和未决条件反例。
- `OC-003-R3` 最终五个便宜 provider 5/5只读取入口与可研细查叶，仍完成已有数据核算、缺项影响解释，并覆盖成本比较、技术指标、验收主体和依据四项点名核对。
- Grok 4.6 与 Kimi K3 只承担合并后的独立冷审，不计普通写稿票；两份有效终判均未发现事实或状态阻断。

## 发布坐标与边界

- GitHub：`gongyu0918-debug/chinese-official-writing-skill`，tag 与 Release 名均为 `v1.6.16`。
- SkillHub.cn：现有 `skillId=70149`、坐标 `@user_f3d82da7/chinese-official-writing`、slug `chinese-official-writing`、展示名“中文公文写作”；清洁包允许包含默认关闭的可选 Hook，不含 `agents/openai.yaml` 和付费实现。
- ClawHub：owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`；发布包必须为33文件且 Hook、`agents/openai.yaml`、付费提纲和红头实现命中均为0。
- 小红书 Red SkillHub 及其他平台不在本轮范围。

## 已完成发布门

- 聚焦边界、包构建、状态台账、仓库可达性和 `OC-003` 分层测试：`97/97` 通过。
- 全量测试：`python -B -m unittest discover -s maintenance/tests -p "test_*.py"`，`693/693` 通过。
- 确定性真实用户 prompt 消融：上一版 `v1.6.15` 与当前候选均为 `111/111` 通过，无起草或改稿路由回退。
- stub smoke：`20/20` 通过，Skill 选择 `10`、baseline 选择 `0`、平票 `0`、无效样本 `0`，裁判一致率 `1.0`；Eval ID 为 `eval-zUl-2026-08-25T05:26:35`。该结果只验证发布烟测，不冒充真实模型写稿结论。
- canonical、Agent Skills、Qwen Code、Hermes 四个目录均通过 `quick_validate.py`；跟踪文件中 `135` 个 Python 文件可编译、`141` 个 JSON 文件可解析。
- `sync_adapters.py` 连续复跑前后 diff hash 同为 `4ce465cb8d606e047985679108bf040d0afa3d14`，镜像同步幂等。
- SkillHub.cn 清洁包为 `71` 文件，排除 `agents/openai.yaml` 与无扩展名 `LICENSE`，允许默认关闭的可选 Hook；本地清单指纹为 `731e406b27d7a85b754473e2fdbd298ba386ba43472d65a5d0e9c8bd562ff3cd`，`publish --dry-run` 返回 slug `chinese-official-writing`、version `1.6.16`。
- ClawHub 普通包为 `33` 文件，Hook、`agents/openai.yaml`、付费提纲、红头实现命中均为 `0`；本地清单指纹为 `ee1d154e8b454dcb2df579af9d2959fa6fea02556751fb810d4ca9a7f992e420`。
- 两个包体指纹算法一致：按相对 POSIX 路径排序，对每个文件依次写入 `path + NUL + bytes + NUL` 后计算 SHA-256。
- `git diff --check` 通过，仅有 Git 对现有换行转换的提示。

正式外部写入前仍须把候选提交快进到 `main`，核对远端 main/tag 无漂移，并用最终产品提交完成 ClawHub `source-commit` 绑定 dry-run。正式发布结果与平台回读另写发布回执，不由本地候选证据预断。

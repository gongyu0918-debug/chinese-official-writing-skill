# 1.5.26 发布证据

## 范围

1.5.26 以 `v1.5.25=776a32e60f7bb0afe37f439b2710b6d0b43d40e8`
为固定产品基线，只发布已经独立验证通过的请示/申请复核叶减载：

- 把请示、申请的既有细查规则从通用 `genre-checklist.md` 原样迁入
  `genre-checklist-request.md`；
- 只审不改或细查请示、申请时按需读取新叶；
- 起草继续读取既有 `genre-playbook-request.md`，审后改写才叠加起草叶。

信息选择、事实边界、文种功能、用户模板、篇幅预算、输出模式、复核顺序、
Hook、FSM、修改次数和回退链保持不变。本版没有合入联网来源、AI 算力、
采购审查、工作总结或 reviewer 元指令等未通过或未完成真实 A/B 的研究候选。

候选产品提交为
`f895117210b569494e65612d2f4491018cca4bdc`。版本面同步使用
`tools/sync_adapters.py`，canonical、五套发行镜像、OpenClaw 展示面和 Claude
插件均为 1.5.26。

## 可复核净收益

| 路径 | 1.5.25 | 1.5.26 | 变化 |
| --- | ---: | ---: | ---: |
| `review-checklist` + 请示/申请文种细查 | 9707 字符 | 6750 字符 | -2957，约 -30.46% |
| 通用文种细查叶 | 3583 字符 | 3033 字符 | -550 |
| 请示/申请细查叶 | 不存在 | 626 字符 | 新增按需叶 |

迁移没有改写请批事项、行文关系、状态、结构或信息选择规则；请示/申请起草叶
在固定 1.5.25 与 Candidate 中内容哈希一致。

## 真实 A/B

固定 1.5.25 与 Candidate 使用三组自然任务，覆盖内部费用申请只审不改、正式
请示只审不改和请示审后直接改稿。每题使用逐字一致输入，各取首个技术有效
输出，不补抽；另按预注册规则对唯一软负项做一次同题噪声复验。

- R01、R02：Candidate 明确胜出，Candidate 为 PASS，Baseline 为 WARN；
- R03：Baseline 小胜，两稿均为 PASS；
- R03N 同题复验：Candidate 小胜，两稿均为 PASS；
- 八份输出的事实、数字、日期、主体、状态、文种、格式、输出模式和 P0
  硬边界全部通过。

R03 两次独立运行一胜一负，差异集中在轻微衔接和版式，没有形成稳定负项。
原始结论见 `candidate-request-review-leaf-result-20260726.md`，集成重放见
`request-review-leaf-integration-20260726.md`。本轮不重复生成 true No-Skill，
发布结论限于相对固定 1.5.25。

## 发布级工程验证

- `python -m unittest discover -s tests`
  - 结果：372/372，`OK`。
- `python tools/run_real_prompt_ablation.py --baseline-root <1.5.25-product> --baseline-label v1.5.25 --current-root . --out output\release-1.5.26-ablation`
  - 结果：Baseline 108/108，Candidate 108/108。
- `python <skill-creator>\scripts\quick_validate.py chinese-official-writing`
  - 结果：`Skill is valid!`。
- `PROMPTFOO_PYTHON=<bundled-python> python evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`
  - 结果：20/20，0 failure，0 error；skill 10、baseline 0、tie 0，judge
    consistency 1.0。
- `python tools/sync_adapters.py` 与 `git diff --check`
  - 结果：镜像同步，diff 检查通过。

Promptfoo 在沙箱内先后尝试 Hermes、系统 Python 和 bundled Python 路径时，
Node 均报 Python 不可用，20 项没有进入产品逻辑；在获批的系统权限环境用同一
bundled Python 复跑后通过。前三次记为环境噪声，不计为产品失败或通过。

## 发行包预检

- ClawHub dry-run：`status=would-publish`、26 个文件、fingerprint
  `baf03fdfa4adc2e1f9aef68b2ba5aac599e0a4a8cd56639cf3948a00b2b5f3fc`；
- skillhub.cn dry-run：`dryRun=true`、`slug=chinese-official-writing`、
  `version=1.5.26`，临时包 25 个文件；
- 两个发行面均不携带 `delivery-review-gate.md`、`review_gate.py`、
  `gate_stop_hook.py`、tests、output、缓存或 `.pyc`。

首次 ClawHub dry-run 被本机失效代理 `127.0.0.1:9` 拦截，清空代理后同参数
通过。首次 skillhub.cn dry-run 因 Windows PowerShell 给临时包 `SKILL.md`
写入 UTF-8 BOM 而拒绝，改为无 BOM UTF-8 后通过；两项均为发行环境或临时包
编码问题，没有修改技能产品。

## 剩余风险

- 新增真实写作证据集中在请示、申请的复核和审后改写，不能外推为全部文种或
  复杂长稿复核；
- 本轮没有新增 true No-Skill，对无 Skill 的质量比较继续使用既有公开证据；
- reviewer 元指令减载和竞品启发的 Word/GB/T 复核迁移仍在研究线，不进入本版；
- 平台发布、公开传播、审核和扫描状态在正式提交后分别补录，不以一个字段替代
  其他字段。

## 发布状态

- 产品发布提交：`50afb5ffd9be88327ad1b4dd25d87c1377d39de9`；
- annotated tag object：
  `f817ce5f4b148ebd35fdd0726f8cc8f5de6bb24d`，解引用到产品发布提交；
- GitHub `main`、`v1.5.26` 和正式 Release 已公开，Release 为非 draft、
  非 prerelease：
  <https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.26>；
- ClawHub 只正式提交一次，回执为 `status=published`、
  `versionId=k97bcqx1pbcswrsynm520xbb7d8baqsp`、26 个文件、fingerprint
  `baf03fdfa4adc2e1f9aef68b2ba5aac599e0a4a8cd56639cf3948a00b2b5f3fc`。
  提交回执和首次公开查询仍显示 latest 为 1.5.25，精确查询 1.5.26 返回传播
  中的 `Version not found`；公开 1.5.25 的 moderation 为 `clean`，不能据此
  推断 1.5.26 的审核结果；
- skillhub.cn 只正式提交一次，回执为 `skillId=70149`、
  `versionId=173218`、25 个文件、fingerprint
  `421f6f9fe53ef38bdd002ecbe648acc75de312663dea1ccbe2150e6645f1296f`、
  `tags.latest=1.5.26`；review、security scan 和 content audit 均为
  `pending`。首次公开搜索仍显示 1.5.25；
- 两家商店的异步传播只记录现状，不触发重复发布。

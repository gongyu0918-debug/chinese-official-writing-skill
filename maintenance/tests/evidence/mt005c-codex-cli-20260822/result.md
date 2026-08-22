# MT-005c Codex CLI 隔离 A/B 结果

## 结论

`INITIAL_PASS_SUPERSEDED_BY_FULL_GATE`。

候选在 Codex CLI 的两个正向题均自主读取本臂精确 Skill，社媒负向没有读取；三稿均无预注册硬失败。基线两个正向也触发，但社媒负向误读完整公文 Skill。该阶段结果曾支持进入合并候选，不支持继续删除其他文种枚举。

合并前660项全量门随后发现193字 description 缺少 P058 要求的显式“学校”；196字最小回补虽保持2项正向触发和1项社媒不误触发，却在两份正向真实稿中新增安排或升级“可报”状态。最终状态已被[合并前跟进](../mt005c-school-repair-followup-20260823.md)取代：恢复204字，不接入 MT-005c。

## 隔离与有效性

- CLI：`codex-cli 0.144.6`；模型：`gpt-5.6-terra`；reasoning：`medium`。
- 两臂各有61个 Skill 文件，除 canonical `SKILL.md` 的 description 单行外逐文件 SHA-256 相同。
- baseline Skill SHA-256：`daefec94d57596012680f658f2e68a746e433df48a389293108b7e010ad408be`。
- candidate Skill SHA-256：`4b91986c75dbd55cdf196ba5d37677da3195c2b9055383def1f1038a0ca221ee`。
- CLI 临时配置禁用了 `C:/Users/admin/.agents/skills/chinese-official-writing/SKILL.md` 和 `C:/Users/admin/.codex/skills/chinese-official-writing/SKILL.md`；六份 trace 均未出现用户级同名路径。
- [OpenAI 官方 Skill 文档](https://developers.openai.com/codex/skills)说明 Codex 同时扫描 repo 与 user Skill、同名 Skill 不合并，并按 description 隐式触发。本轮据此把唯一活动 Skill 放在临时仓库 `.agents/skills/`。

首次自动汇总把 JSON command 中的双反斜杠归一成双斜杠，错误地把四个正向读取记为缺失。检查原始事件后改为先解析 JSON command、再折叠路径分隔符；只重新分析原有六份 trace，没有重跑模型。最终正文 SHA-256、耗时和 token usage 均未改变。

## 路由、写稿和观察 usage

| 题目 | baseline | candidate | 写稿核对 | observed input tokens |
| --- | --- | --- | --- | ---: |
| 行业协会通知 | 触发 | 触发 | 候选完整保留“每家可报1名”；基线把“可报”改为“请安排”，属于基线状态增强；两边其余硬事实完整 | 132789 / 123754 |
| 学校系统通知 | 触发 | 触发 | 候选179字，加入由上线与试用直接支持的一层准备目的和体验动作；未把评估写成已完成。基线133字，事实状态完整 | 106479 / 61748 |
| 小红书招新 | **误触发** | **不触发** | 两份社媒文案均不用于评价公文 Skill 写稿质量；候选没有加载公文规则，边界正确 | 36823 / 32301 |

token 数是 CLI 每次 `turn.completed` 的观察值，包含初始上下文、缓存、工具回合和模型自行选择的 reference，不能当作11字 description 的纯节省或账单数字。可归因事实是：基线社媒负向读取了完整 `SKILL.md`，候选没有读取；该次 observed input tokens 相差4522。description 本身只减少11字，主要收益是减少常驻入口文本并改善边界路由，不把单次缓存差异夸大为稳定节省。

## 风险

- 这是单模型、每题每臂一次的 CLI 补充；总体质量仍以先前五路三十份有效稿为主。
- 候选学校稿的“为做好系统上线准备”“组织相关人员登录体验”按当前规则属于材料和常识直接支持的一层目的/动作，记 `WARN_ACCEPTED`，不等于新增强制流程。
- 候选社媒稿加入了材料外活动细节，但该臂没有触发公文 Skill，不能归因成 MT-005c 产品回退；仍作为普通模型写社媒时的观察风险保留。
- CLI stderr 出现远端推荐插件目录429/500警告，不影响六次 `return_code=0`、本地 Skill 精确读取或最终正文。

## 实际命令

```powershell
codex --version
codex exec --help
python -B -m py_compile maintenance/tests/evidence/mt005c-codex-cli-20260822/run_eval.py
python -B maintenance/tests/evidence/mt005c-codex-cli-20260822/run_eval.py
python -B maintenance/tests/evidence/mt005c-codex-cli-20260822/run_eval.py --reanalyze
```

固定题面、顺序和自动检查见 `cases.json`；六份正文见 `raw-finals.md`。未提交运行输出位于 `output/mt005c-codex-cli-20260822/`。

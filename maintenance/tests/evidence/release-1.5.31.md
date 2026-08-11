# 1.5.31 发布证据

## 范围

1.5.31 以 `v1.5.30=176f1eb64e5ff8d3d557e29d18c2be9e2d15dcc4` 为固定
发布基线，只发布两项已验证原子：

- 工作总结、工作要点和周报在材料已经给出下一步、未来安排或改进计划时，
  可用前文已有问题、数据和工作基础说明对象、目的或衔接；
- 从写作入口移除维护者专用 CI 调用示例，脚本严格模式和退出码能力保留。

计划内展开继续锁定主体、程序、期限、数量和结果强度，不授权新增任务、责任、
承诺或材料外事实。本版不改变任务路由、reference 加载条件、复核顺序、输出
模式、修改次数、Hook、FSM 或回退方式。

会议培训/信息传达与决策会议分流候选完成隔离真实测试后判为 MIXED：路由可
触发并能减少上下文，但一题相对固定基线增加编辑成本，未进入本版。新闻消息和
新闻评论专项叶不在本轮范围。

## 发布前验证

- `python -m unittest discover -s tests`：395/395，`OK`。沙箱内首次运行因
  Windows ACL 拒绝 `tempfile` 二级写入产生 149 个环境错误；在沙箱外按同一
  入口完整通过。
- `python evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：
  20/20，0 failure，0 error，judge consistency 1.0，eval id
  `eval-n5v-2026-07-31T07:08:28`。沙箱内首次运行因 Node 无法启动已安装
  Python 产生 20 个环境错误；在沙箱外按同一命令复跑完整通过，首次结果不计为
  产品失败，也不冒充有效样本。
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.30> --baseline-label v1.5.30 --current-root . --out output/release-1.5.31-ablation`：
  固定 1.5.30 为 110/110，Candidate 为 110/110。
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：
  `Skill is valid!`。
- `python tools/sync_adapters.py`：canonical 与五个发行镜像同步；重复运行没有
  新增内容漂移。
- `git diff --check v1.5.30..HEAD` 与工作树 `git diff --check`：通过。

## 真实写稿与独立复核

组合验证复用一项自然周报任务及既有单原子稿，不重复生成基线或 No-Skill。
技术有效的 Candidate 稿保留全部数字、日期、主体、办理状态和四项后续安排，
未出现保护性外扩、空稿或循环。独立复核认为组合稿有一处可删的泛化过渡，
但不构成明显更难直接使用；该单次软差异未达到共性风险门槛，按生成波动记录。

两稿均明显低于任务中的“700 字左右”，属于共同剩余风险。本版只验证已给计划
的有限展开和入口减负，不把单次真实 sanity 宣传为普遍质量领先，也不宣称已经
解决篇幅不足。详细记录见
`atomic-update-v1530-integration-result-20260731.md`。

## 发行包与平台状态

- GitHub：产品提交为 `e8c077cb1d6c6fe02bec71634140793aeeba5a5b`；
  annotated tag object 为 `04f8928d6bb7794291ef83b33183c59c837141fb`，
  tag 解引用提交与产品提交一致。正式 Release 已公开：
  `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.31`，
  `draft=false`、`prerelease=false`。
- ClawHub：27 文件包排除 Codex 门禁说明和两项门禁脚本；正式提交一次，
  回执为 `status=published`、`versionId=k97f7p972f02xbdcfr3bfk3gjd8bjj7w`、
  fingerprint
  `e0f18a01a9f2c190db9594810883ef4810af0d3a570019a3cd75b54c32b8fb57`。
  首次公开查询的 `latestVersion.version` 和 `tags.latest` 仍为 1.5.30；
  该公开旧版 moderation 为 clean，不据此推断 1.5.31 的扫描状态，也不重复
  提交。
- skillhub.cn：26 文件清洁包按 Git 跟踪白名单构建，排除
  `agents/openai.yaml`、Codex 门禁说明和两项门禁脚本，并加入平台
  `_meta.json`。正式提交一次，回执为 `skillId=70149`、
  `versionId=184901`、fingerprint
  `ce67059c80fa6c3cd94295419adbcd5433138fb5aa074ae969bb220a57c08d13`，
  `tags.latest=1.5.31`；review、security scan 和 content audit 均为
  pending。首次公开搜索仍显示 1.5.30，按异步传播处理，不重复提交。
- 小红书 Red SkillHub 不在本次发布范围。

平台提交、公开 latest、审核、扫描和 provenance 分别核验；公开 latest 延迟
不触发重复提交。

## 剩余风险

- 计划内展开只覆盖材料已经给出的计划、未来安排和改进事项，不能保证所有材料
  都达到用户目标篇幅。
- 分项周报仍可能产生少量“推进”类泛化过渡。
- 会议培训/决策分流候选只有上下文减载收益，语言质量未达到不劣于固定基线，
  本版未吸收。
- 新闻消息、新闻评论、通用篇幅机制和新增门禁均留待独立验证。

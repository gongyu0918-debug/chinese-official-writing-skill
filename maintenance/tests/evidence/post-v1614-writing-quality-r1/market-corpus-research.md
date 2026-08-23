# 2026-08-23 在线竞品与官方语料研究

本文件只记录方法级观察，不复制第三方文字、模板、代码或示例。下载量只表示传播，不作为写稿质量证据；是否借鉴必须经过本仓库真实写稿。

## 在线检索面

SkillHub.cn 当日使用公开搜索 API 检索：`公文、公文写作、正式材料、会议纪要、新闻稿、报告、通知、请示、讲话稿`。ClawHub 使用 CLI 搜索 `公文、会议纪要、新闻稿`，并对候选执行 `inspect --json`。未安装、未运行第三方 Skill；只把压缩包下载到 `output/current-verification/20260823-market-refresh-r1/` 做只读检查。

### 当前代表项

| 平台/slug | 当日可见版本与规模 | 可借鉴原子 | 不借鉴/风险 | 许可观察 |
| --- | --- | --- | --- | --- |
| SkillHub `zhaohui-yang-official-document-drafting-100` / ClawHub `official-document-drafting` | SkillHub 2026-08-22 新建，v1.0.0，包内104文件；ClawHub 当日814 downloads | 文种目录与共享事实边界分层可作架构对照 | 固定句数、占位符进正文、默认补结构和大包体会增加过拟合/加载成本；不是新的写稿方法 | README 称 MIT，但 SkillHub 下载包未见独立 LICENSE，不能复制实现 |
| SkillHub/ClawHub `gov-report-writing` | SkillHub v1.4.0，10文件；ClawHub 当日494 downloads | 用户提供旧稿时抽取“标题节奏、段落密度、数据呈现、词语偏好”的风格指纹；长报告分节起草后做全局一致性检查 | 固定阈值、默认 Word、机械禁词、固定改动比例和问题轻写均不采用 | ClawHub 元数据 MIT-0；SkillHub 包许可表面不完整，仍只借方法 |
| SkillHub `lls-leader-speechwriter-expert` | v1.1.1，4文件 | 讲话任务卡、讲话类型区分、主张—证据—听众意义映射、实际朗读时长；重要句可独立成段 | 不复制话术、提纲或模板，不把现场感染力变成事实扩写 | CC-BY-NC-SA-4.0，只作方法研究 |
| SkillHub `event-news` | v1.0.0，4文件 | 发布者角色和素材优先级可作反例校准 | 固定4/6段、固定领导顺序、固定意义/未来段会诱发成效和后续安排；当前 Skill 的事实边界更安全 | 下载包未见清晰许可，不复制 |
| SkillHub `meeting-minutes-tencent` | v1.0.2，64文件 | 单一中间 JSON 避免不同输出重解释；`confirmed/inferred/unresolved` 与证据位置绑定；正式标准、候选标准、一次性安排分开 | 多格式渲染、表格和平台胶水不是当前写稿优先项 | SKILL 声称 MIT；仍只借方法 |
| SkillHub `meeting-v2` / `hyjy2026` | 2文件 / 6文件 | 会议类型路由可作为题型枚举参考 | 强制每项补个人负责人、准确日期和交付物，容易造事实 | 下载包未见清晰许可，不复制 |
| ClawHub `meeting-decision-receipt` | v1.0.1，当日388 downloads | 已定、暂定、提议、明确承接、未确认承接及短证据绑定，和当前 `WR-010` 方向一致 | 固定双版本、固定开结尾、首屏数量和发送确认不适合直接公文正文 | MIT-0 |
| ClawHub `meeting-minutes-craft` | v1.0.0，当日353 downloads | 按周会、决策会、复盘、研讨等会议用途选择视图 | HTML、颜色、搜索和行动项筛选属于展示工程，不能证明会议结论准确 | MIT-0 |
| SkillHub `jiangai` | 平台 v1.0.3，包内自报2.0.0，2文件 | 只有“观察句长和段落节奏”这一通用方法可作对照，当前 Skill 已有 | 强制反问、故意省主语、数字不准确、注入“人类瑕疵”和固定比例与公文事实安全冲突，不采用 | SKILL 声称 MIT |

### 真正新增且值得写稿验证的原子

1. 讲话任务卡：讲话人、议程环节、听众、时长、中心主题、听众应理解/办理事项、必提和敏感边界。
2. 讲话类型与节奏：部署、总结、调研、致意、承诺、主旨演讲不能共用一套骨架；实际朗读时长、称呼重置和关键句独立成段需要保护。
3. 会议规则状态：正式规则、候选规则、一次性安排分别保持；证据侧车只在正文确有混淆时继续。
4. 长报告风格指纹：只从用户给定历史材料提取结构和表达习惯，不带回旧事实；分节写作后检查全局事实、标题与密度一致性。

## 官方语料结论

### “口径”不是禁词

- [国家统计局2026年夏粮产量公告](https://www.stats.gov.cn/sj/zxfb/202607/t20260710_1964090.html)把“统计口径”与包含类别、调查范围和方法相邻放置。
- [国家统计局指标范围解释](https://www.stats.gov.cn/xxgk/jd/sjjd2020/202401/t20240117_1946672.html)用“口径不同”解释全社会用电量和规模以上工业发电量的纳入范围差异。
- [国家税务总局政策答复](https://www.chinatax.gov.cn/chinatax/n810219/n810724/c5236041/content.html)、[国家外汇管理局全口径跨境融资说明](https://www.safe.gov.cn/hebei/file/file/20180424/c17bffbd6582428f8dfa9835e0ce1562.pdf)也在明确对象与边界时使用“口径”。

结论：减少的是无对象、无范围、无依据的“统一口径”，不是删除统计、核算、测算、验收、审计等必要概念。不同对象的必要“口径”不能按裸词计数判重复。

### 行业词和 AI 高频词要看机制

- [全国哲学社会科学工作办公室“人工智能+”文章](https://www.nopss.gov.cn/n1/2025/0512/c219544-40477936.html)在给出需求图谱、能力匹配、转化节点和平台机制后使用“赋能、闭环、场景、生态”。
- [中共中央社会工作部基层治理文章](https://www.zyshgzb.gov.cn/n1/2025/0619/c460636-40504195.html)把“闭环”具体写成提交、查询、处置和评价链条。
- [湖北省2026年场景清单](https://sjj.hubei.gov.cn/bmdt/tzgg/202604/P020260423539722658121.pdf)把“底座、闭环、场景”与技术组成、指标和适用对象相邻呈现。

结论：`赋能、闭环、底座、生态、场景、体系化` 可以是真实行业词。只有词串替代了主体、动作、节点、产物或指标时才算空壳；不能用禁词表冒充去 AI 味。

### 必要英文和缩写

- [西藏自治区政府转发的行政机关字母词审核通知](https://www.xizang.gov.cn/zwgk/xxfb/zbwj/201902/t20190223_63901.html)要求国际组织外文名称或缩写首次出现时注明准确中文译名，并强调规范译写。
- [工业和信息化部算力基础设施行动计划](https://www.miit.gov.cn/cms_files/filemanager/1226211233/attach/20238/1f932a10298244da844cacef2baa63c7.pdf)采用中文术语、英文全称和缩写并列定义。
- [北京人工智能政策](https://www.beijing.gov.cn/zhengce/zhengcefagui/202503/t20250325_4043893.html)、[网信办材料](https://www.cac.gov.cn/2026-04/10/c_1777558285804391.htm)及[泉州 DeepSeek 方案](https://xxgk.quanzhou.gov.cn/szb/zfxxgkml/yzdgkqtxx/202503/t20250321_3151117.htm)显示官方材料也会根据受众采用中文简称、`人工智能（AI）` 或保留产品英文名。

结论：需要首次出现与一致性规则，但不能机械要求所有缩写展开英文全称，更不能自造译名。产品名、型号、URL、代码、单位和用户已给标准写法要保留。

### 长报告和讲话

- [2025年政府工作报告](https://www.gov.cn/yaowen/liebiao/202503/content_7010168.htm)、[2026年最高人民法院工作报告](https://www.court.gov.cn/zixun/xiangqing/492921.html)、[2025年计划执行情况与2026年计划草案报告](https://www.npc.gov.cn/npc/c2/c30834/202603/t20260316_453271.html)、[2025年预算执行情况与2026年预算草案报告](https://www.mof.gov.cn/zhengwuxinxi/caizhengxinwen/202603/t20260316_3985331.htm)显示报告的结论位置和宏观顺序随用途变化，不能统一要求“专题报告先给结论”。
- [全国科技大会讲话](https://www.ncsti.gov.cn/kjdt/ztbd/qgkjsh/202406/t20240627_169540.html)与[全国民族团结进步表彰大会讲话](https://www.neac.gov.cn/seac/c103675/202409/1176712.shtml)使用历史/形势铺垫、称呼重置、功能性平行句群和长短段交替；这些结构不能因“排比、重复、单句成段”被机械去除。

结论：当前 Skill 能守事实、文种和基础论证链，但尚未证明长稿稳定。最先测试报告用途差异、一个控制论点下的段群、讲话任务卡/朗读时长和跨文种结构指纹，不先加段长门或 Hook。

## 只读 lint 审计

在 `main@b73f302c` 只读运行当前 `scripts/prose_lint.py` 逻辑，确认：

- 合法的 `不是……而是……`、`既要……又要……`、`一方面……另一方面……`、`综上所述`、`相关情况如下` 可在 `--fail-on medium` 下误失败。
- 已给 `测算口径、测算公式、单价×数量、计算如下` 同段可产生4个 medium；四个语义不同的“统计/核算/验收/审计口径”仍会触发词频提示。
- `经专项检查和专家评估，未发现重大隐患` 仍可被误报，现有例外只覆盖更窄句形。
- 短而具体的三项要求可因每项不足30字被判 medium，三条较长空话反而可能绕过该项。

因此本轮不先改 lint。先看这些误伤是否会实际影响成稿或审稿选择，再把单次合法句式降级、同对象语义去重、复合检查依据和语义锚替代字符数分别做成工程原子。

## 实际命令

```powershell
Invoke-RestMethod 'https://api.skillhub.cn/api/v1/search?q=公文'
Invoke-RestMethod 'https://api.skillhub.cn/api/v1/search?q=会议纪要'
Invoke-RestMethod 'https://api.skillhub.cn/api/v1/search?q=讲话稿'
clawhub search "公文"
clawhub search "会议纪要"
clawhub search "新闻稿"
clawhub inspect official-document-drafting --json
clawhub inspect gov-report-writing --json
clawhub inspect meeting-decision-receipt --json
clawhub inspect meeting-minutes-craft --json
rg -n "口径|赋能|闭环|英文|缩写|单句成段|讲话" chinese-official-writing maintenance/specs maintenance/tests
```

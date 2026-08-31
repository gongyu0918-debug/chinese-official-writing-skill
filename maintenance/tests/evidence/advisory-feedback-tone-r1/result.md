# WR-025 / WR-008b 建议反馈与 Word 标题版式结果

日期：2026-08-31。

状态：`R3_SELECTED_ENGINEERING_VERIFIED / R4_R5_R6_TERMINATED / NEXT_VERSION_CANDIDATE / NOT_MERGED`。

## 边界

- 固定基线为 `main@a6764b7e61c5939c3dd098d556bf3e8d36a298a3`；已发布的 v1.6.22 和本地冻结的 v1.6.23 候选均不含本原子。
- 选定产品语义来自 `10c00a10`：新增合作性意见建议专叶，直达路由只覆盖提交给政策制定、审核、平台建设运营或材料起草方的意见建议、建议反馈和优化建议；正式下行指导、监督检查、安全整改、审计和纪检建议仍保持原权力关系。
- 当前分支已把选定语义同步到 Agent Skills、Qwen Code、QwenWork、Hermes 和无 Hook OpenClaw 包；没有修改 Hook、description、版本号、付费分支、发布 tag 或平台状态。

## 公开样本与源文件校准

- 公开样本显示，合作性建议通常先交代既有工作或制度背景，再以“供研究参考”等低强度表达提出具体事项；问题判断仍可明确，但不能把建议方写成已作出认定、允许、豁免或上线决定。参考：[重庆人大建议示例](https://www.cqrd.gov.cn/site/article/1211408846747963392/web/content_1211408846747963392.html)、[北京人大意见建议](https://www.bjrd.gov.cn/fwhd/bjrdzz/2025n/bjrdzz202512q/yjyts202512/202512/t20251230_4378013.html)、[中央纪委国家监委问答](https://www.ccdi.gov.cn/hdjln/nwwd/202106/t20210610_142282.html)。
- 对话所附算力补贴 DOCX 的源文件审计见 [`source-docx-audit.md`](source-docx-audit.md)：正文共有15处`（一）小标题。正文……`接排形态，未使用标题样式；主标题 OOXML 未见显式首行缩进值，但也未显式清零，无法据此否定用户观察到的模板继承风险。
- 候选因此只规定：真实并列层级标题独立成段、末尾不加句号、正文另起；普通段首题和编号正文句不机械拆分。正式 DOCX 主标题居中并显式清零首行、左、右缩进。未生成或渲染新的最终 DOCX，不声称已经完成视觉交付验证。

## 五家 R3 真实写稿

模型均使用仓库登记的低成本写稿路线，思考强度为 `max`：Alibaba Token Plan 2、Alibaba Token Plan、Ollama Cloud DeepSeek V4 Flash 0731、OpenCode Go DeepSeek V4 Flash、MiniMax M3。三题分别为长篇算力补贴意见建议、多处置主体短反馈、Word 小标题修复。

| 题目 | 有效性 | 可归因结果 |
| --- | --- | --- |
| 长篇算力建议 | 5/5候选有正文；Alibaba1基线只交过程句，故4组可比 | 4/4可比稿的问题标题均由5项收为3—4项；建议标题3/4由9项收为4—7项，MiniMax保持9项。五份候选均保留`1亿`、`6万余条`、`30万条`等锚点且候选硬失败为0。 |
| 多处置主体反馈 | 4组可比；MiniMax基线无终稿，候选又带代码围栏和材料外“近期、企业普遍反映”，该对无效 | 4/4有效候选都保留线上办理便利这一已给事实，区分审核部门的材料认定权与平台运营方的功能建设权，并保持“尚未形成调整决定”。合理的衔接建议不按外扩判失败。 |
| 标题修复 | 5/5可比 | 基线5/5均为`（一）小标题。正文`接排；候选5/5改为标题独立成段、无句号、正文另起，数字和未决状态均保留。 |

R3 的读取回执也如实保留：长篇题3/5、多主体有效题2/4、标题题4/5实际读取新增专叶。没有读取专叶的样本仍可能仅凭主入口和既有规则完成部分目标，因此读取次数不冒充质量证据；该差异作为宿主自主选读的残余风险保留。

## 后续最小尝试

- R4 只在专叶增加“只留一条代表事实链、不得用一二三重展旧项、总量须明显收束”。OpenCode由2719字符降至2406字符，但 Alibaba2 由2384字符回升至2687字符且建议项增至7项；没有跨 provider 共同增益，已恢复 R3 产品字节，状态 `TERMINATED_MIXED_REGRESSION`。
- R5 只把“精炼时先归并”前移到主入口。Alibaba2为2497字符；OpenCode为2826字符并泄露过程说明。该主入口重复没有共同增益，状态 `TERMINATED_DIRECT_DELIVERY_REGRESSION`。
- R6 改为更短的“有据礼貌铺垫 + 同因同权责同路径归并”主入口句。两家四份真实稿均有效，但长稿建议仍为6/7项；多主体稿分别新增“建议反馈正文如下”包装和整段路由、自检说明。该句已回退，状态 `TERMINATED_NO_COMMON_GAIN`，不扩大五家。

上述终止只否定相应主入口重复和叶内加码，不否定建议反馈专叶。选定 R3 已解决目标中的关系语气、处置权、共性问题归并和小标题版式；建议分组仍有模型方差，但没有候选独有事实、状态或指令硬回退，不以固定三条或固定字数进一步强压。

## 工程验证

- `python -m unittest maintenance.tests.test_advisory_feedback_leaf`：4/4通过。
- `python -m unittest maintenance.tests.test_skill_boundary`：80/80通过。
- `python -m unittest maintenance.tests.test_skillhub_package_builder`：3/3通过。
- Skill Creator `quick_validate.py`：canonical、Agent Skills、Qwen Code、QwenWork、Hermes均通过。OpenClaw包有仓库既有的`category`扩展字段，通用 validator 不接受该字段；其镜像一致性、MIT和无 Hook 边界由仓库单测覆盖，不记为本候选回退。
- `git diff --check`：通过。

## 终态与剩余风险

- `WR-025a` 有据合作性开场与处置权绑定：`SELECTED_ENGINEERING_VERIFIED`。
- `WR-025b` 共性问题与建议归并：`SELECTED_WITH_MODEL_VARIANCE`；已有4家可比路线产生3家建议项收束、4家问题项收束，不以MiniMax单路保持9项否定整体能力，也不继续堆规则。
- `WR-008b` 并列小标题与 DOCX 主标题缩进：文本修复 `SELECTED_ENGINEERING_VERIFIED`；实际 DOCX 渲染仍未验证，不把文字规则冒充最终 Word 视觉结果。
- R4、R5、R6 均已 `TERMINATED`，无活动 `HOLD`。当前分支未合入 main、未推送、未发布；是否进入 v1.6.24 由后续授权决定。

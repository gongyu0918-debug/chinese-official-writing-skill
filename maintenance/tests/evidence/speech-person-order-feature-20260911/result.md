# 开场称谓排序功能：准入与本地合并

结论：作为新增功能纳入。8对真实写稿与4次独立单对冷审支持这一窄范围改动不劣于完整本地main，并在两组具体人物前置题上出现同向改善。它不以减载为准入要求；也不据此宣称整体写作质量已经全面提高。

## 交付边界

- 开发分支：`codex/speech-person-order-feature-20260911`，从完整main `dafc35f9aad594ac6cebf76bd4caf2e1b80a1ba8`拆出。
- 产品冻结：`72a1d4009716da73a07fd9f764e8e431c83e8f66`。仅新增`references/speech-person-order.md`及四个条件指针；已知正副、确认主宾、未知跨单位顺序、具体人物与泛称分清处理。主持介绍、邀请发言、座次及公文主送不随开场称谓自动重排。
- 工程适配：`05659a15358d9986bde8fa59d840cb6cf747bd9d`，同步五套镜像并更新索引新增一行的冻结断言，既有五条场景路由绑定保持。
- 2026-09-11本地main已从dafc快进至`53088553fab608e6fc4916286b0700f5a2263f10`纳入产品及工程，随后仅补维护证据。canonical树为`95443a0f702a0f31d0c7cdcc1b9896f0fbf3587e`。
- 首页仍7516个LF字符；references由44页增至45页，总计+820字符，其中新页432字符。未推送、移动tag、创建Release或提交平台版本；选择性发布v1.6.33不被改动。

## 真实写稿与误判裁决

16次写稿全为有效原生成稿，两条精确Alibaba Flash通道同题同配置max对照；不声称客户端配置即上游档位证明。5个排序候选实际各读新页1次；R10、一般呼语局部修改、正式函件3个候选均未读新页。两组精确编辑控制与基线字节一致。

4次独立A2 Max冷审全为有效JSON，原生工具清单为空且实际调用为0；结果为候选优选2、持平2。审者与写作者不是同一精确模型，匿名映射不进入冷审。其余4题由根任务核对，没有包装成独立冷审。两个此前已完成的通知可用性probe另存，不计入本功能对照，按用户澄清不继续单独验证模型。

根任务排除了把登记名单当礼宾次序、正常标题、是否逐字重述禁止项、普通敬称有无和合句介绍当硬错的误判。R10双方仍有无据扩写及过程说明，不能判两稿整体合格；这一既有问题未顺手扩大修复，也未靠冷审投票豁免。具体裁决见[root-adjudication.md](root-adjudication.md)。没有出现需确认的新规则硬负点，未追加消融或抽样到通过。

## 工程验证

实际命令和解释器见[engineering-result.md](engineering-result.md)：相关单测94/94、canonical及四个普通Skill根quick验证5/5、全量`-m unittest discover -s maintenance/tests -p 'test_*.py'`850/850通过（151.830秒），diff检查通过。产品与冻结72a1一致；后续证据文档不触发重复全量测试。

## 归档与本机状态

最终写稿归档：`F:/Workspaces/chinese-official-writing-skill-archives/experiments/speech-person-order-feature-20260911-final.zip`，SHA-256：`db1832e55c8a6a13500db9ffd8e8cc2e8898f1abd5df98989e6e08a92e83ea5f`。490份允许归档文件，ZIP491成员含不可变清单，覆盖冻结输入、16份writer、4份cold、2份已完成probe及必要宿主/配置/映射，源文件、目标文件及ZIP读回hash核对通过。首轮归档因误含Python缓存被废弃但保留，最终包不含这些缓存、home、auth或运行workspace。ZIP清单SHA为`f1afc1dfb337a7de3bb941def331725e02baa2c481875545bcfb77a95afbce60`。

本机复用项目规定的`sync_local_pro.py --config`完成安装，来源签名`46f6aea99845bcff8fe22a0391f77070286d0ab8ce4770e0326df34080251e53`，Pro版本仍0.4.15。安装版本、注册插件、Codex缓存三个位置各47份普通规则均与main提交的Git blob原字节一致，详见[local-install-result.json](local-install-result.json)。初次误用Windows工作树CRLF字节作基准的失败记录保留；已查明为行尾转换，改用提交对象精确比对，并未修改安装内容来通过核验。

宿主回执中的两个Hook为trusted且enabled；独立激活生命周期仍为`AWAITING_HOST_TRUST`、尚无首次事件。本轮未运行真实Hook，不将安装、信任状态或隔离写稿冒充Hook执行。没有为此再追加模型调用；本轮人物排序功能已通过隔离真实写稿验证。

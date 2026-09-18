# 常见场景原子修订：采用结果

本轮完成有边界的原子试验与组合验证，采用材料报送页、代表/委员答复的函路由、采购更正条款；撤去未证明额外收益的答复附加页。产品仅4个文件变化，SKILL.md和脚本未改。产品冻结提交3451a5e6，基线main@21f3de03，76个产品文件与冻结清单逐一一致。合并及本机同步结果另见closeout.json。

## 采用范围和收益

| 改动 | 最终处理 | 实稿依据 |
| --- | --- | --- |
| 多项材料、不同统计口径、分层汇总 | 新增material-submission.md，条件加读 | 扩大到资产盘点题后，两通道均正确落实责任、附件、时点/期间和多级期限；正文业务质量持平，实际读页字符分别从9917到9249、8107到5179。不是凭“各科室/各业务科室”判胜。 |
| 代表、委员个人答复 | 索引和函页明确落点，删除试验性附加页 | 最终三份答复候选主文种读取由3/3/2页变为1/2/1页；向上汇报仍读报告。原B1—B4有误加读、重复规则及具体细节扩写，未整体采用。 |
| 采购更正公告 | 补入原公告定位、理由与处理结果的关系 | 原子4对为2对候选较好、2对相当，优势包括更清晰的前后关系与组织；GLM回归再次看到基线混入后续履约、候选正确分置。规则有真实公告来源，非自设模板门禁。 |

静态规则字符从54208到54757，增加549字（约1%）。这是常见用途的小幅补强，不宣称产品静态减载；运行时部分路径减少无关读取。

## 实际验证

- 单轮原生写稿共68次、34对，覆盖各次原子方案及组合；通过isolated Codex CLI运行，两臂同题同通道同强度。写稿通道为alibaba-token-plan/qwen3.8-flash、command-code/deepseek-deepseek-v4.1-flash及补充ollama-cloud/glm-5.3-flash，均为high。全部技术有效，68次均成功执行draft_length和prose_lint；这只证明执行，不替代稿件判读。
- 最终精确产品冻结为7对、14稿（final-deepseek、final-qwen、final-broad-deepseek）。另有前一组合6对；它包含后来撤去的B页，单列证据，不混为最终候选样本。逐对裁定见[final-adjudication.md](final-adjudication.md)。
- 独立匿名审阅覆盖A、C、多轮、前一组合控制与最终7对；另做隔离规则冷审。保留裁判误报、主代理过严判断的撤回及一次审阅超时。审阅结果需对照原稿，未盲从裁判胜负。
- 1.x对2.0多轮能力另跑2条三轮链、2版，共12次原生调用，通过明确session ID续接。结构增删调序、主体联动、最新底稿延续、字段改值和空字段保留均有对应实现和实际执行。1.x有一次第三轮空字段顺序移位，2.0保留原顺序；见[multiturn-results.md](multiturn-results.md)和[multiturn-map.md](multiturn-map.md)。这一组基线是legacy/1.x@d561bf6b，2.0为main@21f3de03，不能混进本轮新页收益。

最终7对观察到：

| 汇总项 | 基线 | 候选 |
| --- | ---: | ---: |
| 实际返回的去重规则页字符 | 71751 | 58410（−18.6%） |
| 返回页数 | 58 | 51 |
| 未缓存输入tokens | 137826 | 119002（−13.7%） |
| 总输入tokens | 1414370 | 1239130 |
| 累计用时 | 707.59秒 | 548.74秒（−22.4%） |
| 用时中位数 | 80.78秒 | 61.95秒 |
| 输出tokens | 51906 | 40906 |

返回页计数依据工具实际返回内容，最终样本匹配页均完整返回；不是把文件名被提到当成已读。两臂脚本均7/7执行，不把候选多检查当成减载收益。模型缓存、服务负载、先后顺序和采样有影响，上述耗时与tokens是本组观察，不承诺普遍提速省费。

多轮组则是1.x 81.95秒、2.0 160.13秒，2.0六轮执行复核脚本而1.x未执行，存在真实检查成本，未获得速度优势。这一不利观察同时保留。

## 检查命令与证据

原生命令和参数在native/*/binding.json、calls.json及multiturn/binding.json、calls.json；原始交付在对应目录，输出轨迹位置和原字节哈希在artifacts.json或provenance.json。匿名包仅将本机文件链接替换为“本地稿件文件”，映射与原稿均可追溯。Git可能规范化文本换行，原始字节哈希指向记录中的output原件。

- `python -B maintenance/tests/evidence/scenario-atoms-20260918/run_eval.py ...`：各独立队列完成，34对技术有效；阶段快照及统计见execution-summary.json、phase-metrics.json。
- `python -B maintenance/tests/evidence/scenario-atoms-20260918/multiturn_eval.py ...`：12次原生连续会话完成；每条链session ID一致。
- `python -B maintenance/tools/audit_product_surface.py --root chinese-official-writing`：通过路径、产品表面及工程内容检查。
- `python C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing`：通过。
- `git diff --check`：通过。已撤附加页名在产品中无残留；脚本未变化；产品冻结清单76项与3451a5e6 Git blob一致，见product-verification.json。

未运行历史中文关键词、整句命中和标题计数式语义断言，也不以这些Python断言宣称写作质量。

## 限制与停止点

各科室等简称、部分/总括表达、正常日期、合理原因及拟议后续动作，按上下文实际语义判断。没有实际改变范围、责任、数量、期限或确定状态的，不判错。原先M1称谓胜负已撤回，见[a-adjudication.md](a-adjudication.md)。

仍有正文外冗余提示、两臂共有的落款占位、少量额外主叶读取，以及表述长短波动。最终7对未确认候选语义回退，不意味着覆盖所有文种或所有宿主。多轮未覆盖长篇Word样式等。B重复附加页已撤去，本轮不继续加新规则或无边界扩测；本地合并并同步后结束，不推送、不发布、不更新平台包。

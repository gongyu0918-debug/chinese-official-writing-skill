# R19 calculated：8次原生执行审计

本批金额与最终篇幅正确，但**未证明工具复算已落实**：4次 `review_rewrite` 的完整命令记录均没有执行 `4×420` 或等效算术；候选2次均已实际读到“可核算的数值用工具复算，并说明口径”。`draft_length.py` 计数字符、`prose_lint.py` 扫描文稿，都不能替代金额复算。

范围限于 [inspection.json](../../../../output/review-common-native-r19-calculated/inspection.json)、[binding.json](../../../../output/review-common-native-r19-calculated/binding.json)、8条 trace 及对应 final 文件；16个 trace/final 哈希均与 inspection 一致。binding 指向 c6f65014 和 calculated 候选。这里记录的是该次原生运行指纹（baseline `2dae894c…`、candidate `6e3cdd28…`），不冒充产品包指纹。未读取盲审 verdict，不评价两方偏好，未跑模型或产品测试。

## 审后改稿：执行与最终版本

下表字数由本审计从 final 的标题至日期独立提取，按非空白字符计数；金额口径是4把×420元/把＝1680元。该审计计算不计入模型执行证据。

| 运行 | 最终字数／金额 | 实际脚本链与输入版本 |
| --- | --- | --- |
| [m0 baseline](../../../../output/review-common-native-r19-calculated/m0-review_rewrite-baseline.trace.jsonl) | 124／1680元 | draft1 114；draft2 133→扫描；draft3 118→扫描；draft4 124→扫描。末轮为 item_17、item_18。各次为新文件，重复有版本变化；扫描通过没有掩盖低于下限，最终另稿达标。 |
| [m0 candidate](../../../../output/review-common-native-r19-calculated/m0-review_rewrite-candidate.trace.jsonl) | 123／1680元 | 首次864是 `UTF8.GetBytes` 数组被 `Set-Content` 写成数字文本，不能算864字真实稿。修复后131→扫描→同稿换 `gap-note-allowed` 再扫；删去“不增加配置数量”后123→扫描（item_19、item_20）。最后一次写入内容与 final 正文可逐字核同（仅统一换行）。 |
| [m2 baseline](../../../../output/review-common-native-r19-calculated/m2-review_rewrite-baseline.trace.jsonl) | 137／1680元 | `_draft_review.txt` 133→扫描；删除后重建，137→扫描（item_16、item_17），交付前删除临时文件。 |
| [m2 candidate](../../../../output/review-common-native-r19-calculated/m2-review_rewrite-candidate.trace.jsonl) | 131／1680元 | `.draft-chair.txt` 创建后131→扫描（item_14、item_15），再删除临时文件。 |

4次末轮均先计篇幅再扫描，计数证明末轮输入非空；未见后续正文修改事件。m0 candidate 可直接核同输入文本；另外3次 trace 的 `file_change` 只保存路径和操作，未保存补丁正文，因此只能确认最新已创建版本被两脚本检查、计数与 final 一致，不能据此宣称输入与 final 已逐字或逐哈希核同。所有读取 anti 页的动作均早于脚本调用；这只能证明页面已返回，不能从读取顺序还原内部人工复核顺序。

## 纯审核与真实读取

8次都完整返回 SKILL、writing-rules、review-checklist、anti-ai-patterns、prose-lint-usage 各1次，另各读对应主叶（申请或新闻评论）。无同一页全文反复返回，无无关文种叶子。目录枚举不算读取全文。

| 运行 | 唯一页数／返回字符 | 六页核心组合以外的实际读取 |
| --- | --- | --- |
| m0 纯审核 baseline | 8／7816 | argument-chains、structure-editing |
| m0 纯审核 candidate | 8／6864 | argument-chains、proofreading-checklist |
| m0 改稿 baseline | 7／10580 | reference-index |
| m0 改稿 candidate | 7／9910 | reference-index |
| m2 纯审核 baseline | 9／10886 | reference-index、genre-routing、structure-editing |
| m2 纯审核 candidate | 11／11445 | argument-chains、genre-routing、reference-index、proofreading-checklist、formulaic-language |
| m2 改稿 baseline | 10／12708 | genre-routing、reference-index、genre-checklist-request、compression-details |
| m2 改稿 candidate | 12／14054 | genre-checklist-request、reference-index、genre-routing、formulaic-language、compression-details、formal-addressing |

纯审核4次均扫描了待审原稿的非空内容，均未执行业务算术；m2 baseline 还扫描了审核意见，这是不同对象，不能算同稿无变化重扫。m0 candidate 在原稿扫描后额外跑 `draft_length.py --min-chars 80`（item_11，211字）；用户只要问题位置和建议，没有此篇幅条件，该次计数没有本轮用途。它是审核范围误用，不是金额复算。

原稿含“调正”及论证、重复表达问题，proofreading、argument-chains、structure-editing 有任务关联，不列为无关。主叶已经明确后再读 index/routing 属可省的发现开销；m2 两方对简单120–220范围均扩读 compression-details，候选还读 formal-addressing，未见复杂计数或称谓关系的独立需求。候选的 formulaic-language 亦属可省扩读，但仍与语言审校有关，不能据此声称误入无关文种。m0 baseline 两次全目录枚举、m2 baseline 的 `dir /s /b references` 失败后重试，以及 m0 candidate 同131字稿切换扫描模式，是另外的重复执行开销。

## 可归因边界

- 确认候选显式复算义务已被读取却未执行；这属于本批已证实的执行缺口。两方终稿都算对，不能把算对、扫描成功或自报校核当工具复算成功。
- m0 改稿两方读页集合相同，候选少返回670字符，对应审核页缩短；其他组合的页选择发生变化。本批总返回字符41990→42273、命令56→61，不能声称实际读取整体下降，也不能当成质量胜负。
- 本批是 c6基线与 calculated 整页候选的比较，没有 repaired 同场执行对照。纯审核未观察到无关算术调用；额外80字计数、扩读页、编码失败及模式切换均不能单独归因于新增复算句。

后续维护仍应沿所有任务共用的短流程处理：核算归本轮可计算事项，计数归本轮需交付的有篇幅对象，材料和路由已经足够时停止扩读。无需新增长短入口、算术专页或逐项询问。本审计不改规则，也不据这8次要求扩大重测。

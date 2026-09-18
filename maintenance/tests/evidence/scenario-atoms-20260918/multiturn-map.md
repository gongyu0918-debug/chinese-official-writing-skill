# 1.0 → 2.0 多轮修改与局部修改映射

核对基线：1.x历史分支d561bf6b，2.0现行main 21f3de03。结论针对功能含义，不要求旧规则逐字搬回。

| 1.x能力与落点 | 2.0落点 | 本轮实际验证 |
| --- | --- | --- |
| SKILL/workflow 的最新版底稿、用户本轮补充优先 | SKILL入口第1/3步；writing-rules第1步；structure-editing“最新版主线” | 同一会话三轮修改，保留已换标题、主送、落款及新增段落 |
| workflow 的结构动作先执行，再统一语言 | structure-editing“结构动作清单” | 交换小节、连续编号、删除完整段落 |
| structure-editing 的句/段/节粒度、新增段落保留标题层级 | structure-editing原功能保留 | 指定位置增加独立自然段，保留三个小标题 |
| structure-editing 的主体变更联动 | 同页“主体变更”；SKILL用途与行文关系 | 改主送和发文单位，正文称谓同步；后续不回旧版 |
| field-editing 的字段名、顺序、边界，指定值增删 | field-editing同名专页；SKILL局部修改直接指向 | 分号拆行、数量及合计、删经办人、增加空电话字段，再只改原因和备注 |
| workflow 的模板优先、文种要素锁定 | SKILL模板与主文种选择；writing-rules第2/3步；各主文种页 | 结构稿保持通知功能，表单保持字段形态；不强迫套正式文种模板 |
| workflow 的首尾位置、结尾语在落款日期前 | formal-addressing“人员称谓和结尾”；format-gbt9704“正文、附件和落款”；对应文种页 | 已确认规则有对应；本轮两条连续链不是尾语专项测试 |
| 局部修改按用户限定范围交付 | SKILL识别修改范围；writing-rules第1步、第3步“局部查改动与关联内容” | 本轮检查未指定字段、段落是否保持，及复核是否越界改写 |

2.0不再由一个长workflow页集中载入所有这些条目，但结构页与字段页并未被删除。入口明确指向两页，因此不能仅根据workflow退役推断能力丢失；也不能仅凭文字仍在就宣布实际执行稳定。

真实会话使用[Codex非交互会话续接](https://developers.openai.com/zh-Hans/docs/non-interactive-mode)的`exec resume <SESSION_ID>`，本机CLI帮助核对参数。每组使用独立临时配置与目录，插件、apps、记忆、子代理关闭；首轮读取对应版本Skill，后续继承本组上下文。原稿、实际session ID、原始命令、读取轨迹、时长与token记录在output/scenario-multiturn-20260918，定稿时将紧凑证据归档到本目录。

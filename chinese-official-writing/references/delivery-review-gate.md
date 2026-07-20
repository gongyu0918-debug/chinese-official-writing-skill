# 保护性外扩一次性门禁

本页只用于起草或改稿已经形成非空完整初稿 D0 后的交付边界。它处理反复出现的保护性事实外扩、证据充分性元判断、写法自证、无办理作用的外围未决汇总和相邻零增量复述；不重新起草全文，不改变文种路由、事实边界、格式、篇幅预算或长文结构。

## 先保住成稿

- 原始用户请求、用户提供的材料和 D0 是唯一输入来源。检测前建立一次性事务，保存原始请求、材料和 D0 快照；Agent 自己归纳的请求、保留清单或锚点说明不能替代这些快照。
- D0 是不可变回退稿。检测、局部修改和复核只在事务内进行，最终只能选择 D0 或复核通过的 D1。
- 当前宿主缺少命令执行能力或门禁脚本不可用时，不启动本页事务，沿用总审后的完整 D0，标记通道不启用。事务已经建立且快照可验证时，无命中、报告缺失、解析异常、局部修改为空、超时、复核失败、修改越界或结果不确定均使用 D0。选择记录已经存在或有终态证据、但记录损坏或无法验证时，脚本返回非成功且不输出另一稿，由宿主沿用内存或调用侧已保留的选定输出。
- 每个事务只有一次检测、一次补丁预算、一次机械预检和一次语义确认预算。终稿选择凭证写入后，任何后续命令只读取既有选择，不再检测、修改或复核。

## 有限状态

```text
DETECTING
  -> AWAITING_REPAIR
     -> MECHANICAL_VERIFYING
        -> AWAITING_VERDICT
           -> SEMANTIC_VERIFYING
              -> TERMINAL_D1
              -> TERMINAL_D0
           -> TERMINAL_D0  超时、报告缺失、确认不全
        -> TERMINAL_D0     越界、事实回退或正文明显塌缩
     -> TERMINAL_D0  超时、空补丁、主动回退
  -> TERMINAL_D0     无命中、检测异常
```

在尚无终稿选择记录且事务快照可验证时，`DETECTING`、`MECHANICAL_VERIFYING` 或 `SEMANTIC_VERIFYING` 中断后直接进入 `TERMINAL_D0`。状态之间没有返回边，也没有语义确认后返修、终态再检测或补字后再审。终稿通过原子选择凭证锁定；并发调用只能服从最先写入的 D0 或 D1 选择。若凭证或可交叉验证的终态证据损坏，脚本不猜测、不改选，返回非成功且不写标准输出，宿主使用调用侧已经保留的选定输出。首次起草调用本身的超时、拒绝或无返回由宿主处理。

## 检测与语义确认

支持命令执行的 Agent 按本页依次完成 `detect -> prepare -> finalize -> emit`。`detect` 同时接收复看前 D0 和写后只标记稿，先机械确认去标记文本与 D0 逐字一致，再建立无标记 D0 和 sidecar；当前 Agent 只提交一次局部决定和一次只读确认。提供稳定 bridge 的 harness 或宿主 hook 可以调用 `dispatch` 运行同一有限状态链。两种入口共用同一事务预算和终稿选择规则。

检测同时建立 D0 快照：

```text
python scripts/review_gate.py detect --request <raw-request.txt> --draft <draft0.txt> --marked-draft <draft0.marked.txt> --txn <transaction-dir>
```

改稿任务另把用户提供的最新版底稿、附件摘录或其他原材料作为 `--source` 传入；该参数可重复。不要把 Agent 生成的摘要或测试要求写成 source。

```text
python scripts/review_gate.py detect --request <raw-request.txt> --source <user-source.txt> --draft <draft0.txt> --marked-draft <draft0.marked.txt> --txn <transaction-dir>
```

`detection.json` 只定位候选句。命中词语或句式不是删除指令。只有同时满足以下条件，才提交局部补丁：

1. 句子主要解释已知事实不能推出材料未要求的结论，说明稿件没有采用某种写法，集中罗列与当前办理目的无关的外围未决事项，或者只复述相邻正文已经完整承载的同一主体、动作、对象、数字、日期和状态而没有新增结论或办理作用。
2. 句子不是原始材料明确载明的业务状态、正式否定结论、法定或制度性禁止、直接引语、建议、议定事项、责任或期限；删改后不会把待定写成已定，也不会改变原因、影响、处置和决策状态。
3. 局部处理后不损失事实、数字、日期、主体、对象、建议、决定、议定事项、文种功能和用户明确要求。

材料只写某项尚未决定或尚未形成结论时，先看该状态是否承担当前文种功能。必要状态按原对象、范围和强度保留。材料没有给出后续动作时，不补造调查、研究、报会、采购或责任安排。

起草或改稿的完整 D0 在进入本流程前，应已按 `information-selection.md` 完成一次写后只标记复看。`--draft` 传入复看前 D0，`--marked-draft` 传入复看稿；脚本去除分隔符后逐字比较文字、数字、空格、标点、段落和顺序。任何差异均选择复看前 D0。标记数可以为零；零标记仍须执行普通检测，无任何 finding 时直接选择 D0，存在普通 finding 时继续既有有限状态链，最后统一由 `emit` 交付 D0 或 D1。门禁不要求模型补写待处理内容。

本流程发现 AG-G 标记时，先去除 `⟦OWG-DROP⟧…⟦/OWG-DROP⟧` 分隔符并逐字保留其中内容，以这份无标记文本建立 D0；标记边界、精确位置和原始输入哈希另存 sidecar。成对、非嵌套且不跨段的标记才进入 finding。截断、孤立闭合、嵌套、空块或跨段标记直接选择 D0，不调用修改 Agent。相同标记内容按位置区分，不用全文字符串替换。最终 D0、D1 均不得残留机器标记。

## 一次局部补丁

同一 Agent 只生成一个内部 JSON 决策包，最多处理 12 个 finding。包内必须逐项覆盖本次检测的全部 finding，每项只选 `KEEP`、`DELETE` 或 `REWRITE`，并服从该项 `allowed_decisions`；该字段按材料只读性、句子完整性、可结构化硬锚点和删除拼接安全性先行收窄动作范围，合成后的硬锚点冗余、权威来源和整稿完整性仍由机械层统一确认，未通过即选择 D0：

- `KEEP`：材料明确载明、承担当前文种功能，或无法确认删改安全时原样保留；`replacement` 与 `target` 逐字一致。普通检测 finding 的 `source_exact=true` 继续只读。AG-G 标记只说明模型主动隔离了待判断尾句；即使该尾句近于材料原句，也须结合主旨关联性和文种功能作语义判断，不能仅凭 `source_exact` 自动删改或自动保留。
- `DELETE`：仅在该 finding 的 `allowed_decisions` 明确列出 `DELETE` 时使用；整句均为可机械证明的保护性表达，或者由 AG-G 圈定且经原稿证明的无办理作用复述，且删除不改变数字、日期、主体、对象、建议、决定、议定事项、标题、序号、分节和正文完整性；`replacement` 为空字符串。其余 finding 在该项给出的 `KEEP`、`REWRITE` 范围内处理。
- `REWRITE`：保留原句承担的事实与状态，只把保护性外扩改成自然的进行态或业务表达。替换句保持单句、非空，不增加事实、动作、主体、因果、未来承诺或责任强度，不把未决写成已定，不另开条件。进行态转写可以小幅增加字符；机械层按整稿净增量控制，默认容许不低于 20 字且约为目标篇幅或现稿的 5%，不要求为压短替换句而删减数字、对象或状态。

整个决策包仍只计一次补丁。普通检测与 AG-G 命中同一精确区间和原句时合并为一个 finding，保留 AG-G 身份并合并全部标签，只占一个预算、只提交一个决定；区间或原句不同的相邻、交叠内容不合并。脚本逐项检查精确 target、决定类型、硬锚点、序号和结构，再对合成后的唯一 D1 做一次正文完整性检查。任何 finding 缺少决定、超过 12 处、发生目标重复或任一改动越界，整个事务选择 D0，不拆包、不追加第二轮。AG-G 的整块删除如果重复引用日期时段、数字加单位、中文数量、拉丁标识或完整引语，只有同一完整锚点短语在原稿未修改区域和用户原始请求或 source 中均有留存时，才允许进入语义确认；日期、时间、阿拉伯数字和中文数量都按最长单位短语识别，只归一其中的横向空格，换行不作空格，完整引语、书名号和拉丁标识逐字比较，request 与 source 分开提取。唯一锚点、裸数字、同数字不同角色、由两个待删块互相背书或删除拼接形成的锚点仍选择 D0。该机械放行只确认重复硬值没有被换值或清空，主体、对象和事实关系仍由一次语义确认及 `guided_marker_scope_safe` 负责。

存在多项 AG-G 时，Agent 在一次决策包内先按用户口径估算合成稿篇幅。全部删除会使篇幅明显偏离时，保留兼具必要承接或与文种功能关联较强的低风险项，优先处理材料外程序、写法自证和无办理作用最明显的复述，不补写新内容凑字数。用户给出的篇幅用于观察局部处理后的成稿是否明显失衡，不以一两个句子的安全删改造成轻微偏差作为硬阻断；只有篇幅偏差明显扩大或正文、分节发生塌缩时选择 D0。AG-G 只按最终去除机器标记后的交付稿计数；失败回退时保留的标记内文属于实际交付内容，照常计入篇幅。

`run_id` 和三个哈希取自事务内的 `state.json`、`detection.json`，`revision_count` 固定为 1。`repair.packet.json` 含 `guided_marker_sha256` 时，决策包必须逐字复制该字段；没有该字段时省略：

```json
{
  "schema_version": 2,
  "run_id": "<transaction run_id>",
  "request_sha256": "<state.json 中的值>",
  "source_sha256": "<state.json 中的值>",
  "draft_sha256": "<state.json 中的 d0_sha256>",
  "guided_marker_sha256": "<repair.packet.json 含此字段时逐字复制>",
  "revision_count": 1,
  "repair_mode": "decisions",
  "repairs": [
    {
      "finding_id": "P001",
      "target": "<逐字引用命中句>",
      "decision": "REWRITE",
      "replacement": "<保持原事实与状态的单句局部改写>"
    },
    {
      "finding_id": "P002",
      "target": "<逐字引用命中句>",
      "decision": "KEEP",
      "replacement": "<与 target 逐字一致>"
    }
  ]
}
```

补丁文件放在事务目录外。没有安全改动时，对全部 finding 选择 `KEEP`，或者直接回退：

```text
python scripts/review_gate.py abort --txn <transaction-dir> --reason no_safe_repair
```

## 一次机械预检、语义确认与交付

```text
python scripts/review_gate.py prepare --txn <transaction-dir> --repairs <repairs.json>
python scripts/review_gate.py finalize --txn <transaction-dir> --verdict <semantic-verdict.json>
python scripts/review_gate.py emit --txn <transaction-dir>
```

`prepare` 接收首个决策包后把事务切到 `MECHANICAL_VERIFYING`。脚本只机械应用精确替换，并检查事务和输入哈希、finding 覆盖、决定类型、修改范围、数字日期和中英文数量、直接引语、书名号、拉丁标识、标题与小标题、正文和分节完整性、用户篇幅偏差是否明显扩大，以及已定、未决和条件语境。任一项失败立即选择 D0；通过后只生成内部 D1 和 `semantic-verification.packet.json`，不交付 D1。

同一 Agent 随后只读原始请求、用户材料、D0、补丁和 D1，按以下固定 JSON 判定，不提出建议、不输出改稿、不要求再审：

```json
{
  "schema_version": 1,
  "run_id": "<state.json 中的值>",
  "request_sha256": "<state.json 中的值>",
  "source_sha256": "<state.json 中的值>",
  "draft_sha256": "<state.json 中的 d0_sha256>",
  "candidate_sha256": "<state.json 中的 d1_sha256>",
  "verdict": "PASS",
  "checks": {
    "no_new_fact_action_or_actor": true,
    "decision_and_unresolved_state_preserved": true,
    "necessary_content_preserved": true,
    "p0_expression_removed_or_reduced": true,
    "genre_structure_and_usability_preserved": true
  }
}
```

`p0_expression_removed_or_reduced` 在本页统一指本次 finding 对应的保护性表达或无办理作用复述已经删除或减少；字段名沿用现有事务协议。

存在 AG-G sidecar 时，语义确认包另要求 `guided_marker_scope_safe=true`，并回显 sidecar 哈希。该项只确认标记未圈入必要事实、数字、主体、责任、期限、决定状态或文种功能；无标记任务仍沿用原有五项检查，不增加字段。

只有哈希全部一致、`verdict` 为 `PASS` 且五项均为 `true` 时，`finalize` 才选择 D1。尚未产生终稿选择记录时，`FAIL`、`WARN`、无法判断、缺字段、多余建议文字、超时、解析失败或任一项为 `false` 均选择 D0。已有选择记录无法验证时，`finalize` 返回非成功且不改选。语义确认只判定当前 D1，不得返回补丁或触发第二次修改。

`emit` 是唯一终稿读取入口，只向标准输出写入已选择的完整稿件，不接受任意输出文件路径。若在语义确认完成前调用 `emit`，原子选择凭证立即锁定 D0；即使当时事务锁被其他进程占用，后续机械预检或语义确认也不能再把该事务改成 D1。选择凭证可验证时，重复 `emit` 始终返回同一稿；选择凭证及其交叉验证证据同时损坏时，`emit` 以非成功结束且不输出替代稿，宿主使用调用侧已保存的终稿。脚本不把磁盘故障表述为已经送达用户。调用成功后，把本次 `emit` 的标准输出逐字作为整条最终回复，输出后结束回答。

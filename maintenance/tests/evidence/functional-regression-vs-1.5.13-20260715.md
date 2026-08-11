# current 相对 v1.5.13 的真实写稿功能回归

日期：2026-07-15

固定上一发行基线：`v1.5.13` / `cd2d46c58a5f56b9009c5da08626a88640f2e5b3`

被测候选：`f4d79ceeed4f2ae78f8a2522f22f709d63b6056c`

## 目的与边界

本轮回答“当前相对 1.5.13 是否出现功能性写稿回退”，撤回条件为 current 独有的事实、文种、格式或输出模式失败。测试只使用固定 tag worktree 和当前根目录，不读取或复用会话 `019f565b-ac83-79d2-8958-ccd3f91ea9fa` 的旧实现路径；该会话只用于确认修改边界。

`v1.5.13..current` 虽累计涉及 95 个文件，但实际产品规则变化集中在 canonical `SKILL.md` 和 `references/task-route-cards.md`：先判输出模式，轻量卡只覆盖四类任务，已形成决定、结论、一致意见、责任或期限以及完整正式纪要转入 playbook。其余主要为镜像、评测 provider、测试和证据。本轮仍按真实用户可见结果做广泛 A/B，不用文件数替代功能验证。

## 测试设计

两名全新 writer 分别使用反向 A/B 映射；每一侧从对应根目录的 `SKILL.md` 开始，按该版本的渐进路由读取必要 reference。两名 writer 不读取旧证据、外部审核报告或对方输出。15 个 prompt、每个 prompt 由两名 writer 各写 baseline/current，共 60 份成稿。

两名全新 verifier 均只读取原 prompt 和匿名成稿，不读取源码、Skill、Git、版本映射或其他证据：

1. 综合 verifier 同时判内容和 writer 自报路由；
2. 硬边界 verifier 独立复核事实、文种、格式、输出模式和明确禁止项，不评价路由。

两份盲审完成后才创建 `mapping.md` 揭盲。原始文件见同名目录。

## 覆盖范围

| 用例 | 主要风险 |
|---|---|
| F01 | 简短且全部未决的会议纪要；轻量卡；禁止补决定、责任和期限 |
| F02 | 完整正式且已决/未决并存的会议纪要；决定、责任、期限和待确认状态 |
| F03 | 材料稀疏情况说明；限字；不补原因、责任、整改或正文外说明 |
| F04 | 短通知；对象、期限、渠道、联系人、落款和日期 |
| F05 | 二次局部修改；只改一个日期；其余逐字保留 |
| F06 | 请示不写成报告；缺项不编造；请批事项和文后短提示 |
| F07 | 报告不夹带请批；数量、状态和期限保真 |
| F08 | 只审不改；指定普通文本标签；不重写、不评分、无 Markdown 加粗 |
| F09 | 去口语化；引语逐字保留；不扩张事实 |
| F10 | 字段式模板优先；只改目标字段；顺序和值锁定 |
| F11 | 普通服务器维护采购；不得误入 AI 算力 |
| F12 | AI 算力需求；GPU、期限、费用、用途和可用性保真；缺失参数不补造 |
| F13 | 最新底稿唯一主线；旧主送、金额、服务期和结论防回流 |
| F14 | 完整正式但全部未决；隔离验证“完整正式”升级条件 |
| F15 | 简短但已经形成决定；隔离验证“已决/责任/期限”升级条件 |

F14、F15 是独立覆盖审计后追加的隔离样本，避免 F02 同时触发“完整正式”和“已经形成决定”而掩盖单一分支错误。

## 盲审结果

综合 verifier：

| 版本 | 内容 PASS | 内容 WARN | 内容 FAIL | 合计 |
|---|---:|---:|---:|---:|
| 固定 `v1.5.13` 基线 | 29 | 1 | 0 | 30 |
| current | 29 | 1 | 0 | 30 |

两项 WARN 均来自 Writer E 的 F01：基线侧和 current 侧都没有明示“未形成决定、结论、责任分工和完成期限”，但都保持建议、观察和再次评估的未决口径，没有写出相反决定。该现象对称出现，不是版本独有。综合 verifier 对 60 条 writer 自报路由均判任务相关。

硬边界 verifier：

| 版本 | PASS | WARN | FAIL | 合计 |
|---|---:|---:|---:|---:|
| 固定 `v1.5.13` 基线 | 30 | 0 | 0 | 30 |
| current | 30 | 0 | 0 | 30 |

两条独立盲审链均未发现 current 独有的事实、文种、格式或输出模式问题。current 没有触发用户约定的撤回条件。

## 路由复核

真实 writer 自报：

- current 的 F01 两次均停在未决事项轻量卡；固定基线一次停轻量卡、一次进入会议纪要 playbook；
- current 的 F02、F14、F15 两次均进入会议纪要 playbook，并分别保留混合状态、全部未决状态和已决事项；
- F03、F04、F05 分别命中材料稀疏、短通知和二次局部修改轻量卡；F06、F11、F12 等非四类任务进入相应文种或专项叶子。

另用 exact prompt 调用评测 provider 的 reference 选择函数，得到：

| 用例 | 固定 `v1.5.13` provider | current provider |
|---|---|---|
| F01 | `SKILL + task card + playbook + argument + style` | `SKILL + playbook` |
| F02 | 同上 | `SKILL + playbook` |
| F14 | 同上 | `SKILL + playbook + argument` |
| F15 | 同上 | `SKILL + playbook` |

current provider 相对基线已显著减少无关 reference，但 F01 的“不得补写‘会议决定’”仍被 provider 正则识别为已决信号，因此多读 playbook；F14 因会议名称含“论证会”额外读 argument。真实 current writer 在 F01 的两次执行中均正确停轻量卡，60 份正文也没有由此产生功能失败。该差异属于评测 provider 的剩余路由效率问题，不是 current 独有的用户可见回退。本轮不继续扩张否定正则：前序复现已经证明整段屏蔽会吞掉同句后半的真实责任或期限，继续在本次功能回归提交中追补会扩大修改范围。

## 工程回归

- `python -B -m unittest discover -s tests -v`：174/174 通过。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.13-cold-audit --baseline-label baseline-1.5.13 --current-root . --out output/functional-regression-vs-1.5.13`：baseline 108/108，current 108/108。该工具不调用 LLM，只作确定性支撑。
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`：20/20 通过，0 failed，0 errors。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：通过。

## 结论与限制

相对固定 `v1.5.13`，本轮 15 场景、2 名反向映射 writer、60 份成稿、2 条独立盲审链未发现功能性写稿回退。事实、数字、状态、文种、用户模板、只审不改、只输出正文、局部修改、旧稿防回流、普通采购和 AI 算力边界均稳定；不撤回 `f4d79ce`。

该结论是广泛短稿/改稿功能回归，不等同 3000 字以上长文、多附件合稿、Word 版式或全 29 文种发布级矩阵。writer 的 `ROUTE` 是自报，不是操作系统级访问日志；评测 provider 的 F01/F14 剩余 over-read 已如实记录。由于本轮产品文件未再改变，不因这个测试证据提交重新启动长文或全量文种生成。

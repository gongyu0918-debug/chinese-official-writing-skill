# WR-014-R5 采购状态层级真实写稿结果

日期：2026-08-25。

## 结论

`CURRENT_PRODUCT_SUFFICIENT_FOR_STATE_SCOPE / NO_PRODUCT_CHANGE / NO_NEW_HOOK_CAPABILITY`。

“尚未形成采购决定”不是多重否定，也不是应当机械禁用的词串。真正需要核对的是状态层级：整体采购决定、具体型号/供应商/采购方式、采购活动阶段不能互相替代。当前产品在四个范围有效样本中的目标层级4/4通过，没有达到预登记的“至少两家复现目标问题”候选启动条件，因此不修改 Skill、reference、Hook 或 adapter。这里的4/4只证明本原子目标；Alibaba2和MiniMax另有下表所列全文硬失败，不得合并成“全文四稿通过”。

合理推断没有被当成失败。A题中基于月借还量、高峰等待和短时离线反推的采购原因、分流作用和低强度预期均予接受；Alibaba1 C题的“资格审查完成前尚不具备确定供应商的条件”也按给定阶段直接支持的办理结论处理，只记措辞观察，不判状态硬失败。判定不要求结论在材料中逐字出现，也不把一切效果判断强制降成预期；只有把目的或尝试升级成材料不能支持的全量、长期、确定成效，或新增数字、真实对象、责任、程序、期限和决定时，才按事实硬失败。

## Codex Desktop Baseline

固定提交：`9f96e373`，产品树等同 `main@4a55c283`。五个任务均在 Codex Desktop 创建；写稿模型只使用便宜 provider，完成结果提取后均已归档。

| provider | task | final SHA-256 | 目标判定 | 全文判定 |
| --- | --- | --- | --- | --- |
| OpenCode Go DeepSeek V4 Flash | `01a0354f-8cf8-76a2-a7d7-6e8336bf6a20` | `DCB6CB9C5D6DB619171C9DFD505F0B7CF32E22E5EB0E162B8342463463ED853F` | `INVALID_SCOPE` | 实际读取 `C:\Users\admin\.codex\memories\MEMORY.md` 和 rollout summary，违反固定只读范围；稿件不计质量票 |
| Ollama Cloud DeepSeek V4 Flash 0731 | `01a0354f-913f-7da3-bb3b-3a6d0dfc954d` | `A2DF4082E7F867378C1040D22996433293230D14A1E91FDDA28BC7B09D8EAA6B` | `PASS` | `PASS_WITH_SCOPE_NOTE`；A的原因/预期成立，B/C状态完整，个别定性略宽但无硬事实升级 |
| Alibaba Token Plan DeepSeek V4 Flash 0731 | `01a0354f-9575-7772-a559-e17345054b5e` | `3C6610B36359B9DB687039FC9F44E5167E312E6CC34A3890F88362705CB9B5AD` | `PASS` | `PASS_WITH_SCOPE_NOTE`；C的条件结论由给定资格审查阶段直接支持，不按过严口径阻断 |
| Alibaba Token Plan 2 DeepSeek V4 Flash 0731 | `01a0354f-99e4-7201-bf28-17032efd34c6` | `5EB484C88842A75FEBD319F50C6A65FF62E4659BE2801A26CFD15FC24C085307` | `PASS` | `HARD_FAIL_OUTPUT_SHAPE`；A/B/C分隔符后移，C在保留具体状态后追加抽象“尚无最终结论”，后者只记表达观察 |
| MiniMax M3 | `01a0354f-9e1f-7792-bc21-507cec4fdf89` | `30D7618FC549908EACE5E098E81154777FE4D3DD167CD0ACC2E165C2EAE9F8D2` | `PASS` | `HARD_FAIL_FACT_DATE`；B新增“设备运行正常”，三题擅加未给成文日期2026年8月25日 |

### 三题目标结果

- A“原则同意采购、局部节点未定”：四个有效范围样本均保留总体已决，没有写成“尚未形成采购决定”。
- B“整体未决明示”：四个有效范围样本均保留会议只听取、继续试用、补测后再研究和未作新增采购决定的含义；允许自然正向承载，不要求固定词句。
- C“采购已启动、资格审查进行中、供应商未定”：四个有效范围样本均保留具体阶段和对象。Alibaba2 另加抽象概括但没有替代具体状态，按预登记只记 `STYLE_SCOPE_NOTE`。

Alibaba2 的输出形状失败、MiniMax 的事实/日期外扩是真实质量风险，但它们不构成“采购状态层级”候选的目标收益，也不能用来反向证明需要增加禁词或 Hook。

## Hook 只读诊断

当前 Hook 并非完全看不见该句，而是有意把未决状态视为语义敏感项：

- A题安全稿中的“型号、供应商和采购方式尚未确定”会形成1个 finding；追加材料外“目前尚未形成采购决定”后形成2个 findings。
- B题来源明确的“会议未作出新增采购决定”也会形成1个 finding。
- 三类 finding 的动作约束均为 `KEEP/REWRITE`、`semantic_sensitive_finding`，说明机械检测不能判断“局部上推”与“整体明示”。
- 尝试把A题材料外抽象句改写为来源已有的“采购事项已获馆务会原则同意”，机械门安全回退D0，原因为 `replacement_strengthens_status`；D0回退不算修复成功。

首个 Hook 诊断命令因动态导入时漏注册 `sys.modules` 报错，修正为仓库测试同样导入方式后才得到上述结果。基于本轮真实写稿未复现目标问题，不为一次合成 D0 新增语义 verifier、capability 或宿主 adapter。以后若出现新的真实稿反例，应先做同一D0的语义修订原子；不能用字符串删除，因为来源明确的整体未决状态必须保留。

## 官方表达校准

- 中国政府采购网案例分别写“政府采购活动尚未完成”“中标、成交供应商尚未确定”，说明具体阶段和对象应分别承载：<https://www.ccgp.gov.cn/llsw/202404/t20240423_21892700.htm>。
- 上海市发展改革委清单写“尚未确定采购对象或承建主体”，同样采用具体对象状态：<https://fgw.sh.gov.cn/fgw_fzggdt/20231019/440820b253814ef9929fb9cb6aa99e8f.html>。

这两例只校准方法，不复制为固定模板，不以流量或单例冒充质量。

## 实际命令与边界

- `git worktree add -b codex/wr022-procurement-state-scope-r1 ... main`
- 五次 Codex Desktop `create_thread`，模型与 task id 如上表；使用 `wait_threads`、`read_thread` 提取命令和冻结正文，随后 `set_thread_archived`。
- `python -B chinese-official-writing/scripts/review_gate.py --help`
- 三次只读 Python Hook 诊断；前两次分别暴露导入错误和不完整/错误 KEEP packet，最终完整 packet 得到 `D0 / replacement_strengthens_status`。
- 官方网页检索与实际打开页见 `research.md`。
- `python -B -m unittest maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability.RepositoryReachabilityTests.test_active_markdown_local_links_exist`：最终7项通过；首次运行因规格状态缺少既有“已随v1.6.15发布”精确标记失败1项，补回历史发布事实后复跑通过。
- `python -B C:\\Users\\admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py chinese-official-writing`：`Skill is valid!`；此前误用不存在的仓内 `maintenance/scripts/quick_validate.py`，脚本未启动，不记为通过。
- `git diff --check`：通过，仅有 Windows 换行提示。

没有修改产品、没有运行 Candidate、没有启用在线 Hook 生命周期、没有使用 Kimi/Grok/Qwen 做普通写稿，也没有 push、tag 或发布。

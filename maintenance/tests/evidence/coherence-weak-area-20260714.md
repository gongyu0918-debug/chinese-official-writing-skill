# 改稿一致性薄弱面补测（2026-07-14）

## 结论

本轮补测此前没有覆盖的四类改稿薄弱面：整项删除并调序、正文与表格及两个附件同步、同一单位多重角色和语义指代联动、局部联系人变更防止过度修改。

两名独立 writer 共完成 4 个 prompt、8 份改稿。第三方 verifier 独立判定 8 PASS、0 WARN、0 FAIL。没有同类问题达到“至少 3 份输出、2 个不同 prompt、2 名独立 writer，并经两名 reviewer 共同确认”的产品修复门槛。本轮不修改 `SKILL.md`、`references/proofreading-checklist.md` 或其他产品 Prompt，不新增脚本门禁。

## 样本与隔离方式

原始题面在 writer 开始前固定于 `tests/evidence/coherence-weak-area-20260714/writer-prompts.md`。两名新 writer 只读取题面、W1 指定底稿和当前 skill，不读取其他 writer、reviewer 或预期答案；输出锁定后分别保存为 `writer-a.md`、`writer-b.md`。

两名独立 reviewer 只读取题面、底稿和两份匿名产出，分别保存 `reviewer-a.md`、`reviewer-b.md`。第三方 verifier 再独立核验全部产出和两名 reviewer 的判定，保存为 `verifier.md`。测试使用 Codex 独立子上下文，运行界面未提供可核验的精确模型 ID，因此本轮不把结果外推为跨模型统计结论。`writer-a.md` 入库前只去除了四处 Markdown 行尾双空格，以通过仓库 whitespace 检查；成稿字符内容和段落次序未变，以下记录入库文件的新哈希。

四类样本为：

| 类别 | 场景 | 主要检查点 |
| --- | --- | --- |
| D | 删除统一字段库整项议题，并交换“下一步安排”“存在问题”顺序 | 远距离残留、节号、节内次序、范围限定、其他事实保留 |
| M | 同步修改通知正文、进度表、附件1、附件2 | 接收主体和期限联动，网络安全与技术排障职责不误改 |
| S | 办公室同时承担会议组织和材料汇总，后者改由数据资源处 | “牵头单位”“归口部门”“该单位”等语义指代联动，角色分离 |
| C | 只修改联系人，正文中同名项目负责人保持不变 | 防止按人名全局替换和无关事实回流 |

## 独立评审结果

| Writer-output | Reviewer A | Reviewer B | Verifier |
| --- | --- | --- | --- |
| A-W1 | PASS | PASS | PASS |
| B-W1 | PASS | WARN | PASS |
| A-W2 | PASS | PASS | PASS |
| B-W2 | PASS | PASS | PASS |
| A-W3 | PASS | PASS | PASS |
| B-W3 | PASS | PASS | PASS |
| A-W4 | PASS | PASS | PASS |
| B-W4 | PASS | PASS | PASS |

Reviewer B 认为 B-W1 没有逐字写出“只汇总第二轮核验情况”，将其记为 WARN。第三方 verifier 核对全文后认定：成稿已删除统一字段库及其他汇总对象，专题会议研究对象也已限定为第二轮工作的下一步安排；“只”在题面中是内容范围要求，不是逐字保留要求，因此不构成实质违背。即使保守保留这一 WARN，也只涉及 1 份输出、1 个 prompt、1 名 writer，仍远低于修复门槛。

按 verifier 口径汇总：

| 类别 | PASS | WARN | FAIL |
| --- | ---: | ---: | ---: |
| D | 2 | 0 | 0 |
| M | 2 | 0 | 0 |
| S | 2 | 0 | 0 |
| C | 2 | 0 | 0 |
| 合计 | 8 | 0 | 0 |

## 机械核对

对两份 writer 输出检索以下旧值或残留模式：`统一字段库`、`8月10日`、`8月12日`、`报送信息技术部`、`牵头单位`、`归口部门`、`该单位`、`联系人：陈晨`、`87654321`。结果为 `STALE_PATTERN_MATCHES=0`。

原始文件 SHA-256：

- `writer-prompts.md`：`CFB857554B3EBB079F94C45BEB40447FC2455C454F553E10F247A0D2D847C43E`
- `writer-a.md`：`7A0E842B5F272949EB880205333DEAD6C51FF0588D0093485754CFB6CA7D1001`
- `writer-b.md`：`24D1BE47D95A11494B51A35E8024D98D4D8F83F386F095F88553CD3BA188D953`
- `reviewer-a.md`：`84DB133FA5C8D5E4FC2AD6CCA2F0DF4E5AE6600F37AC3CB7F611B4B59A3BFF42`
- `reviewer-b.md`：`DD4AB5EBF105075CE786752E7BD097F8CE6BB964FFDFDF26FB2BB8A2B19EDDCB`
- `verifier.md`：`BED6F30AB42AA564E60DB0CA062CA58BDADDDE195FBF2DB30C98F34B596602E6`

## 工程验证

- `python -B -m unittest discover -s tests`：152/152 通过。
- `npm.cmd run eval:official-writing:smoke`：20/20 通过，0 failed、0 errors；judge consistency 1.0。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 本轮只有测试题、原始产出和评审证据，没有产品候选，故不制造无意义的产品 A/B；产品 Prompt 保持当前 1.5.13 内容不变。

## 剩余未覆盖风险

本轮不能证明以下场景稳定：

- 用户要求固定法定表述或逐字锁定关键限定词；
- DOCX 正文、表格、批注、页眉页脚和附件的跨对象同步；
- 多个单位同时换责、同名主体和跨节隐含指代；
- 多轮要求相互冲突，或后一轮撤销前一轮修改；
- 更大样本、其他模型和更多文种上的普遍稳定性。

下一轮如继续补测，应优先覆盖“多主体同时换责”和“后一轮撤销前一轮要求”，仍先测后修；只有形成跨 prompt、跨 writer 的重复失败才调整现有稿内一致性 Prompt。

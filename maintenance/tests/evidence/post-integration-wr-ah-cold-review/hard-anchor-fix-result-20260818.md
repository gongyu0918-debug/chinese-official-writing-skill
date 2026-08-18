# AH-001 三方冷审缺口修复与真实修订结果

## 结论

`PASS`。三方冷审确认的字段、ASCII 标识数字、汉字数量、请求授权字段和篇幅数字忽略缺口已修复。修复先经真实扩写/压缩验证，再补直接合同与宿主胶水检查；没有改动 WR-007 reference，也没有删除高信息熵候选规则。

## 真实修订

模型固定为 `opencode-go/deepseek-v4-flash`、`ollama-cloud/deepseek-v4-flash:0731`、`alibaba-token-plan-2/deepseek-v4-flash-0731`，均 max、零重试。

- R1 共6次，6/6技术有效。压缩3/3通过共享硬锚：内联字段、H100、两个小区、6台及供应商未决状态均保留。稀疏材料扩写3/3逐字返回D0；这是事实不足时的预期安全回退，未用于证明字段新增能力。
- R2 只补材料充足的字段化扩写3次，3/3技术有效。OpenCode Go 与 Alibaba 两稿均达到字数、包含全部指定字段并通过机械门；Ollama 稿虽保留全部事实和数字，但漏写用户指定的“申请数量”字段名，机械门正确回退D0。
- 没有重跑已通过的压缩题，也没有为获得更高通过数补抽同题。

R1 manifest SHA-256：`eb40854c04505cd5c59771f1956f74d5d7d57ca69296e3983fdd1014287735f5`。

R2 manifest SHA-256：`df30cf60c58f28d1aa3e682a886e97bc4ce579c57301f38c26ba51b032e5a142`。

## 修复边界

1. 字段按表单结构识别：有值的单行字段或同一行多个字段；“现将有关情况说明如下：”不再被当作字段。
2. 一行多个字段全部进入顺序保护；请求明确要求的新字段可以补入，未授权字段仍回退。
3. H100、A12 等标识中的数字进入硬锚；常见汉字数量单位补齐。
4. 篇幅下限或区间的数字即使带“个”等单位，也不能被误当作正文事实授权。
5. under/over 共用同一缓存契约；加载或 compare 异常均回退原稿。
6. 等义总量句仍可压缩重复自证，但“涉及两个小区”“86人参加”等独立范围事实必须保留。

## 必要工程检查

- 共享硬锚、under、over 直接合同：34/34通过。
- Hook layer、Codex/CodeBuddy adapter、Claude adapter：29/29通过。
- Skill Creator `quick_validate.py`：`Skill is valid!`。
- Codex、CodeBuddy、Claude Code 三套 companion 静态组装成功，分别55、54、54文件；均 `enabled=false`、`installed=false`、`network_used=false`。
- `git diff --check`：通过。

首次误用仓库内不存在的 `maintenance/tools/quick_validate.py`，原始结果为文件不存在；随后改用已安装 Skill Creator 的真实校验器并通过。该路径错误不计为通过记录。

## 信息熵结论

当前32个入口/reference 共197719字节、2139行。五个文种叶的直达、补读、字段和信息选择前言存在逐字重复，日期规则也有三处措辞漂移风险；但12组真实读取总量仅增加约3.1%，真实稿无由此产生的硬回退，三位 reviewer 对是否抽公共层存在分歧。本轮维持 `OBSERVE`：不建立大公共字典，不牺牲叶子自包含；只有后续真实共同加载或稿件机械化证据出现时才做减载原子。

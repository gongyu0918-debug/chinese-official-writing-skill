# Candidate B 自然触发真实写稿来源记录

日期：2026-07-15

## 候选与安装边界

- 产品提交：`b5ef168e617bd0ca9afa1d5d3ca257291a701976`。
- 候选全局安装 `SKILL.md` SHA-256：`D9B80B7295032D07DCA052E6CE3158C5A83AA323E5D4D3AC6D2547EE8EA7A53B`，版本仍为 1.5.14。
- 测试前全局 Skill 为 1.2.18，`SKILL.md` SHA-256：`44BDCF85399E0FEBA87A90A82611B9F336A4580075F91919E0DDE7063DEF6E83`。
- 写稿完成后，候选安装副本保存在忽略目录 `output/candidate-b-global-installed-20260715-1718`，原 1.2.18 已原位恢复；恢复哈希仍为 `44BDCF85399E0FEBA87A90A82611B9F336A4580075F91919E0DDE7063DEF6E83`。

每个 writer 均为 projectless 独立线程，thinking 为 medium。委派 `<input>` 只含固定 T01—T04 的原始用户任务，没有 Skill、基线、测试、A/B、盲审、读取路径或输出标记等控制语。App 自动加入的 `<codex_delegation>` 仅为共同传输外壳。

9 个线程的 `codexDelegation.input` 分别与 Candidate A 同题来源逐字符核对：`9/9 一致`。各输入长度与核对结果如下：

| 文件 | 输入字符数 | 与固定同题 Prompt 逐字一致 |
| --- | ---: | --- |
| `luna-t01.md` | 658 | 是 |
| `luna-t02.md` | 802 | 是 |
| `luna-t02-route-miss.md` | 802 | 是 |
| `luna-t03.md` | 403 | 是 |
| `luna-t04.md` | 555 | 是 |
| `terra-t01.md` | 658 | 是 |
| `terra-t02.md` | 802 | 是 |
| `terra-t03.md` | 403 | 是 |
| `terra-t04.md` | 555 | 是 |

## 线程与实际读取

| 模型 | 任务 | thinking | thread | 入口 SKILL | reference |
| --- | --- | --- | --- | --- | --- |
| `gpt-5.6-luna` | T01 | medium | `019f6513-fc69-7260-a45b-e67cf08dfb4f` | 完整读取 1 次 | 0 |
| `gpt-5.6-luna` | T02 | medium | `019f6518-2a41-7213-b427-5e6c1ab11ff7` | 完整读取 1 次 | 0 |
| `gpt-5.6-luna` | T02 route miss | medium | `019f6514-191f-75e3-a340-a407b9134ac3` | 未读取 | 0 |
| `gpt-5.6-luna` | T03 | medium | `019f6514-2233-7030-830d-7b10f5d4411c` | 完整读取 1 次 | 0 |
| `gpt-5.6-luna` | T04 | medium | `019f6514-2eb8-7f01-94ed-e24c1559058d` | 完整读取 1 次 | 0 |
| `gpt-5.6-terra` | T01 | medium | `019f6514-398c-73e3-8dc5-1077ff69a51c` | 完整读取 1 次 | 0 |
| `gpt-5.6-terra` | T02 | medium | `019f6514-466d-71a1-aedb-cfe4b2f34185` | 完整读取 1 次 | 0 |
| `gpt-5.6-terra` | T03 | medium | `019f6514-5148-7690-911d-19c0ade4197e` | 完整读取 1 次 | 0 |
| `gpt-5.6-terra` | T04 | medium | `019f6514-5f36-7612-81ee-bce46bec7799` | 完整读取 1 次 | `genre-playbooks.md; task-route-cards.md` |

初始 8 个自然调用中，7/8 读取候选入口；Luna T02 首次调用没有读取本 Skill，其原始输出保存在 `luna-t02-route-miss.md`，并计入触发可靠性风险。随后用完全相同的原始 T02 Prompt 新建一次独立 Luna medium 线程，入口读取成功；该复跑稿作为 Candidate B 的有效 T02 质量样本。因此，有效质量样本为 8 份，入口读取 8/8；初始自然触发率仍按 7/8 记录，不因复跑抹除。

8 份有效稿中，仅 Terra T04 自然读取 `genre-playbooks.md` 与 `task-route-cards.md`，其余 7 份只读取入口。因此本轮称为“Candidate B 自然入口执行”，不称为完整渐进式路由。触发与 reference 路由可靠性作为独立风险记录，不与本次中和“宁可短写”的单变量修改混并。

## 原始输出

同目录 8 个 `luna/terra-t01—t04.md` 文件逐字保存有效线程的单个 `final_answer`；`luna-t02-route-miss.md` 逐字保存首次未触发稿。未把 commentary、测试标签或主上下文改写混入成稿。


# 三原子当前 main 组合验证结果（2026-08-01）

## 结论

`ENGINEERING PASS / READY FOR ONE COMBINATION SANITY`。

固定基线为 `6bd6c6762a6ccf6b42c378a3990c093db43804ab`。组合只包含新闻评论 R3、工作总结逐字物理拆叶和入口固定余量删除三个已冻结原子；三项来源补丁均无冲突机械移植，工程回归全部通过。组合未生成真实稿，不据此新增写作质量结论；下一步可由独立 writer 只做预注册的一题组合 sanity。

本分支不合并 main、不改版本号、不发布、不推送。

## 提交与差异追溯

- 组合预注册：`5a9c2734`。
- 新闻评论组合产品：`3036618f`，来源 `ba59011f`。
- 工作总结组合产品：`4a8a2f6d`，来源 `755177b6`。
- 固定余量删除组合产品：`46897a62`，来源 `2d006905`。

stable patch-id 核验：

| 原子 | 来源 / 组合 patch-id | 结果 |
| --- | --- | --- |
| 新闻评论 R3 | `ffcc9452e83e98df0e3664fc6e0aa118798691ce` / 同值 | PASS |
| 工作总结逐字拆叶 | `6ac1f23eb79b6d235ffac01d56232925aa0c3a4d` / 同值 | PASS |
| 删除入口固定余量 | `8c7533c6798738b7f7619d1e48acc44e01868f67` / 同值 | PASS |

独立只读 diff 审计进一步确认：三个来源补丁文件并集与组合产品提交的文件集合相同，双方集合差异为 0；未混入第四项产品规则。

## 三项组合不变量

### 1. 新闻评论 R3

- canonical 新闻评论叶 Git blob 为 `662104ea0ba040911d0815a8db5c02e2c3247e1f`，与来源 `ba59011f` 相同。
- canonical 与五个发行镜像的工作区 SHA-256 均为 `44e4055b1d2a3b85c034d262c631e1fb23b8eb400d9ded77074c7f05b1e8c89f`。
- 只在既有“一次局部复核”句中增加评论推演的事实依据、适用范围和判断强度核对；新闻评论路由、骨架和复核次数未变。

### 2. 工作总结逐字物理拆叶

- 新叶 Git blob 为 `d952abb4dcf38b9b03295077d3a488c41dc2dcea`，删段后的通用 playbook blob 为 `1762062a90a96a0f7351829bea86da33a5d7544f`，均与来源 `755177b6` 相同。
- 独立审计将固定基线原段与新叶正文按 Ordinal 比较：均为 340 字符、7 行，结果为相同，无逐行差异。
- canonical 与五个发行镜像的新叶 SHA-256 均为 `8a52a0c31edda8a2c3ab94769b2f5c9d867cd5ed1f80cd20ccb0a79c3a10226d`；通用 playbook 均为 `4e9ddd112a7eb540b3cb68cd1de98bc4970a68e3cce85dcbccd413b269817d8f`。
- 真实 provider 加载集合由 `SKILL.md + genre-playbooks.md` 改为 `SKILL.md + genre-playbook-work-summary.md`；包含加载标题包装的上下文由 14,192 字符降至 11,005 字符，减少 3,187 字符，减载 22.46%。

### 3. 删除入口固定 5%—10% 余量

- 六个 `SKILL.md` 各减少 13 个字符，短语计数均由 1 降为 0；仍保留“字数自检”和“尽量压到限制内”。
- 六个 `references/workflow.md` 的 `5%-10% 余量` 均仍保留 1 次，明确硬上限场景的安全规则未被删除。
- 未新增达到下限、展开、补写或二次修订规则。

## 实际工程验证

| 验证 | 结果 |
| --- | --- |
| 三原子 focused unittest | 9/9 PASS |
| `python -m unittest discover -s tests` | 407/407 PASS |
| `npm run eval:official-writing:smoke` | 20/20 PASS，0 error |
| 固定 `6bd6c676` 确定性消融 | current 110/110；baseline 109/110。baseline 仅在新增的 P075 工作总结专叶路径断言失败，属于产品新增覆盖，不是 current 回退 |
| `quick_validate.py chinese-official-writing` | PASS，`Skill is valid!` |
| `python tools/sync_adapters.py` | 完成同步；重新暂存行尾归一化后无实际内容 diff |
| 镜像字节一致性专项 | 2/2 PASS |
| reference graph | PASS，缺失引用 0 |
| 三项关键 reference 六包 SHA-256 | 各文件六包完全一致 |
| `git diff --check` | PASS |

Promptfoo 提示本机 `promptfoo 0.121.11` 低于可用的 `0.121.20`，但本轮 20 项均实际完成并通过；未在组合候选中升级依赖。

确定性消融输出位于忽略目录 `output/final-three-atom-ablation-20260801/`。该消融不调用 LLM，只证明包、路由、引用和评测入口无回退。

## 来源证据复制核验

最终提交原样带入四份来源结果证据；复制后 Git blob 与来源分支逐一相同：

| 证据 | Git blob |
| --- | --- |
| `news-commentary-r3-main-integration-result-20260801.md` | `15f0744c79a0f0fc5a9c57fbeb8e270206d993ed` |
| `work-summary-current-main-integration-result-20260801.md` | `81dbbc7e8aabcc723b93fe55148815f6ad889ee9` |
| `candidate-length-headroom-delete-only-current-main-v1531-engineering-result-20260801.md` | `717d1aa16f3c96247f0633d9d448752ac15f160c` |
| `candidate-length-headroom-delete-only-current-main-v1531-real-ab-result-20260801.md` | `8718fb05eb1fc1583583eb99924c28d761e36bb8` |

这些原始结果分别记录：新闻评论 R3 的三对匿名收益与证据限制；工作总结逐字拆叶的真实证据继承和减载；固定余量删除的工程门及三题真实 A/B。组合结果不改写其中结论。

## 剩余风险与停止边界

1. 本轮只做工程组合，没有生成真实稿；三个原子的交互尚需最多一题独立组合 sanity 确认。
2. 新闻评论既有 A/B 的精确模型和 thinking 未由 writer 回执独立回显，仍属二级运行证据；组合工程通过不消除这一证据限制。
3. 工作总结拆叶证明加载减负且未发现可归因回退，不代表它单独提升语言质量；偶发外围补写和篇幅不足仍是共享写作风险。
4. 固定余量删除的三题 A/B 支持篇幅服从改善，但篇幅合规不等于语言质量稳定；本组合不继续调整 `workflow.md` 或增加扩写规则。
5. 任何后续修改新闻评论叶正文、工作总结叶正文/加载集合、篇幅复核顺序或 `workflow.md` 余量规则，都会超出本次证据继承范围，需要重新验证。

综合判定：三原子组合的产品差异、镜像、引用和工程入口兼容，可进入一次独立组合 sanity；不在本分支继续扩规则。

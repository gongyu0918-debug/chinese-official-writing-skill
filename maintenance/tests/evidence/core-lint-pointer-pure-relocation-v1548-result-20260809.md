# 终稿 lint 指针纯前移真实结果（2026-08-09）

## 结论

`PASS / MERGE`。

候选只移动现有 `draft-body` 使用时点，不新增强制执行、命令、检测规则或改稿循环。真实写稿得到一项可由读取轨迹直接解释的改善，其他有效题未形成稳定回退。

## 产品差异

- 基线：终稿 `draft-body` 指针位于 `SKILL.md` 末尾“脚本”段。
- 候选：同一句逐字移动到核心流程第 6 步末尾。
- 末尾仍保留“检查草稿时可使用 `scripts/prose_lint.py`”及原有脚本边界。
- 未增加“运行一次”“必须”、CLI 示例、正则、Hook、FSM、复核次数或自动改稿。

产品提交：`3df03cac`。

## 真实写稿

写手为 Alibaba DeepSeek V4 Flash 0731 high 与 GPT-5.6 Luna high；每题两臂只冻结首个最终正文，后续只询问实际读取和处理轨迹。

### T1 局部改稿

材料明确接口恢复、20 次抽查成功和原因核查中；待修改稿另带无材料锚定的“这不代表问题已经彻底解决，也不意味着业务已经完全恢复”。

- Alibaba：两臂均删除该尾句并保留“异常原因正在核查”；两臂均未读 `final-review-layers.md`，结果为持平。
- Luna Baseline：未读 `final-review-layers.md`，把尾句改写并强化为“尚不能据此认定问题已彻底解决或业务已完全恢复”。
- Luna Candidate：实际读取 `final-review-layers.md` 和 `proofreading-checklist.md`，删除无锚保护尾句，保留原因核查状态，未补材料外行动。

该组形成“位置前移 → 终稿叶被读取 → 无锚保护尾句删除”的直接因果信号。

线程：Alibaba base `019fe2d7-1cca-7b52-953c-35f08f1d6b2d`，Candidate `019fe2d7-2302-7c70-916e-380ef0864952`；Luna base `019fe2d7-44db-7332-80c9-cb3848a467e4`，Candidate `019fe2d7-4bdb-77b3-86ae-f2a25904964e`。

### T2 自然起草

- Luna 两臂正文等价，均保留“共同原因尚未形成结论”，无材料外行动；Baseline 实际读取了已安装镜像而非指定仓库路径，该对只作行为旁证，不作严格路径比较。
- Alibaba R1 Candidate 独有补写核查打印纸和继续跟踪网络原因；Candidate 实际未读终稿叶，无法由移动后的指针解释。
- Alibaba 同题 R2、R3 均未复现材料外行动。R3 两臂共同输出路由旁白，证明该提供商存在同提示输出范围波动。

按既定因果规则，R1 孤立行动扩写记采样噪声，不计 DIFF 回退。

线程：R1 base `019fe2d7-298c-71c2-8dd1-a31f557298ba`，Candidate `019fe2d7-2fb1-7503-9b42-095e1a92004b`；R2 base `019fe2d9-0551-7642-9a95-e5f4bf10f668`，Candidate `019fe2d9-0b64-71a0-989d-720c8f9f7812`；R3 base `019fe2da-b042-7662-966b-955e6ca5480c`，Candidate `019fe2da-b69c-7ed0-90c5-a4937c545083`。

### T3 反向控制

两家写手两臂均保留材料明确的“不得/不能据此判断全体人员填写情况”，未把真实边界删除或弱化。Alibaba 的正文外路由旁白首轮只在 Candidate 出现，复放时两臂共同出现，按噪声处理。

线程：Alibaba base `019fe2d7-3670-78c2-b8c4-7081f2e4a129`，Candidate `019fe2d7-3e45-70d0-b0bc-f76fd85758c9`；复放 base `019fe2d9-11f1-7e22-8515-51abf46b62e6`，Candidate `019fe2d9-189d-76c1-8781-618d73da6ef3`；Luna base `019fe2d7-624c-7270-82f1-b27f5af128c8`，Candidate `019fe2d7-698d-7992-a1a5-6f243e8169df`。

## 决策边界

本结论只支持纯位置移动。此前包含“运行一次”、精确命令、“必须执行”或 `59ea0def` 新正则的候选仍为隔离研究，不随本原子进入 main。

## 工程门禁

- `python -B -m unittest discover -s tests`：457/457 通过。
- `$env:OFFICIAL_WRITING_EVAL_STUB='1'; npm run eval:official-writing:smoke`：20/20 通过，0 failed、0 errors。
- 固定 `main-494c2c11` 与 Candidate 确定性消融：111/111、111/111。
- `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 镜像同步、`git diff --check` 和工作树清洁检查通过。

工程门禁证明结构和确定性支撑稳定；合并依据仍是上面的真实读取轨迹与正文结果。

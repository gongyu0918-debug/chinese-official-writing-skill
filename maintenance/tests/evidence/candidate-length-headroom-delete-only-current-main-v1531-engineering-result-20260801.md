# 入口固定余量删除原子工程验证结果

日期：2026-08-01

## 结论

`ENGINEERING PASS / WAIT FOR REAL A/B`。

本候选从固定 main `6bd6c6762a6ccf6b42c378a3990c093db43804ab` 建立，只删除入口句中的“并留出 5%-10% 余量”。`references/workflow.md` 和 `references/review-checklist.md` 中针对限字压缩的安全余量规则保持不变，也未新增达到下限、展开或补写规则。

产品原子已通过全部预注册工程门，可以按冻结的 `LH01`—`LH03` 题面进入严格真实 A/B；本阶段没有生成稿件，不能据此判断篇幅改善、事实安全或直接使用成本。

## 提交

- 预注册：`c5c139db`。
- 产品原子：`2d006905`。

## 精确差异

- 产品文件：canonical `SKILL.md` 与五份发行镜像，共六份入口。
- 每份运行包减少 13 个字符、23 个 UTF-8 字节。
- 测试变化只涉及入口固定余量短语的存在性：入口仍检查“字数自检”和“尽量压到限制内”，并确认不再出现“并留出 5%-10% 余量”；`workflow.md` 的固定余量断言继续保留。
- `tools/run_real_prompt_ablation.py` 只把 `P038` 的入口锚点由固定余量短语改为“尽量压到限制内”，workflow 与复核清单锚点未变。
- 未修改文种路由、reference 加载、事实边界、篇幅预算、计划段、检测器、脚本门、修改次数、回退、版本号或发布链。

## 实际验证

| 验证 | 实际命令 | 结果 |
| --- | --- | --- |
| focused unittest | `python -m unittest tests.test_skill_boundary.SkillBoundaryTests.test_v144_common_real_writing_risks_and_adoption_gate_are_documented` | PASS，1/1 |
| 全量 unittest | `python -m unittest discover -s tests` | PASS，405/405 |
| Promptfoo smoke | `npm run eval:official-writing:smoke` | PASS，20/20；10 组 skill 胜出，0 error |
| 固定 main 确定性消融 | `python tools/run_real_prompt_ablation.py --baseline-root F:\\Workspaces\\chinese-official-writing-skill\\output\\release-worktrees\\release-1.5.23-main --baseline-label current-main-6bd6c676 --current-root . --out output\\length-headroom-delete-only-current-main-ablation-20260801` | PASS，baseline 110/110；current 110/110 |
| quick validate | `python C:\\Users\\admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py chinese-official-writing` | PASS，`Skill is valid!` |
| 镜像专项 | `python -m unittest tests.test_skill_boundary.SkillBoundaryTests.test_primary_adapter_mirrors_match_canonical_bytes tests.test_skill_boundary.SkillBoundaryTests.test_packaged_resource_mirrors_match_canonical_bytes` | PASS，2/2 |
| 同步复核 | `python tools/sync_adapters.py` | canonical 与五份发行镜像同步后无内容差异 |
| diff 检查 | `git diff --check` | PASS |

Promptfoo 提示本机 `promptfoo 0.121.11` 低于可用的 `0.121.20`，不影响本轮 20 项实际通过结果，未在本候选升级依赖。

## 下一阶段冻结门

只复用预注册中提交 `dbfc4ac1` 的 `LH01`—`LH03` 原始任务及既有 SHA-256。Candidate 与固定 baseline 必须使用 `gpt-5.6-terra/high`、逐字一致输入、同序读集和各自首个技术有效输出，不补抽；writer、硬核验和匿名盲审相互独立。

真实结果须同时回答：

1. `LH01` 硬上限是否继续安全；
2. `LH02`、`LH03` 的低于下限缺口是否缩小；
3. Candidate 是否出现独有的事实、数字、状态、文种、格式、输出模式或 P0 回退；
4. 语言和直接修改成本是否不劣于固定 main。

本候选仍不合并 main、不推送、不发布、不改版本号。

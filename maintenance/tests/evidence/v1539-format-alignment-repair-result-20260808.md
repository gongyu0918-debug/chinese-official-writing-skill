# 1.5.39 Word 正文对齐方式最小修复结果（2026-08-08）

## 结论

判定为 `PASS / RELEASE-READY`。

1.5.39 发布前精简 A/B 发现 Word 版式 Candidate 连续 3/3 漏写正文“两端对齐”，固定 1.5.38 首稿包含该项。问题与本版把 Word 细节从入口下沉至 `format-gbt9704.md` 直接相关：格式 reference 原条目只承载首行缩进，没有承载对齐方式。

## 最小修复

- 预注册提交：`68fc4e01`。
- canonical 只把“正文段落：一般首行缩进 2 个汉字”改为“正文段落：一般两端对齐、首行缩进 2 个汉字”。
- 增加一条确定性边界断言，确保格式 reference 承载“两端对齐”。
- 使用 `tools/sync_adapters.py` 同步五套镜像；入口继续只保留格式 reference 指针，没有恢复字体字号细则。
- 未修改文种路由、事实边界、输出模式、复核顺序、脚本、Hook 或发布链。

## 修复后真实复放

逐字一致原任务由两名新的独立 writer 各取首个完整技术有效输出：

| writer | 实际读取 | 结果 |
| --- | --- | --- |
| `019fe018-b861-7b70-bff7-5bf494ad927e` | `SKILL.md`、`information-selection.md`、`task-route-cards.md`、`format-gbt9704.md` | 明确“正文：3号仿宋体，两端对齐，首行缩进2个汉字”；其他版式要素、事实和日期状态通过 |
| `019fe018-b984-7933-be4e-5650eb895e4c` | 同上 | 明确“正文：3号仿宋体，两端对齐，首行缩进2个汉字”；其他版式要素、事实和日期状态通过 |

两稿均未联网、未补“3月5日”的年份、未补成文日期，标题、12台设备、2台标识不清和“不得据此作出故障结论”均保留。修复后为 2/2 PASS。

## 最终工程门

| 验证 | 结果 |
| --- | --- |
| `python -m unittest tests.test_skill_boundary` | 66/66，通过 |
| `python -m unittest discover -s tests` | 442/442，通过 |
| Promptfoo stub smoke | 20/20，通过；0 failed、0 errors |
| 固定 1.5.38 确定性消融 | baseline 111/111；current 111/111 |
| quick validate | `Skill is valid!` |
| py_compile、镜像同步幂等、`git diff --check` | 通过 |

Promptfoo 运行时提示本机 0.121.11 低于可用的 0.122.0，但本轮 smoke 命令实际完成且 20/20 通过；该提示不改写为产品失败或升级已发生。

原始双臂稿、匿名映射、裁决和前后复放见 `v1539-compact-repro-pack-20260808.md`。

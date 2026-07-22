# Reference 高熵实验 5-commit 检查点（2026-07-23）

## 范围

- 基准：`bc1477c49e9b3cf9ec1ababade9bc4d445f778fe`
- 检查点：`a72d36c`
- 范围内五次提交：两项 proofreading 原子实验的预注册和失败结果，以及一份高熵清单。

## 独立 review 结论

无 P1，产品与测试撤回完整。范围净变化只有三份 `tests/evidence/` 文件；canonical、五份发行镜像和 `tests/test_skill_boundary.py` 与 `bc1477c` 零差异。

review 发现并修正两项 P2 证据口径：

1. 工具链实验预注册固定产品基线写为 `283184b`，实际运行快照使用 `6261427`。后者仅比前者多本实验预注册文档，产品文本一致；失败结论不受影响，结果记录现已明确区分两者。
2. 高熵清单曾写“5-commit 独立 review 通过”，但未在同一提交范围持久化同期回执。现改为本轮检查点复核，并以本文件保存实际 review 结论。

## 复核证据

- 两项实验的 12 份原稿 SHA-256 全部与结果文档一致；原稿和独立判断支持 `FAIL` 与撤回。
- 六份 `proofreading-checklist.md` 当前 SHA-256 一致，为 `8ED0EC71553536E41718A84B6D315395AE81C025006CC4467F1D2C28F6D088AA`。
- 两组确定性消融均为 Baseline 108/108、Current 108/108。
- 现存 Promptfoo 结果为 20/20、0 failures、0 errors、judge consistency 1.0。
- `python -m unittest discover -s tests`：355/355，OK。
- `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：通过；review 后工作树未发现产品残留。

## 证据限制

- 第一项 proofreading 实验自己的 Promptfoo JSON 和沙箱错误日志已被后续同路径运行覆盖，独立原始回执为 `unavailable`；结果文档如实保留当时命令结果，但当前只能直接核验后一次 Promptfoo 文件。
- 被忽略的真实稿件和 writer 回执可在本工作区复核，不是 Git 持久证据；文档中保存了全部稿件哈希和决定性失败点。

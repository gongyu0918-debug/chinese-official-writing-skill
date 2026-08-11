# 1.5.37 后入口清晰化小更新集成记录

## 集成范围

本轮只合并两个已完成原子候选，不改版本号、不发布市场：

1. 关键名词例子下沉：入口保留抽象契约，五个具体例子留在按需 reference。
2. 轻量卡术语自然化：把“在轻量卡早停”改为“由卡片完成，不再读取长 reference”。

其余输出范围自然化、Word 细则迁移、单位名称搜索句删除、模式与路由顺序、终稿 lint 模式指针均保留在独立 worktree，未进入 main。

## 提交与合并

- 关键名词产品提交：a7ad6f54。
- 关键名词测试契约：4ec0bb6d。
- 关键名词证据：b3a34e42。
- 关键名词合并提交：370a2bfd。
- 轻量卡产品提交：3dbfe3ab。
- 轻量卡测试契约：33a0c367。
- 轻量卡证据：2cd738c4。
- 轻量卡合并提交：84292368。

## 真实写作与读取轨迹

两组 A/B 均以 gpt-5.6-terra / high 对称派发，各取首个技术有效输出，不补抽、不二次修订，并由独立匿名盲审复核。

- 关键名词题：Candidate 与 1.5.37 均为 PASS；“受理渠道”“牵头科室”“复核节点”逐字保留，只改指定段落。盲审为 Candidate 小胜，普通句式差异不作因果收益。
- 轻量卡题：两臂均只读取 SKILL.md、information-selection.md、task-route-cards.md，Candidate 未读取长 reference。Candidate 约 203 字并 PASS；Baseline 约 223 字。篇幅差异视为单次采样，不作为术语修改的质量收益。

可归因结论：两项改动均未造成事实、数字、状态、文种、输出范围、局部修改或 reference 集合回退。

## main 组合验证

- python -m unittest discover -s tests：442/442 通过。
- npm run eval:official-writing:smoke：20/20 通过，0 failure、0 error。
- 固定 1.5.37 确定性消融：Baseline 111/111，current 111/111。
- quick_validate.py chinese-official-writing：Skill is valid。
- tools/sync_adapters.py：重放后内容对象哈希与 HEAD 相同；Windows racy-clean 状态经索引刷新后工作树干净。
- git diff --check origin/main..HEAD：通过。

## 剩余风险

- 轻量卡候选因额度收紧没有新增长任务 writer 控制；长任务转读条件没有修改，并由既有单元测试与 111/111 消融覆盖。未来若改变触发集合，必须补短稿/长稿双向轨迹。
- 本轮未证明入口抽象契约可以删除；只删除了重复的具体例子。
- 其余五个候选没有完整真实验证，不能随本轮推送。

# 三原子当前 main 组合验证预注册（2026-08-01）

## 目标与固定基线

- 固定基线：`6bd6c6762a6ccf6b42c378a3990c093db43804ab`。
- 隔离分支：`codex/final-three-atom-integration-v1531`。
- 本轮只验证三个已经单独完成工程验证或真实 A/B 的产品原子在同一工作树中的兼容性；不新增规则、不改版本号、不生成真实稿、不发布、不推送。

## 冻结的产品原子

1. 新闻评论 R3：来源提交 `ba59011f04ff85c62eed999c03e5a5e0a9304870`。只在六个 canonical/adapter 镜像的 `genre-playbook-news-commentary.md` 中，将评论推演的事实依据、适用范围和判断强度核对并入既有一次局部复核句；不改变路由、写作骨架或复核次数。
2. 工作总结逐字物理叶拆分：来源提交 `755177b66765d344755d1cee0e711fd0f61b0e26`。把 `genre-playbooks.md` 中既有九行工作总结/工作要点/周报规则逐字迁移到 `genre-playbook-work-summary.md`，增加直接路由与对应测试/评测入口；不改迁移文本语义。
3. 入口固定余量删除：来源提交 `2d0069056a12470c7f61e9c9e45d5868bd59ad00`。只从六个 `SKILL.md` 的上限自检句删除“并留出 5%-10% 余量”，同步更新确定性断言；`references/workflow.md` 中针对硬上限和精确限字的余量规则保持不变。

三个产品提交按上述顺序机械移植。冲突只允许解决相同上下文的行级合并；任何需要改变规则语义、路由条件、复核次数或测试口径的冲突都停止本轮。

## 组合不变量

- 最终产品差异必须等于三个来源产品相对 `6bd6c676` 的差异并集，不带来源分支的预注册、结果或其他历史修改。
- 新闻评论 canonical 叶内容与 `ba59011f` 对应 blob 一致，各镜像相同。
- 工作总结新叶正文与原 `genre-playbooks.md` 被迁移段逐字一致；常规工作总结、工作要点、周报、月报只加载专用叶，混合文种同时保留另一命中叶。
- 六个技能包的入口只删除固定余量短语；入口其他语义不变。实际字符差按文件内容重新统计，不用提交说明替代实测。
- canonical 与五个发行镜像一致；reference graph 无断链；现有测试和固定基线消融不回退。

## 预注册验证

1. 检查三个产品提交相对固定基线的精确 diff，并在组合后逐项比对文件与 blob/hash。
2. focused：工作总结路由、新闻评论叶、篇幅自检和镜像边界相关单测。
3. full unittest：`python -m unittest discover -s tests`。
4. Promptfoo smoke：`npm run eval:official-writing:smoke`。
5. 固定基线消融：`python tools/run_real_prompt_ablation.py --baseline-root <6bd6c676 工作树> --baseline-label 6bd6c676 --current-root . --out <组合证据目录>`。
6. `skill-creator` quick validate、adapter 同步/镜像一致性、reference graph、`git diff --check`。
7. 统计工作总结命中上下文字符变化，确认减载仍成立；确认新闻评论叶和入口余量原子的最终内容与来源一致。

## 判定

- `PASS`：全部工程门通过，三个原子的最终差异可分别追溯到来源提交，未出现语义冲突或加载回退。随后才允许独立 writer 做最多一题组合 sanity。
- `FAIL`：任一产品差异漂移、镜像不一致、路由/引用断链，或现有工程回归失败；不把失败组合并到 main。
- 环境启动、权限或依赖噪声与产品失败分开记录；只在同一条件下复跑，不改产品措辞救测试。

## 证据随产品保留

最终结果提交同时原样带入三个来源分支的关键 tracked 证据：新闻 R3 当前-main 结果、工作总结当前-main 结果、固定余量删除的工程结果与真实 A/B 结果。复制后逐文件核对 Git blob/hash，避免主线后续只保留产品而缺少验证链。

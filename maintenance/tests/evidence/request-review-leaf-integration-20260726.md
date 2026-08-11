# 请示与申请复核叶集成复核

## 集成对象

- 稳定 main 基线：`8e4721b031422b691e8c9780a9f821a944e68526`
- 预注册重放提交：`1c4527b`
- 产品重放提交：`121a90b`
- 真实 A/B 结果重放提交：`f4f7f9b`
- 集成分支：`codex/1.5.26-relief-integration-20260726`

本次重放保留原候选完整证据链。产品只把请示、申请两节从通用 `genre-checklist.md` 原样迁入 `genre-checklist-request.md`，并在只审或细查请示、申请时读取新叶；起草仍使用既有 `genre-playbook-request.md`，审后改写才叠加起草叶。

固定 1.5.25 的请示/申请起草叶已在稳定 main 的祖先中，本产品提交不依赖其他未发布候选。相对稳定 main 没有产品冲突。

## 本轮复核

- `python -m unittest discover -s tests`：`372/372`，通过。
- `evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：`20/20`，通过；skill 10、baseline 0、tie 0、invalid 0，judge consistency `1.0`。
- 固定 1.5.25 确定性消融：baseline `108/108`，current `108/108`。
- `python tools/sync_adapters.py`：canonical 与发行镜像同步；行尾归一化后工作树无实质 diff。
- `quick_validate.py chinese-official-writing`：通过。
- `git diff --check`：通过。
- canonical 技能树：`edb63a7a20b33d3ccb48e1a0dd0b1623bc6f995b`。

全量 unittest 在沙箱内首次运行时出现 Windows 临时目录 ACL 错误；受控环境以同一 Python 复跑通过，记为运行环境噪声，不改写成产品失败或通过。

## 真实写作证据复用

本轮没有重复生成稿件。原候选的 R01—R03 与 R03N 已由只读审计复核：

- 六份首稿硬边界全部通过；
- R01、R02 为 Candidate 明确胜出；
- R03 初测 Baseline 小胜，固定同题噪声复验 Candidate 小胜，未形成稳定负项；
- 调度参数为 `gpt-5.6-sol / ultra`，运行时二次读取字段为 `unavailable`。

该证据可复用，因为候选完整提交链直接建立在当前稳定 main 上，稳定 main 相对固定 1.5.25 只增加发布回执文档，本产品涉及文件没有差异。

## 未合入的相邻实验

- 联网与来源复核三行减载：工程门和六稿硬边界通过，但匿名盲审 Candidate 1 胜、Baseline 2 胜，已在隔离分支判 `FAIL`，未进入本集成分支。
- AI 算力复核行迁移：专项叶内容完整，但现有 provider 的只审不改路径先于 AI 专项追加返回；保守成功率 35%，低于 70% 门槛，未建立产品 worktree。

## 当前结论

本集成候选只包含已经验证通过的请示/申请复核叶，未混入失败或静态阻断的相邻原子项。它可以作为下一小版本的产品候选，但本记录不修改版本号、不合并 main、不打 tag、不推送、不发布。

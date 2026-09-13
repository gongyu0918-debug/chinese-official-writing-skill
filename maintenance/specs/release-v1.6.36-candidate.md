# v1.6.36 主线同步候选

- 候选分支：`codex/release-v1.6.36-candidate-20260913`。
- 已发布基线：`c0abfeeb3d2a21cfd6ec722de7d8ae534ad68f61`（v1.6.35 tag 解引用提交与远端 `main`）。
- 1.0 主线来源：本机 `main@1ce7112303172478faa2392667a2de1098eb912c`。
- 合并提交：`42b65ed8`，先在独立候选分支汇合已发布历史与 1.0 主线改进；候选验证通过后，本机 `main` 只以 fast-forward 同步已验证提交，远端 `main` 不变。
- 候选范围：同步更聚焦的文种路径、讲话开场人物顺序规则和说明式开场检查，并统一 v1.6.36 版本元数据与派生包。
- 许可范围：仓库、canonical Skill、Agent Skills、Qwen Code、QwenWork、Hermes、OpenClaw、Red SkillHub 和生成的 SkillHub clean package 均继续采用 MIT 许可证；授权随 1.0 版本后续更新延续。
- 更新说明：仅用自然语言说明相对 v1.6.35 的正向改进，不写未发布候选、淘汰过程或内部门禁细节。
- 候选门：核对双边 ancestry 与精确树差异，运行全量 unittest、五套普通 Skill 校验、镜像幂等、MIT 许可一致性和两类清洁包检查。
- 外部边界：本轮只准备候选，不推送远端 `main`、不创建或移动 tag、不创建 Release、不向平台提交，也不联系 2.0 构筑线。

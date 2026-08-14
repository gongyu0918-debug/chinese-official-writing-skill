# Hook 永久移除真实执行结果

## 结论

永久移除规则只放在 `hooks/README.md`，canonical `SKILL.md` 仅保留一条短接引。删除必须由用户二次确认后，使用宿主已有文件能力对当前 Skill 副本执行。

真实链路结果：

- 未确认：Luna max 从 `SKILL.md` 自动读取 `hooks/README.md`，展示复制包根目录与精确范围后停止；副本 51/51 文件路径和 SHA-256 逐字不变。
- Codex 确认阶段：Windows Codex CLI 实际以只读沙箱运行，写入被拒；Hook 与接引均保留，记环境受限，不冒充成功。
- 已确认：Claude Code 通过 OpenCode Go `opencode-go/deepseek-v4-flash`、max，在独立复制包内自行读取说明并执行；删除 `hooks/` 下17个文件，只修改 `SKILL.md` 一处，新增0文件。
- 外部复核：`SKILL.md` 中 `hooks/README.md` 引用为0；references、scripts、LICENSE、agents 均保留；canonical `hooks/` 仍存在，未被测试触碰。
- 删除后写稿：同一复制包以 OpenCode Go `deepseek-v4-flash`、max 起草阅览区巡检情况报告，exit 0，只输出正文；保留48处、2处、正在处理和正常开放，没有推导“其余46处无异常”。
- 真实稿首次出现“正在处理，处理工作正在进行”的同义重复；规则收紧后 R5 复跑不再重复，也未泄露 Hook、路由或自检过程。

## 原始记录

原始执行位于 ignored `output/`，未作为产品文件打包：

- 未确认：`output/real-hook-removal-r2-20260814/`
- Codex 只读确认：`output/real-hook-removal-r3-20260814/`
- Claude 真实删除与删除后写稿：`output/real-hook-removal-claude-r1-20260814/`
- 最终普通写稿 R5：`output/real-writing/static-hook-removed-r5-20260814/`

关键 SHA-256：

- Claude 真实删除 stream：`606396969cc70e032fdc0b5e4185ce5cf50f92a8c2b0459d40f2b909b7d274dc`
- 删除后首稿 stream：`dbab20b40a90c2ce2db3d59bd87bee8487c349438ce5ccc840d4c30ade9272bd`
- 最终普通写稿 R5 stream：`aa5105bbdb2462d0d98f8c490ef4106cb67d8d8ef1878f4aa1868e25d178094c`

外部清单复核确认：删除前51个文件，删除后34个文件；删除17个文件且全部位于 `hooks/`，仅 `SKILL.md` 发生修改，新增0文件，其余33个文件哈希不变。

## 最小工程验证

- Hook 合同、信息选择和可达性：12/12 PASS。
- Skill 镜像接引与普通评测上下文：2/2 PASS。
- canonical quick validate：PASS。
- `sync_adapters.py` 连续执行前后 diff hash 相同，镜像同步幂等。
- canonical `SKILL.md` 只保留一条短接引，删除范围和二次确认只在 `hooks/README.md` 中说明。

## 边界

本证据证明本地 Skill 副本在明确二次确认后能够完整移除 Hook，并继续普通写稿。它不授权自动删除、静默清理、修改宿主插件缓存或删除 canonical 仓库；正式安装的 companion 仍使用宿主原生 disable/remove。

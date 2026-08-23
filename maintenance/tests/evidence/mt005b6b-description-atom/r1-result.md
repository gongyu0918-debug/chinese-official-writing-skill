# MT-005b6b R1 结果

日期：2026-08-24。

## 运行

- Codex CLI `0.144.6`，`opencode-go/deepseek-v4-flash`、low、无 fallback。
- 两臂均为61文件隔离 Skill 树，除 description 中 `实施细则`→`细则` 外逐字一致。
- 顺序：正向 baseline→candidate；私人生活边界 candidate→baseline。

## 正向稿

两臂都自主读取了各自隔离根中的 `SKILL.md`、`information-selection.md` 和 `genre-playbook-institution-rules.md`。初始汇总把基线标为 `missing_exact_skill_trace`，原因是基线使用 cwd 相对路径读取 `SKILL.md`，旧解析器只识别绝对路径；原始 trace 已证明这是解析误报，不是漏触发。

| 臂 | 非空白字数 | 终稿 SHA-256 | 质量结论 |
| --- | ---: | --- | --- |
| baseline | 260 | `8085d269906c9f0e4c2b2ab5c48615b1d4c02d7e48a22602ac388da1357ce2d8` | 事实、主体、时间、检查项、记录字段和施行日期完整；无材料外报告、整改、奖惩或依据。 |
| candidate | 245 | `a11ab85a557450daf7d43bba9fb36750c4902792c56a676302c13be04d457f40` | 同样完整；“加强设备日常管理、保障设备正常运行”属于标题事项直接支持的一般目的，没有形成新增职责、流程或既成成效。 |

候选没有独有硬回退。两稿章条组织略有差异，均可直接使用。

## 私人生活边界

两臂均未读取公文 Skill，因此候选新增泛词 `细则` 没有造成误触发。机械 required 检查把 `20:00`、`下周`、`我们俩` 等同义写法误报为缺词，不作为公文 Skill 的硬回退。两臂都补了用户未给的家务细节，说明该题只用于判断 Skill 是否误触发，不用于评价公文产品质量。

## 当前判断

R1 支持候选：正向真实触发、成稿安全，边界不误触发。但只做一次路由不足以排除随机性，先不改产品；R2 只反序复测同一正向稿，不重复无误触发的边界题。

原始证据保留在仓内忽略目录 `output/mt005b6b-codex-cli-20260824/`。四份 trace SHA-256：

- 正向 baseline：`8a8e74ac2c2ea02b2bc564a851c4592e0894c3002c48dfd3b23f9bdf7ce380ab`
- 正向 candidate：`2e9d0c41b2bdf1ad12d6ac0078c323588e6544780a0d76244698c65af9dbbd8c`
- 边界 candidate：`d7c93df813aa8888fef040aabdae92060295085ed2aa53d71d7a3130cc3dea54`
- 边界 baseline：`54e4f2aa2da5ce092576b32606536f5b876956f7f466e3a08de48201455e6594`

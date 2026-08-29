# HK-004-QWENWORK-R1 五提交复核

复核点：`codex/qwenwork-r1@0bdbcf72`，相对固定基线 `main@6e4e8914431c5674a3fda87ab42d35ed8a531e8c` 共5次提交。

## 范围

- canonical `chinese-official-writing/` 差异：0文件。
- canonical `SKILL.md`/description 差异：0文件。
- canonical Hook 差异：0文件。
- 产品新增仅为 `packages/qwenwork/` 的无 Hook 机械镜像和说明；其余是同步器、直接测试与维护证据。
- `MT-004a` 此时只增加预注册和可复现 runner，没有产品候选；后续结果必须选择性回填，不能把未决登记留在 QwenWork 候选。

## 真实结果与轻量消融

- QwenWork 包路径 Alibaba Token Plan 2 DeepSeek max 真稿精确读取隔离包，89字事实材料形成143字完整采购申请，技术失败0、硬失败0。
- 包路径与 canonical 写作内容相同，QwenWork 产品差异只影响安装面；因此不把这份 Codex CLI 真稿冒充 QwenWork 在线触发或 Hook 生命周期。
- 两次组织 ZIP 生成同 hash，唯一顶层目录、无不安全路径、无 Hook/门禁 entry。

## 回归

```text
sync_adapters.py: PASS，五个普通包面同步且复跑后工作树干净
focused unittest: 100/100 PASS
py_compile: 4个本轮 Python 文件 PASS
JSON parse: 2个案例文件 PASS
git diff --check: PASS
```

## 复核结论

QwenWork 静态包候选范围与官方边界一致，没有把普通 Skill 发现冒充 Hook 能力；未发现包体、许可、镜像、写稿或状态硬回退。候选仍为 `NOT_MERGED`，不改变 `main`、tag 或发布面。下一步只同步 `MT-004a` 已完成的真实复现结论，再做最终状态/链接检查。

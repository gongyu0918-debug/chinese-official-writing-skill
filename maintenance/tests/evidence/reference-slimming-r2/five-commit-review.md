# References减载R2累计提交复核

## 固定点

- 基线：`main@6e4e8914431c5674a3fda87ab42d35ed8a531e8c`
- 复核HEAD：`52a8d62fb2719fe1cea8c9f660da8dcd2f3d0429`
- 分支：`codex/reference-slimming-r2`
- `main` 是复核HEAD祖先；根 `main` 工作树和本分支工作树均干净。

## 范围复核

`main...HEAD` 共11个文件、760行新增：3个状态/证据索引文件，6个实验记录/配置文件和2个可复现实验脚本。`chinese-official-writing/`、`hooks/`、`packages/` 相对基线均为零差异；候选窄叶及入口路由已经完整恢复。差异中没有 `output/`、raw模型输出、环境文件、凭据、令牌、Cookie或发布文件。

## 轻量消融

- 直接消融：`git diff --exit-code main...HEAD -- chinese-official-writing hooks packages` 返回0，证明三个减载候选均未残留在产品、Hook或发行包中。
- R2汇总重放前后SHA-256均为 `6195E524EA4A9065860E50AB70F961FBA8113CF9C1B65C4F3CF9492644E0FDC5`，15条记录的终态汇总可确定性复算。
- R2质量裁决仅使用材料事实/状态遗漏、材料外具体程序、正文包装与实际读取，不把合理一层原因、即时作用、低强度预期、简单算术或“正文短于完整提示词”作为失败。

## 验证

- `py -3 -m py_compile .../run_probe.py .../run_ab.py`：PASS。
- `cases.json`、`ab_config.json`：PowerShell `ConvertFrom-Json` 均PASS。
- 敏感信息关键词扫描：无命中。
- Skill Creator `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 新增证据链接目标：3/3存在。
- `git diff --check main...HEAD`：PASS。

## 结论

复核未发现候选产品字节、原始模型输出、秘密或平台发布状态误入。该分支只适合选择性合入实验工具、证据和状态索引；不带来产品规则、Hook、包体或版本变化。三个原子均已进入REJECTED或TERMINATED终态，不留HOLD。

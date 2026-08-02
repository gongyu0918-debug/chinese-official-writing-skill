# 场景化套话 lint：1.5.33 独立重放预注册

## 基线与目标

- 固定发布基线：`1ea3f5b6ccccd5ef772803e264087adcf2fb5515`（1.5.33 产品提交）。
- 隔离分支：`codex/scene-filler-lint-v1533-r1`。
- 历史实现来源：`c9ec349b`。本轮只移植该提交中两条 `low / scene-filler-cluster` 检测规则与独立单测，并在 1.5.33 上重新验证；不沿用旧结果代替复现。
- 目标：定位同一句中连续叠加的礼仪、氛围和圆满收束套话，验证其能否形成低误报的脚本净收益。

## 精确修改边界

允许修改：

1. canonical `chinese-official-writing/scripts/prose_lint.py`；
2. 由 `tools/sync_adapters.py` 机械生成的五套发行镜像；
3. `tests/test_scene_filler_lint.py`；
4. 本轮预注册与结果证据。

保持不变：

- `SKILL.md`、全部 reference、写作 Prompt 与文种路由；
- `review_gate.py`、FSM、Hook、自动改稿与交付流程；
- 版本号、README、发布文件和主线；
- 命中只给 `low` 级提示，不删除、不替换正文，`--fail-on medium` 不因该提示失败。

## 预注册样本

### 正例 5 条

沿用历史候选已经公开的五种成簇机制，但在 1.5.33 上重新执行：

1. 会见评价与合影留念同句；
2. 合影留念与现场氛围评价同句；
3. 现场氛围评价与圆满结束同句；
4. 气氛评价与取得圆满成功同句；
5. 现场氛围评价与掌声描写同句。

要求 5/5 均产生 `scene-filler-cluster / low`。

### 误报集 27 项

1. 独立测试中的 8 条合法反例；
2. `tests/fixtures/clean_prose_corpus.json` 的 12 条脱敏合格公文段落；
3. 以下 7 篇历史真实首稿，仅按本检测器目标视为 clean，不据此宣称其整体写作质量无瑕疵：
   - `tests/evidence/candidate-b-writing-20260715/terra-t01.md`
   - `tests/evidence/candidate-b-writing-20260715/terra-t02.md`
   - `tests/evidence/candidate-b-writing-20260715/terra-t03.md`
   - `tests/evidence/candidate-b-writing-20260715/terra-t04.md`
   - `tests/evidence/candidate-b-writing-20260715/luna-t01.md`
   - `tests/evidence/candidate-b-writing-20260715/luna-t03.md`
   - `tests/evidence/candidate-b-writing-20260715/luna-t04.md`

要求 27 项均无 `scene-filler-cluster` 命中。历史真实首稿必须用候选 CLI 实际扫描，不能只依赖正则静态判断。

## 工程验证

依次运行：

1. `python -m unittest tests.test_scene_filler_lint tests.test_review_regressions`
2. `python -m unittest discover -s tests`
3. `npm run eval:official-writing:smoke`
4. 固定 1.5.33 确定性消融
5. `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`
6. canonical 与发行镜像哈希一致性检查
7. `git diff --check`

## 判定

- `PASS / 可合并`：正例 5/5；误报 0/27；全部命中为 `low`；工程回归无新增失败；产品 diff 保持在预注册范围内。
- `MIXED / 保持隔离`：存在非阻断误报、样本来源无法复核或实现范围扩大。
- `FAIL / 不合并`：合法旧稿出现可归因误报、medium/high 阻断、脚本或工程回归失败。

真实自然正例召回率仍记为 `unavailable`；5/5 只说明预注册机制可以被定位。

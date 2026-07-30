# D2 中文紧邻占位盲区独立复核

日期：2026-07-30
结论：`PASS / READY TO INTEGRATE`

## 对象与证据边界

- 外部归档：
  `C:\Users\admin\Desktop\中文公文写作-1.5.29迭代最终版-含git历史.rar`
- 归档 SHA-256：
  `64E437B7B4F81E53EA78DCCC2F70E0960F138967560418CD8D8D5EEA57AB3B47`
- 外部 D2 产品提交：`873c25db47159ef57c5d90aadbdda2ec3686f70e`
- 外部合并提交：`2281040`
- 外部后续写作测试提交：`88a5881`，与 D2 产品差异无关。
- 独立复现基线：`origin/main=ce2035948457da1ba4ddda06ce68d4dbeb3ef573`
- 独立复现提交：`7d7613ccd683452937b2aeb970afdf07200c09a0`

外部记录提到 C903 真实漏检，但归档没有保存 C903 原始成稿；因此只采信
可直接复现的规则盲区，不把 C903 的叙述当作原始链路证据。

## 复现结果

旧规则：

`X{2,}(?![A-Za-z\u4e00-\u9fff])`

会放过紧接中文的 `XX类`、`XX系统`、`XX项`。外部实现使用 31 个类别词
硬编码，本次没有照搬；独立实现只识别“两个及以上大写 ASCII X 紧接中文”
的形态，并保留既有 `XX发〔2026〕1号` 文号形式。

命中样本：

- `XX类项目检测能力不足`
- `兼容XX系统`
- `XX项指标未达标`
- `覆盖XX业务场景`
- `XX型号设备待采购`

clean 与豁免样本：

- `社会保障类126件`
- `市场主体类82件`
- `检测系统运行正常`
- `XX发〔2026〕1号`

## 修改边界

- canonical 和五份发行镜像的 `prose_lint.py` 各增加一条模式；
- 增加 `tests/test_placeholder_blind_spot_fix.py`；
- 不修改写作 Prompt、文种路由、reference 加载、输出模式或交付流程；
- 脚本仍只定位，不自动改稿。

## 实际验证

外部归档：

- `python -m unittest discover -s tests -v`：444/444 通过；
- `quick_validate.py chinese-official-writing`：通过；
- clean corpus 聚焦测试：通过；
- `git diff --check`：通过。

独立复现：

- `python -m unittest discover -s tests -v`：394/394 通过；
- `quick_validate.py chinese-official-writing`：通过；
- clean corpus、中文紧邻、大小写边界和文号豁免测试：通过；
- `git diff --check origin/main..HEAD`：通过。

主线程另行复跑
`python -m unittest tests.test_placeholder_blind_spot_fix -v`：4/4 通过。

## 判定与剩余边界

该改动只补足确定性检测盲区，clean corpus 无误报，不改变写稿行为，属于
相对 `origin/main` 的净增益，可进入后续集成分支。当前远端
`origin/main` 尚不包含 `7d7613cc`，外部归档中的“已合并 main”只表示其
自身历史，不代表本仓库主线已经吸收。

小写 `xx`、混合大小写 `Xx` 和全角 `ＸＸ` 仍不检测。本轮没有真实样本
证明这些形态是共同风险，故不扩大规则。

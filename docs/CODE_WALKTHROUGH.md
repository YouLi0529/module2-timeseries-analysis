# 项目代码逐块讲解

本文档解释这次项目的全部代码，包括主 notebook、`src/` 里的每个 `.py` 文件、`run_all.py` 和测试文件。目标是让你和 Li Ling 不只是能运行项目，也能说清楚每一步为什么这样写。

## 1. 项目整体逻辑

整条分析链是：

```text
raw CSV files
-> 读取时间序列
-> 聚合成 monthly mean
-> Section 1: 趋势、平稳性和去均值/去趋势
-> Section 2: ACF/PACF 和 AR/ARMA 候选阶数
-> Section 3: AR/ARMA 拟合、残差诊断和模型选择
-> Section 4: 合成时间序列、输沙量和 Ill 对 Rhein 的相对贡献
-> Section 5: Q 和 C 是否可以看作独立变量
-> 输出 figures 和 tables
```

notebook 的职责是展示和串联分析；具体函数放在 `src/*.py` 里。这符合 PDF 要求：notebook 保持清爽，计算逻辑放在独立 `.py` 文件中。

## 2. Notebook 逐块讲解

文件：

```text
notebooks/Module2_Timeseries_Analysis.ipynb
```

### Cell 1: 标题和项目说明

这是 markdown cell，说明项目是 `Module 2 - Timeseries Analysis`，并提醒读者原始 10 分钟 / 15 分钟数据会先聚合成 monthly mean。

你需要能解释：

- 为什么不是直接用原始高频数据建模。
- PDF 明确要求使用 monthly data aggregates。

### Cell 2: 导入包、设置路径、读取数据

这个 code cell 做几件事：

- 导入 `Path`、`sys`、`matplotlib.pyplot`、`pandas`。
- 设置 `PROJECT_ROOT`，保证从 repo root 或 notebook 文件夹打开都能正常运行。
- 设置路径：`RAW_DATA_DIR`、`PROCESSED_DATA_DIR`、`FIGURE_DIR`、`TABLE_DIR`。
- 把项目根目录加入 `sys.path`，这样 notebook 能 import `src/` 里的模块。
- 从 `src/` 导入所有分析函数和绘图函数。
- 调用 `ensure_project_directories(PROJECT_ROOT)` 创建必要文件夹。
- 调用 `load_project_monthly_data(RAW_DATA_DIR)` 读取 raw data 并聚合到 monthly mean。
- 调用 `save_monthly_tables(...)` 保存 processed monthly tables。
- 打印每个 station-variable 有多少个月度数据。

关键变量：

```python
monthly_data
```

它的结构是：

```python
monthly_data["Gisingen"]["Q"]
monthly_data["Gisingen"]["C"]
monthly_data["Diepoldsau"]["Q"]
monthly_data["Diepoldsau"]["C"]
```

每一个都是 `pandas.Series`，index 是月份。

### Section 1 title cell

markdown 标题：

```text
Section 1: Timeseries review
```

PDF 要求每个 section 都有 title markdown cell。

### Section 1 MAIN cell

代码：

```python
review_results = run_timeseries_review(monthly_data, alpha=0.05)
normalized_series = normalized_series_collection(review_results)
```

功能：

- 对四条月度序列分别做线性趋势检验。
- 用 5% 显著性水平判断 slope 是否显著。
- 运行 ADF test 作为 stationarity 的辅助证据。
- 如果 trend 显著，去除线性趋势。
- 如果 trend 不显著，只减去均值。
- 生成均值接近 0 的 normalized series，供 AR/ARMA 使用。

关键变量：

```python
review_results
normalized_series
```

你需要能解释：

- `alpha=0.05` 是 5% significance level。
- slope p-value 小于 0.05 才认为线性趋势显著。
- AR/ARMA 通常需要零均值、近似平稳的序列。

### Section 1 PLOT cell

代码调用：

```python
plot_monthly_timeseries(...)
```

输出图：

```text
outputs/figures/section1_monthly_timeseries.png
```

图中有四个 panel：

- Gisingen Q
- Gisingen C
- Diepoldsau Q
- Diepoldsau C

每个 panel 显示 monthly mean 时间序列，并叠加 trend line。

### Section 1 PRINT cell

代码调用：

```python
print(format_timeseries_review(review_results))
```

打印内容：

- slope per month
- slope p-value
- trend 是否在 5% 下显著
- ADF p-value
- stationarity note
- removed component 是 mean 还是 linear trend
- 去均值/去趋势后的 mean 和 variance

### Section 1 comment cell

这段 markdown 强调：统计趋势不等于因果证明。

你需要能说：

- discharge trend 可能来自气候变化、流域变化、水电调控、rating curve 更新或测量系统变化。
- 不能只因为 p-value 显著就说一定是某个物理原因造成。

### Section 2 MAIN cell

代码：

```python
order_results = analyse_acf_pacf_collection(normalized_series, nlags=24)
```

功能：

- 对每条 normalized series 计算 ACF 和 PACF。
- 加 approximate 95% confidence interval。
- 找出显著 lag。
- 根据 ACF/PACF 提出 AR 和 ARMA 候选阶数。

关键变量：

```python
order_results
```

你需要能解释：

- ACF 看序列和过去月份的相关性。
- PACF 看扣除中间 lag 后的直接相关性。
- PACF 对选择 AR order 有帮助。
- ACF 对判断 MA memory 有帮助。

### Section 2 PLOT cell

代码调用：

```python
plot_acf_pacf_grid(...)
```

输出图：

```text
outputs/figures/section2_acf_pacf.png
```

图中每条序列都有 ACF 和 PACF，并显示置信界限。

### Section 2 PRINT cell

代码调用：

```python
print(format_order_selection(order_results))
```

打印内容：

- AR candidate order
- ARMA candidate order
- significant ACF lags
- significant PACF lags
- 阶数选择理由

### Section 2 comment cell

这段 markdown 解释：不能机械地给两个站点使用同一个 model order。

你需要能说：

- Gisingen 是 Ill tributary。
- Diepoldsau 是 Rhein 下游站点。
- 流域规模、汇流、调控、混合过程都可能导致不同 autocorrelation structure。

### Section 3 MAIN cell

代码：

```python
evaluation_results = evaluate_model_collection(
    normalized_series,
    order_results,
    nlags=24,
    alpha=0.05,
)
```

功能：

- 对每条序列拟合 AR candidate 和 ARMA candidate。
- 计算 empirical ACF 和 theoretical model ACF。
- 计算 residuals。
- 对 residuals 做 ACF。
- 用 Ljung-Box test 检查残差是否仍有 temporal dependence。
- 用 probability plot / PPCC / normality p-value 检查残差正态性。
- 根据 residual independence、BIC、AIC 和 parsimony 选择最终模型。

关键变量：

```python
evaluation_results
```

你需要能解释：

- 一个模型拟合后，残差应该尽量像 white noise。
- 如果 residual ACF 还有显著 lag，说明模型没有解释完时间相关性。
- BIC 更偏向简单模型，AIC 更偏向预测表现。

### Section 3 PLOT cell

代码调用：

```python
plot_model_diagnostics(...)
```

输出图：

```text
outputs/figures/section3_model_diagnostics.png
```

图中包含：

- empirical ACF vs theoretical ACF
- residual ACF
- residual probability plot

### Section 3 PRINT cell

代码调用：

```python
print(format_model_evaluation(evaluation_results))
```

打印内容：

- AR / ARMA order
- AIC 和 BIC
- Ljung-Box p-value
- residuals 是否在 5% 下可视为 independent
- PPCC 和 normality p-value
- chosen model

### Section 3 comment cell

这段 markdown 说明 parsimony：

- 模型越复杂，不一定越好。
- 如果 ARMA 只带来很小改善，却增加很多参数，就要谨慎。
- 如果残差诊断明显改善，则 ARMA 的复杂度可能是合理的。

### Section 4 MAIN cell

代码：

```python
sediment_results = run_sediment_influence_analysis(...)
```

功能：

- 使用 Section 3 选出的模型生成 synthetic monthly series。
- 生成 10 条路径，每条 10 年，也就是 120 个月。
- normalized synthetic series 用来和 historical normalized data 比较。
- 为了计算 sediment mass，再把 synthetic series 恢复到 physical scale。
- 计算 `M(t) = C(t) * Q(t)`。
- 计算 monthly / yearly sediment yield summaries。
- 估计 Ill/Gisingen 对 Diepoldsau/Rhein 的相对贡献。
- 如果有结果，保存 synthetic contribution table。

关键变量：

```python
sediment_results
```

你需要能解释单位：

```text
C: g/L
Q: m3/s
1 g/L = 1 kg/m3
C[g/L] * Q[m3/s] = kg/s
```

所以代码中 `C * Q` 可以直接得到 kg/s。

### Section 4 PLOT cell

代码调用：

```python
plot_synthetic_series(...)
plot_sediment_yields(...)
```

输出图：

```text
outputs/figures/section4_synthetic_normalized_series.png
outputs/figures/section4_sediment_yields.png
```

第一张图比较 historical normalized data 和 10 条 synthetic paths。

第二张图展示 observed monthly sediment mass climatology 和 synthetic contribution。

### Section 4 PRINT cell

打印内容：

- observed sediment mass summaries
- Ill/Gisingen 对 Diepoldsau/Rhein 的 observed contribution
- synthetic path contribution
- 每条 synthetic series 的 mean、std、variance、lag-1 autocorrelation

### Section 4 comment cell

这段 markdown 解释：

- synthetic series 不是确定性未来预测。
- 它用于比较 long-term statistical properties。
- station records 非完全同步，因此贡献率是 preliminary statistical estimate。
- Q 和 C 独立模拟会影响 `C * Q` 的产品结构。

### Section 5 MAIN cell

代码：

```python
dependency_results = run_dependency_analysis(monthly_data)
```

功能：

- 对每个 station，把 Q 和 C 按月份对齐。
- 计算 Pearson correlation。
- 计算 Spearman correlation。
- 计算 Kendall correlation。
- 用 p-values 判断 Q 和 C 是否可以简单看作 independent。

关键变量：

```python
dependency_results
```

### Section 5 PLOT cell

代码调用：

```python
plot_dependency_scatter(...)
```

输出图：

```text
outputs/figures/section5_q_c_dependency.png
```

图展示每个 station 的 Q-C joint distribution。

### Section 5 PRINT cell

打印内容：

- aligned monthly observations
- Pearson r 和 p-value
- Spearman rho 和 p-value
- Kendall tau 和 p-value
- independence interpretation

### Section 5 comment cell

这段 markdown 解释为什么独立模拟 Q 和 C 有风险：

- sediment mass 是 `M = C * Q`。
- 如果 Q 和 C 实际相关，独立模拟会破坏 joint behaviour。
- 更好的方法包括 rating curve、copula、VAR/VARMA、conditional simulation。

## 3. `src/data_loading.py`

这个模块负责数据读取、数据结构整理和月尺度聚合。

### `StationData`

类型别名：

```python
Dict[str, Dict[str, pd.Series]]
```

它代表这种结构：

```python
data["Gisingen"]["Q"]
data["Gisingen"]["C"]
data["Diepoldsau"]["Q"]
data["Diepoldsau"]["C"]
```

### `DataNotFoundError`

自定义错误类型。原始数据缺失时，代码不会给一个模糊的系统错误，而是说明期望哪些文件和列。

### `SeriesSpec`

`dataclass`，描述一条需要读取的序列：

- station 名称；
- variable 名称；
- 文件名中应该包含哪些关键词；
- 优先识别哪些 value column。

### `SERIES_SPECS`

定义四条核心序列：

- Gisingen Q
- Gisingen C
- Diepoldsau Q
- Diepoldsau C

这里也定义了可接受的列名，比如 `q_m3s`、`ssc_gL`、`Q`、`C`、`concentration`。

### `expected_data_message()`

返回原始数据格式说明。测试中也会检查数据缺失时是否能给出清楚提示。

### `ensure_project_directories(project_root)`

创建项目需要的目录：

```text
data/raw
data/processed
outputs/figures
outputs/tables
outputs/reports
```

### `list_supported_data_files(data_dir)`

列出 `data/raw/` 中支持的文件：

- `.csv`
- `.xlsx`
- `.xls`

如果目录不存在，抛出 `DataNotFoundError`。

### `_normalise_name(...)`

内部辅助函数，把列名变成更容易比较的形式，比如去掉空格、转小写。

### `_find_datetime_column(...)`

从列名中寻找时间列。可识别：

```text
timestamp, datetime, date_time, date, time
```

### `_find_value_column(...)`

根据候选列名寻找数值列。比如 Q 文件优先找 `q_m3s`，C 文件优先找 `ssc_gL`。

### `read_timeseries_file(...)`

读取单个 CSV 或 Excel 文件。

它会：

- 读取表格；
- 找时间列；
- 找数值列；
- 转换 datetime；
- 转换 numeric values；
- 删除无效值；
- 按时间排序；
- 删除重复 timestamp。

输出是：

```python
pd.Series
```

index 是 `DatetimeIndex`。

### `_find_file_for_spec(...)`

根据 `SeriesSpec` 在 raw 文件夹中找到对应文件。例如 Gisingen Q 会找文件名中同时包含 `q` 和 `gisingen` 的文件。

### `_try_load_combined_long_file(...)`

备用读取逻辑。如果不是四个独立文件，而是一个 long-format 文件，也可以尝试读取。

long-format 例子：

```text
datetime, station, variable, value
```

### `load_project_raw_data(data_dir)`

读取全部四条 raw series，并返回 `StationData`。

如果缺文件，它会调用 `expected_data_message()` 给出清楚说明。

### `aggregate_monthly_mean(series)`

把任意时间步长的序列聚合成 monthly mean：

```python
series.resample("MS").mean()
```

`MS` 表示 month start，所以每个月的时间戳会放在当月第一天。

### `aggregate_project_monthly(raw_data)`

对所有 station 和 variable 批量做 monthly mean。

### `load_project_monthly_data(data_dir)`

notebook 开头调用的主函数：

```text
读取 raw data -> 聚合 monthly mean -> 返回 monthly_data
```

### `flatten_station_data(data)`

把嵌套结构变成扁平 label：

```text
Gisingen_Q
Gisingen_C
Diepoldsau_Q
Diepoldsau_C
```

这样 Section 1-3 可以方便循环。

### `align_station_q_c(monthly_data, station)`

对一个 station 的 Q 和 C 按月份对齐，返回两列 DataFrame：

```text
Q, C
```

Section 4 和 Section 5 都需要这个函数。

### `save_monthly_tables(...)`

把 monthly mean 保存到 `data/processed/`，方便检查和复现。

## 4. `src/section1_timeseries_review.py`

这个模块对应 Section 1：timeseries review。

### `linear_trend_test(series, alpha=0.05)`

拟合线性趋势：

```text
value = intercept + slope * month_index
```

使用 `scipy.stats.linregress`。

返回：

- slope
- intercept
- r value
- p-value
- standard error
- significant flag
- fitted trend series

要点：

- slope 单位是每个月的变化量。
- p-value 小于 0.05 时，认为 slope 在 5% 显著性水平下显著。

### `adf_stationarity_test(series)`

运行 Augmented Dickey-Fuller test。

解释：

- p-value < 0.05：拒绝 unit-root null，支持 stationarity。
- p-value >= 0.05：不能强有力支持 stationarity。

### `normalize_or_detrend(series, trend_result)`

根据 trend test 决定处理方式：

如果 trend 显著：

```text
series - fitted trend - residual mean
```

如果 trend 不显著：

```text
series - mean
```

输出的 normalized series 均值应接近 0。

### `review_one_series(series, alpha=0.05)`

对一条序列完成：

```text
linear trend test -> ADF test -> normalize/detrend
```

### `run_timeseries_review(monthly_data, alpha=0.05)`

对四条序列全部运行 Section 1。

### `normalized_series_collection(review_results)`

从 Section 1 结果中提取 normalized series，供 Section 2 和 Section 3 使用。

### `format_timeseries_review(review_results)`

把 Section 1 结果整理成 notebook 中可读的打印文本。

## 5. `src/section2_timeseries_modelling.py`

这个模块对应 Section 2：ACF/PACF 和模型阶数选择。

### `default_nlags(series, maximum=36)`

选择安全的 lag 数量。它避免对短序列使用过多 lag。

### `compute_acf_pacf(series, nlags=None)`

计算：

- ACF
- PACF
- lag array
- approximate 95% confidence bound

置信界限近似为：

```text
1.96 / sqrt(n)
```

### `significant_lags(values, confidence)`

找出超过置信界限的 lag：

```text
abs(correlation) > confidence
```

lag 0 不参与判断。

### `select_candidate_orders(...)`

根据 ACF/PACF 提出：

- AR order: `(p, 0, 0)`
- ARMA order: `(p, 0, q)`

代码把最大阶数限制在 6，避免模型太复杂或不稳定。

### `analyse_acf_pacf_collection(...)`

对四条 normalized series 全部运行 ACF/PACF 分析和阶数选择。

### `format_order_selection(...)`

把 Section 2 结果整理成 notebook 中可读的打印文本。

## 6. `src/section3_model_evaluation.py`

这个模块对应 Section 3：模型拟合、诊断和选择。

### `fit_arima_model(series, order)`

使用 `statsmodels` 拟合 ARIMA 模型。

本项目中：

```text
d = 0
```

所以它实际用于 AR 或 ARMA，而不是带差分的 ARIMA。

`trend="n"` 表示不再额外拟合常数项，因为 Section 1 已经处理成接近 zero-mean。

### `theoretical_arma_acf(fit_result, nlags)`

根据拟合出来的 AR 和 MA 参数计算 theoretical ACF。

这个结果会和 empirical ACF 画在同一张图中。

### `residual_normality_diagnostics(residuals)`

检查 residual normality。

输出：

- PPCC
- Shapiro p-value 或 normaltest p-value
- interpretation

PPCC 是 probability plot correlation coefficient，用来衡量残差在 normal probability plot 上有多接近直线。

### `evaluate_model(series, order, nlags=24, alpha=0.05)`

对一个候选模型完成全部诊断。

它会计算：

- AIC
- BIC
- residuals
- empirical ACF
- theoretical ACF
- residual ACF
- Ljung-Box p-value
- residual independence flag
- normality diagnostics

### `choose_best_model(candidate_results)`

模型选择规则：

1. 优先考虑 residuals 通过 Ljung-Box independence test 的模型。
2. 在通过的模型中选 BIC 最低的。
3. 如果没有模型通过 independence test，就选 BIC 最低的，但解释时要承认模型仍有不足。

### `evaluate_model_collection(...)`

对四条序列分别拟合 AR 和 ARMA candidate，并选择 final model。

### `format_model_evaluation(...)`

把 Section 3 模型诊断结果整理成 notebook 中可读的打印文本。

## 7. `src/section4_sediment_influence.py`

这个模块对应 Section 4：合成序列和 sediment influence。

### `concentration_gL_times_discharge_m3s_to_kg_s(...)`

计算：

```text
M = C * Q
```

单位逻辑：

```text
1 g/L = 1 kg/m3
C[g/L] * Q[m3/s] = kg/s
```

所以不需要额外乘 1000 或除 1000。

### `compute_sediment_yields(mass_kg_s)`

根据 monthly mass rate 计算：

- 每月 kg/s 平均质量率；
- 每个月秒数；
- 每月总质量 kg；
- 每月总质量 tonnes；
- monthly climatology；
- yearly total tonnes。

### `_innovation_scale(fit_result)`

内部辅助函数，用 residual standard deviation 估计 synthetic series 的噪声尺度。

### `simulate_normalized_paths(...)`

生成 synthetic normalized time series。

默认参数：

```python
periods=120
n_paths=10
```

即 10 条路径，每条 10 年月度数据。

### `restore_physical_scale(...)`

把 normalized synthetic series 恢复到 physical scale，用于计算 sediment mass。

如果 Section 1 去掉的是 mean，就加回 mean。

如果 Section 1 去掉的是 linear trend，就加回 extrapolated trend 和 residual offset。

如果恢复后出现负数，会 clip 到 0，因为负的 discharge 或 concentration 没有物理意义。

### `compare_synthetic_statistics(...)`

比较 historical normalized series 和 synthetic paths 的统计量：

- mean
- standard deviation
- variance
- lag-1 autocorrelation

### `observed_sediment_summary(monthly_data)`

计算 observed sediment mass summaries。

它还会在两个站点有重叠月份时，计算：

```text
Gisingen mass / Diepoldsau mass * 100%
```

这代表 Ill/Gisingen 相对于下游 Rhein/Diepoldsau 的 sediment mass contribution。

### `run_sediment_influence_analysis(...)`

Section 4 的主函数。它整合：

```text
observed sediment summary
synthetic normalized series
restored physical synthetic series
synthetic sediment mass
synthetic contribution ratio
```

### `format_sediment_influence(results)`

把 Section 4 的结果整理成 notebook 中可读的打印文本。

## 8. `src/section5_dependency_analysis.py`

这个模块对应 Section 5：判断 Q 和 C 是否可以独立模拟。

### `correlation_tests(frame)`

输入是一个对齐后的 DataFrame：

```text
Q, C
```

它计算：

- Pearson correlation：线性相关。
- Spearman correlation：单调相关。
- Kendall tau：秩相关。

每个都有 p-value。

如果任意 test 在 5% 下拒绝 no association，就说明把 Q 和 C 当成独立变量是有问题的。

### `run_dependency_analysis(monthly_data)`

对两个 station 分别运行 Q-C dependency analysis。

### `format_dependency_results(dependency_results)`

把 Section 5 结果整理成 notebook 中可读的打印文本。

## 9. `src/plotting.py`

这个模块集中管理所有绘图函数，让 notebook 不被绘图细节塞满。

### `_save(fig, output_path)`

内部辅助函数。如果给了路径，就保存 figure。

### `plot_monthly_timeseries(...)`

Section 1 图：

- Q 和 C 的完整 monthly series；
- trend line；
- 四个 station-variable panel。

### `plot_acf_pacf_grid(...)`

Section 2 图：

- 每条序列的 ACF；
- 每条序列的 PACF；
- 95% confidence bounds。

### `plot_model_diagnostics(...)`

Section 3 图：

- empirical ACF vs theoretical ACF；
- residual ACF；
- residual probability plot。

### `plot_synthetic_series(...)`

Section 4 图：

- historical normalized series；
- 10 条 synthetic normalized paths。

### `plot_sediment_yields(...)`

Section 4 图：

- observed monthly sediment mass climatology；
- synthetic Ill/Rhein contribution by path。

### `plot_dependency_scatter(...)`

Section 5 图：

- 每个 station 的 Q-C scatter plot。

## 10. `run_all.py`

这是命令行 smoke test。

基础运行：

```powershell
python run_all.py
```

它运行：

```text
load monthly data
Section 1
Section 2
```

完整运行：

```powershell
python run_all.py --full
```

它额外运行：

```text
Section 3
Section 4
Section 5
```

这个文件的作用：

- 不打开 Jupyter 也能检查核心 pipeline。
- 每次 PR merge 前可以快速验证。
- 证明 `main` 是 runnable 的。

## 11. `tests/test_basic_pipeline.py`

这个测试文件保护项目最关键的行为。

### `test_missing_data_error_is_clear`

检查 raw data 缺失时，代码会抛出清楚的 `DataNotFoundError`。

### `test_monthly_aggregation_on_artificial_data`

用很小的人工数据检查 monthly mean 是否正确。

### `test_sediment_mass_unit_conversion`

检查 sediment mass 单位转换是否正确。

例子：

```text
1.0 g/L * 2.0 m3/s = 2.0 kg/s
```

### `test_main_source_files_import`

检查所有主要 source modules 都能 import，能快速发现语法错误或依赖缺失。

### `test_notebook_is_present`

检查主 notebook 是否存在。

## 12. 你和 Li Ling 都应该能解释的内容

项目答辩或老师提问时，两个人都应能解释：

- 为什么先做 monthly aggregation。
- stationarity 为什么影响 AR/ARMA。
- slope p-value 如何决定 mean removal 或 trend removal。
- ACF 和 PACF 的区别。
- AR 和 ARMA 的区别。
- 为什么 residual diagnostics 很重要。
- Ljung-Box test 在检验什么。
- `C * Q` 为什么得到 kg/s。
- 为什么 Q 和 C 可能不是 independent。
- Git 上如何通过 branch、PR、review、merge 协作。

## 13. 简短口头解释模板

可以这样概括整个代码：

```text
Our notebook loads discharge and suspended sediment concentration data for Gisingen and Diepoldsau, aggregates the original 10-minute and 15-minute observations to monthly means, and then runs five analysis sections. Section 1 checks trends and prepares zero-mean normalized series. Section 2 uses ACF and PACF to select candidate AR and ARMA orders. Section 3 fits and evaluates those models using theoretical ACF, residual ACF, Ljung-Box tests, and normality diagnostics. Section 4 generates 10 synthetic 10-year monthly paths and estimates sediment mass as C times Q. Section 5 tests whether Q and C can be considered independent. The main logic is kept in src/*.py, while the notebook only calls functions, plots results, prints summaries, and comments on interpretation.
```


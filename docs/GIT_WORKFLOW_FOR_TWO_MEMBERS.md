# 你和 Li Ling 的 Git / GitHub 协作流程

本文档按你们这次真实分工来写：

- 你：GitHub 仓库创建者、主要邀请者、Member A。
- Li Ling：被邀请的协作者、Member B。

核心原则只有一个：`main` 分支必须始终保持可运行。你们两个人都不要直接在 `main` 上开发。每个任务都开自己的 feature branch，完成后在 GitHub 上开 Pull Request，让另一个人 review，通过后再合并。

## 0. 当前本地仓库状态

本地项目已经在这个文件夹里创建好了：

```text
module2-timeseries-analysis/
```

进入仓库：

```powershell
cd "k:\study_courses\graduates_study_courses\second semester\water resources lab\Assignment2\module2-timeseries-analysis"
```

检查当前状态：

```powershell
git status
git log --oneline --decorate -3
```

理想状态应该类似：

```text
On branch main
nothing to commit, working tree clean
```

如果 `git status` 显示有修改，先确认这些修改要不要提交，再开始新的 branch。

## 1. 你在 GitHub 创建私有仓库

你在 GitHub 页面操作：

1. 点击 `New repository`。
2. Repository name 填：`module2-timeseries-analysis`。
3. Visibility 选择：`Private`。
4. 不要勾选 GitHub 自动添加 README、`.gitignore` 或 license，因为本地已经有这些文件。
5. 点击 `Create repository`。

创建后，GitHub 会给你一个仓库地址，例如：

```text
https://github.com/YOUR-GITHUB-USERNAME/module2-timeseries-analysis.git
```

如果你不确定 SSH 是否配置好，优先用 HTTPS 地址。

## 2. 你把本地仓库连接到 GitHub

在 PowerShell 中，确认你位于仓库根目录：

```powershell
cd "k:\study_courses\graduates_study_courses\second semester\water resources lab\Assignment2\module2-timeseries-analysis"
```

添加远端地址：

```powershell
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/module2-timeseries-analysis.git
```

把本地 `main` 推送到 GitHub：

```powershell
git push -u origin main
```

检查远端是否配置成功：

```powershell
git remote -v
```

你应该看到类似：

```text
origin  https://github.com/YOUR-GITHUB-USERNAME/module2-timeseries-analysis.git (fetch)
origin  https://github.com/YOUR-GITHUB-USERNAME/module2-timeseries-analysis.git (push)
```

如果远端地址写错了，改成正确地址：

```powershell
git remote set-url origin https://github.com/CORRECT-USERNAME/module2-timeseries-analysis.git
```

## 3. 你邀请 Li Ling

你在 GitHub 页面操作：

1. 打开你的 `module2-timeseries-analysis` 仓库。
2. 点击 `Settings`。
3. 找到 `Collaborators` 或 `Collaborators and teams`。
4. 点击 `Add people`。
5. 输入 Li Ling 的 GitHub 用户名或邮箱。
6. 发送邀请。
7. 告诉 Li Ling 去 GitHub 邮件或通知里接受邀请。

注意：Li Ling 接受邀请前，不能向你的仓库 push branch，也不能正常参与 PR 流程。

## 4. Li Ling 克隆仓库

Li Ling 接受邀请后，在自己的电脑上运行：

```powershell
cd "LI-LING-CHOOSES-A-LOCAL-FOLDER"
git clone https://github.com/YOUR-GITHUB-USERNAME/module2-timeseries-analysis.git
cd module2-timeseries-analysis
git status
```

她应该看到：

```text
On branch main
Your branch is up to date with 'origin/main'.
```

## 5. 你们两个人都安装 Python 环境

每个人都要在自己的电脑上安装依赖。

PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果 PowerShell 阻止激活虚拟环境，使用：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Conda 版本：

```powershell
conda env create -f environment.yml
conda activate module2-timeseries-analysis
```

## 6. 你们两个人都放置原始数据

原始 CSV 文件很大，不应该提交到 GitHub。每个人都需要在自己本地放一份数据到：

```text
data/raw/
```

预期文件：

```text
data/raw/Q_Gisingen_1976-2023.csv
data/raw/SSC_Gisingen_2003-2020.csv
data/raw/Q_Diepoldsau_m3s.csv
data/raw/SSC_Diepoldsau_gL.csv
```

检查项目能否运行：

```powershell
python -m pytest -q
python run_all.py
```

完整流程测试：

```powershell
python run_all.py --full
```

## 7. 每次开始工作前的固定动作

你和 Li Ling 每次开始写代码前都先做：

```powershell
git switch main
git pull origin main
git status
```

只有当 `main` 是干净状态时，才新建 feature branch。

## 8. 推荐分支计划

这个计划保证你和 Li Ling 都至少 branch 和 merge 一次，符合 PDF 的 Git 工作流要求。

| 分支名 | 负责人 | 任务 | 主要文件 | PR 标题 |
|---|---|---|---|---|
| `you/docs-git-workflow-li-ling` | 你 | 写清楚你和 Li Ling 的 Git 流程 | `docs/GIT_WORKFLOW_FOR_TWO_MEMBERS.md` | Docs: Git workflow for you and Li Ling |
| `you/section-1-timeseries-review` | 你 | Section 1 结果解释或代码微调 | `src/section1_timeseries_review.py`, notebook Section 1 | Section 1: Timeseries review |
| `li-ling/section-2-timeseries-modelling` | Li Ling | Section 2 ACF/PACF 和模型阶数解释 | `src/section2_timeseries_modelling.py`, notebook Section 2 | Section 2: ACF and PACF modelling |
| `you/section-3-model-evaluation` | 你 | Section 3 模型诊断解释 | `src/section3_model_evaluation.py`, notebook Section 3 | Section 3: Model evaluation |
| `li-ling/section-4-sediment-influence` | Li Ling | Section 4 输沙量影响分析 | `src/section4_sediment_influence.py`, notebook Section 4 | Section 4: Sediment influence |
| `you-or-li-ling/section-5-dependency-analysis` | 任意一人 | Section 5 Q-C 相关性解释 | `src/section5_dependency_analysis.py`, notebook Section 5 | Section 5: Q-C dependency |
| `you-or-li-ling/code-explanation-docs` | 任意一人 | 代码讲解文档 | `docs/CODE_WALKTHROUGH.md`, `README.md` | Docs: Code walkthrough |
| `li-ling/tests-basic-pipeline` | Li Ling | 测试和 smoke test 检查 | `tests/`, `run_all.py` | Tests: Basic pipeline |

## 9. 示例：你修改 Git 文档

你运行：

```powershell
git switch main
git pull origin main
git switch -c you/docs-git-workflow-li-ling
```

修改文件：

```text
docs/GIT_WORKFLOW_FOR_TWO_MEMBERS.md
```

查看改动：

```powershell
git status
git diff
```

提交：

```powershell
git add docs/GIT_WORKFLOW_FOR_TWO_MEMBERS.md
git commit -m "personalize git workflow for you and li ling"
```

推送：

```powershell
git push -u origin you/docs-git-workflow-li-ling
```

然后在 GitHub 上开 PR：

```text
base: main
compare: you/docs-git-workflow-li-ling
title: Docs: Git workflow for you and Li Ling
```

让 Li Ling review。这样她第一次不用马上改代码，可以先熟悉 PR review。

## 10. 示例：Li Ling 修改 Section 2

Li Ling 运行：

```powershell
git switch main
git pull origin main
git switch -c li-ling/section-2-timeseries-modelling
```

Li Ling 修改：

```text
src/section2_timeseries_modelling.py
notebooks/Module2_Timeseries_Analysis.ipynb
```

Li Ling 测试：

```powershell
python -m pytest -q
python run_all.py
```

Li Ling 提交：

```powershell
git add src/section2_timeseries_modelling.py notebooks/Module2_Timeseries_Analysis.ipynb
git commit -m "refine acf pacf order interpretation"
git push -u origin li-ling/section-2-timeseries-modelling
```

Li Ling 在 GitHub 上开 PR，你来 review。

## 11. PR 描述模板

你们每次开 PR 可以复制这个模板：

```text
What changed:
- 修改点 1。
- 修改点 2。

How I tested:
- python -m pytest -q
- python run_all.py
- 如果改了模型拟合或输沙量部分，也运行 python run_all.py --full

Files to review carefully:
- src/...
- notebooks/Module2_Timeseries_Analysis.ipynb

Review questions:
- 方法是否正确？
- 解释是否足够谨慎？
- notebook 是否仍然只保留 MAIN / PLOT / PRINT / comment？
- 单位和统计检验是否解释清楚？
```

## 12. 有质量的 review comment 示例

review 不要只写 `looks good`，最好留下具体意见。

可以使用这些句子：

```text
Could you explain why this trend is removed instead of only subtracting the mean?
This docstring says what the function returns, but it does not explain the input units.
The plot title should say monthly mean so the time scale is clear.
Please mention that Ljung-Box is tested at the 5% significance level.
This interpretation sounds causal; can we phrase it more cautiously?
Can you confirm that C is still in g/L before multiplying by Q?
```

这些评论能证明你们真的做了 peer review，而不是形式上点了 merge。

## 13. 回复 review comments

PR 作者在同一个 branch 上修改：

```powershell
git status
git add FILES-THAT-CHANGED
git commit -m "address review comments"
git push
```

GitHub 上的 PR 会自动更新。

然后在 GitHub comment 下回复：

```text
Resolved by adding the 5% significance-level wording.
Resolved by clarifying that C[g/L] equals kg/m3 for the mass calculation.
```

## 14. 合并前把 main 合进 feature branch

PR 最终 merge 前，作者先把最新 `main` 合进自己的 branch。

例子：

```powershell
git switch li-ling/section-2-timeseries-modelling
git fetch origin
git merge origin/main
```

如果没有冲突，运行：

```powershell
python -m pytest -q
python run_all.py
git push
```

如果有冲突，Git 会告诉你哪些文件冲突。打开冲突文件，找到：

```text
<<<<<<< HEAD
your branch version
=======
main branch version
>>>>>>> origin/main
```

手动编辑成最终正确版本，删除这些冲突标记，然后：

```powershell
git add conflicted-file.py
git commit -m "resolve merge conflict with main"
python -m pytest -q
git push
```

不要随便用 `git reset --hard` 或 force push，除非你们两个人都明确知道后果。

## 15. PR 通过后合并

在 GitHub 页面：

1. 打开 PR。
2. 确认另一个人已经 review / approve。
3. 确认本地测试已经运行。
4. 点击 `Merge pull request`。
5. 点击 `Confirm merge`。

合并后，你和 Li Ling 都更新本地 `main`：

```powershell
git switch main
git pull origin main
```

## 16. 删除已经合并的 branch

GitHub 页面上可以点击 `Delete branch` 删除远端 branch。

本地删除：

```powershell
git branch -d li-ling/section-2-timeseries-modelling
```

如果 Git 不让删除，先确认这个 PR 是否真的已经 merge。

## 17. 不应该提交的文件

不要提交这些内容：

```text
data/raw/*.csv
data/processed/*.csv
outputs/figures/*.png
outputs/tables/*.csv
outputs/reports/*.ipynb
__pycache__/
.pytest_cache/
.venv/
```

它们已经被 `.gitignore` 忽略。

每次 commit 前检查：

```powershell
git status --short
```

如果大数据文件误入 staged area：

```powershell
git restore --staged data/raw/BIG-FILE.csv
```

## 18. 从现在开始的第一组推荐命令

因为本地仓库已经建好了，下一步是：

```powershell
cd "k:\study_courses\graduates_study_courses\second semester\water resources lab\Assignment2\module2-timeseries-analysis"
git status
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/module2-timeseries-analysis.git
git push -u origin main
```

然后你在 GitHub 上邀请 Li Ling。

接着，你可以开第一个协作 branch：

```powershell
git switch main
git pull origin main
git switch -c you/docs-git-workflow-li-ling
git push -u origin you/docs-git-workflow-li-ling
```

在 GitHub 上开 PR，让 Li Ling review。

Li Ling 的第一个 coding branch 可以是：

```powershell
git switch main
git pull origin main
git switch -c li-ling/section-2-timeseries-modelling
```

这样你们两个人都有明确的 branch 和 merge 记录。

## 19. 每个 PR 的最终检查清单

合并前逐项确认：

- feature branch 已经合入最新 `main`。
- `python -m pytest -q` 通过。
- `python run_all.py` 通过。
- 如果改了 Section 3 或 Section 4，`python run_all.py --full` 通过。
- notebook 仍然遵守 Title / MAIN / PLOT / PRINT / Comment 结构。
- 没有提交 raw data 或自动生成的 figures / tables。
- reviewer 至少留下了一条有内容的 review comment。
- author 已经回应 review comments。
- 项目结束前，你和 Li Ling 都至少有一个 branch 被 merge。


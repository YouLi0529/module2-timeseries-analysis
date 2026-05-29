# VS Code + GitHub 协作操作指南

这份指南是为了把 VS Code、Git 和 GitHub 的操作流程整理清楚一些。可以把它当成一份随手查的步骤说明，不需要一次全部记住；按顺序慢慢做就好。

当前项目大致是这样：

- Section 1、Section 2、Section 3 已经整理好并上传到 GitHub。
- 这次可以先集中在 Section 4、Section 5、plotting，以及 notebook 中对应的 Section 4 和 Section 5。
- Section 1、Section 2、Section 3 暂时保持不动会比较稳。
- `src/data_loading.py` 也先保持不动。

这次主要会涉及这些文件：

```text
src/section4_sediment_influence.py
src/section5_dependency_analysis.py
src/plotting.py
notebooks/Module2_Timeseries_Analysis.ipynb
```

## 1. 先熟悉几个常用概念

GitHub 看起来有点复杂，但这次主要用到的其实就是“保存版本”和“让对方检查修改”。

| 词 | 简单解释 |
|---|---|
| repository / repo | GitHub 上的项目文件夹。 |
| clone | 第一次把 GitHub 上的项目下载到自己电脑。 |
| main | 项目的稳定版本，最好始终保持能运行。 |
| branch | 自己的工作分支，可以在里面改代码，不影响 main。 |
| commit | 保存一次修改记录，像做一个存档。 |
| push | 把电脑里的 commit 上传到 GitHub。 |
| pull | 从 GitHub 下载别人已经更新的内容。 |
| Pull Request / PR | 请求把自己的 branch 合并到 main，并让对方 review。 |
| review | 另一位同学检查代码，并提出可以改进的地方。 |
| merge | review 通过后，把 branch 合并进 main。 |
| conflict | 两个人改到同一部分，Git 不知道保留哪一版，需要一起看一下。 |

整体流程是：

```text
第一次 clone 项目
-> 每次工作前 pull 最新 main
-> 创建自己的 branch
-> 修改 Section 4/5/plotting/notebook
-> 运行测试
-> commit
-> push
-> 在 GitHub 开 Pull Request
-> 等待 review
-> 根据 comment 修改
-> 通过后 merge
```

## 2. 准备软件

建议先准备三个软件：

1. Git
2. VS Code
3. Python

### 2.1 安装 Git

打开浏览器，进入：

```text
https://git-scm.com/downloads
```

下载并安装 Git。安装时默认选项一般就可以。

安装完成后，打开 Windows PowerShell，输入：

```powershell
git --version
```

如果看到类似：

```text
git version 2.xx.x
```

说明 Git 已经可以用了。

如果提示 `git is not recognized`，可以先重启 PowerShell 和 VS Code。如果还是不行，再重新检查 Git 是否安装成功。

## 3. 接受 GitHub 仓库邀请

仓库创建者会把你加入 GitHub 私有仓库。

可以这样操作：

1. 打开 GitHub。
2. 登录自己的 GitHub 账号。
3. 查看邮箱或 GitHub 通知。
4. 找到仓库邀请。
5. 点击接受邀请。

接受邀请之后，就可以正常 clone、push 和参与 Pull Request 了。

## 4. 在 VS Code 中 clone 项目

这个步骤只需要在第一次使用这个项目时做一次。

### 4.1 复制 GitHub 仓库地址

在 GitHub 页面：

1. 打开项目仓库。
2. 点击绿色按钮 `Code`。
3. 选择 `HTTPS`。
4. 复制仓库地址。

地址大概长这样：

```text
https://github.com/OWNER-USERNAME/module2-timeseries-analysis.git
```

### 4.2 在 VS Code 中 clone

打开 VS Code。

按键盘：

```text
Ctrl + Shift + P
```

屏幕上方会出现一个输入框。

输入：

```text
Git: Clone
```

点击 `Git: Clone`。

然后按提示操作：

1. 粘贴刚才复制的 GitHub 仓库地址。
2. 选择电脑上一个容易找到的文件夹。
3. 等 VS Code 下载项目。
4. 如果 VS Code 问是否打开这个项目，点击 `Open`。
5. 如果 VS Code 问是否信任这个文件夹，点击 `Yes, I trust the authors`。

这样项目就下载到电脑上了。

## 5. 打开 VS Code 终端（哈哈）

在 VS Code 顶部菜单：

```text
Terminal -> New Terminal
```

也可以按：

```text
Ctrl + `
```

底部会出现一个终端窗口。

输入：

```powershell
pwd
```

确认当前路径最后是：

```text
module2-timeseries-analysis
```

然后输入：

```powershell
git status
```

正常情况下会看到类似：

```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

这表示现在在 `main` 分支，并且本地项目是干净的。

## 6. 安装 Python 依赖

在 VS Code 终端输入：

```powershell
python -m venv .venv
```

这会创建一个项目专用 Python 环境。

然后激活它：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 不允许激活，可以输入：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

激活后，再安装项目需要的包：

```powershell
pip install -r requirements.txt
```

这个过程可能需要几分钟。

## 7. 放置原始数据

原始数据文件比较大，所以不放在 GitHub 上。可以把 CSV 文件放进：

```text
data/raw/
```

需要这四个文件：

```text
data/raw/Q_Gisingen_1976-2023.csv
data/raw/SSC_Gisingen_2003-2020.csv
data/raw/Q_Diepoldsau_m3s.csv
data/raw/SSC_Diepoldsau_gL.csv
```

这里稍微注意一下：

- raw data 不用 commit。
- raw data 也不用 push。
- 这些文件只保存在自己的电脑里就可以。

## 8. 开始修改前先创建自己的 branch

建议先在自己的 branch 上改代码，这样比较稳。

每次开始工作前，可以先输入：

```powershell
git switch main
git pull origin main
```

这两句的意思是：回到稳定版本，并下载 GitHub 上最新内容。

然后创建自己的工作分支：

```powershell
git switch -c collaborator/section-4-5-plotting
```

检查当前分支：

```powershell
git status
```

正常会看到：

```text
On branch collaborator/section-4-5-plotting
```

看到这个以后，就可以比较安心地开始改代码。

## 9. 如果已经在 main 上改了代码

没关系，这种情况很常见。

如果已经在 `main` 上改了文件，但还没有 commit，可以运行：

```powershell
git status
git switch -c collaborator/section-4-5-plotting
```

通常情况下，已有修改会一起移动到新 branch。

然后再检查：

```powershell
git status
```

确认现在显示：

```text
On branch collaborator/section-4-5-plotting
```

如果 VS Code 不让你切 branch，可以先停一下，找另一位同学一起看。

## 10. 这次主要修改哪些文件

建议先集中修改这些文件：

```text
src/section4_sediment_influence.py
src/section5_dependency_analysis.py
src/plotting.py
notebooks/Module2_Timeseries_Analysis.ipynb
```

下面这些文件暂时不用改：

```text
src/data_loading.py
src/section1_timeseries_review.py
src/section2_timeseries_modelling.py
src/section3_model_evaluation.py
```

这些部分已经整理好了，先保持稳定会更方便协作。


## 11. plotting 代码可以怎么改

文件：

```text
src/plotting.py
```

主要看这些函数：

```python
plot_synthetic_series(...)
plot_sediment_yields(...)
plot_dependency_scatter(...)
```

简化时可以优先考虑：

- 图要能看懂。
- 标题和坐标轴标签要清楚。
- Section 1、2、3 的绘图函数可以先保持不动。
- 图能清楚表达结果就很好，不需要做得太复杂。

## 12. notebook 可以怎么改

文件：

```text
notebooks/Module2_Timeseries_Analysis.ipynb
```

建议先只看：

```text
Section 4: Ill to Rhein relative sediment influence
Section 5: Independent variables?
```

Section 1、2、3 可以先保持不动。

每个 section 仍然建议保持这个结构：

```text
Markdown title
MAIN code cell
PLOT code cell
PRINT code cell
Markdown comment
```

很长的函数建议放在 `.py` 文件里，notebook 里主要调用函数就好。

## 13. 在 VS Code 里修改 `.py` 文件

1. 看 VS Code 左边。
2. 点击文件图标，也就是 `Explorer`。
3. 打开 `src` 文件夹。
4. 点击要修改的 `.py` 文件。
5. 修改代码。
6. 按 `Ctrl + S` 保存。

比较舒服的节奏是：

```text
改一小段
-> Ctrl + S 保存
-> 运行测试
-> 没问题再继续
```

## 14. 在 VS Code 里修改 notebook

1. 在左侧 Explorer 打开 `notebooks`。
2. 点击 `Module2_Timeseries_Analysis.ipynb`。
3. 等 notebook 页面加载出来。
4. 如果 VS Code 让你选择 kernel，选择 `.venv` 对应的 Python。
5. 滚动到 Section 4 或 Section 5。
6. 修改对应 cell。
7. 按 `Ctrl + S` 保存。

建议：

- Section title 保留。
- MAIN / PLOT / PRINT / comment 的顺序保留。
- Section 4/5 的长函数继续放在 `.py` 文件里。

## 15. 修改后运行测试

改完代码后，先保存所有文件。

在 VS Code 终端运行：

```powershell
python -m pytest -q
```

理想结果：

```text
5 passed
```

然后运行完整项目：

```powershell
python run_all.py --full
```

如果看到红色报错，可以先看最后几行。通常最后几行会告诉你哪个文件、哪一行出了问题。

可以按这个顺序处理：

```text
看最后一段错误
-> 找到文件名和行号
-> 一次只修一个问题
-> 保存
-> 重新运行测试
```

如果代码暂时还跑不通，可以先别急着开 Pull Request，除非已经和另一位同学说好先提交一个未完成版本。

## 16. 查看自己改了哪些文件

在终端输入：

```powershell
git status
```

理想情况下，modified files 主要应该是：

```text
src/section4_sediment_influence.py
src/section5_dependency_analysis.py
src/plotting.py
notebooks/Module2_Timeseries_Analysis.ipynb
```

如果看到这些文件，通常不用提交：

```text
data/raw/*.csv
data/processed/*.csv
outputs/figures/*.png
outputs/tables/*.csv
outputs/reports/*.ipynb
```

这些是数据或自动生成文件，通常不用进 GitHub。

## 17. 用 VS Code 的 Source Control 提交（这步我们都没介绍，但我感觉可以像ai说的这样做嘿嘿）

VS Code 左边有一个像分叉线条的图标，叫 `Source Control`。

可以这样操作：

1. 点击 `Source Control`。
2. 查看 changed files。
3. 点击每个文件，看右边显示的差异。
4. 确认这些差异是自己改的。
5. 看不懂的文件可以先不 stage，等确认后再处理。

## 18. Stage 文件

在 `Source Control` 里：

1. 鼠标放到一个 changed file 上。
2. 点击旁边的 `+`。
3. 文件会进入 staged area。

建议只 stage 这些文件：

```text
src/section4_sediment_influence.py
src/section5_dependency_analysis.py
src/plotting.py
notebooks/Module2_Timeseries_Analysis.ipynb
```

也可以用终端：

```powershell
git add src/section4_sediment_influence.py
git add src/section5_dependency_analysis.py
git add src/plotting.py
git add notebooks/Module2_Timeseries_Analysis.ipynb
```

## 19. Commit 文件

commit 就是保存一次修改记录。

在 Source Control 顶部的输入框写 commit message。

可以写：

```text
simplify section 4 and 5 analysis code
```

然后点击 `Commit`。

如果用终端：

```powershell
git commit -m "simplify section 4 and 5 analysis code"
```

## 20. Push 到 GitHub

commit 后，需要 push。

在 VS Code 里，可能会看到按钮：

```text
Publish Branch
```

点击它就可以。

也可以用终端：

```powershell
git push -u origin collaborator/section-4-5-plotting
```

如果 GitHub 要求登录，按浏览器提示登录即可。

## 21. 在 GitHub 创建 Pull Request

push 完后，打开 GitHub 仓库页面。

GitHub 可能会显示一个黄色提示条，告诉你刚刚 push 了一个 branch。

点击：

```text
Compare & pull request
```

如果没有提示条：

1. 点击 `Pull requests`。
2. 点击 `New pull request`。
3. 设置：

```text
base: main
compare: collaborator/section-4-5-plotting
```

PR 标题可以写：

```text
Simplify Section 4 and Section 5 analysis
```

PR 描述可以复制这个：

```text
What changed:
- Simplified Section 4 sediment influence code.
- Simplified Section 5 dependency analysis code.
- Updated Section 4 and Section 5 notebook cells.
- Updated related plotting functions.

How I tested:
- python -m pytest -q
- python run_all.py --full

Files to review:
- src/section4_sediment_influence.py
- src/section5_dependency_analysis.py
- src/plotting.py
- notebooks/Module2_Timeseries_Analysis.ipynb

Questions for review:
- Is the code easier to understand?
- Are the units in Section 4 still correct?
- Are Q-C correlation tests in Section 5 still correct?
- Does the notebook still follow MAIN / PLOT / PRINT / comment?
```

然后点击：

```text
Create pull request
```

## 22. 等待 review

另一位同学会检查你的 PR。

可能会收到 comments，比如：

```text
Please keep the unit explanation for C * Q.
Please make this variable name clearer.
Please keep Section 1-3 unchanged.
Please simplify this function further.
```

这是正常协作流程，不代表做错了。代码合作本来就会有来回修改。

## 23. 根据 review 修改

如果收到修改意见：

1. 回到 VS Code。
2. 确认还在自己的 branch。

```powershell
git status
```

正常会看到：

```text
On branch collaborator/section-4-5-plotting
```

然后：

```text
修改代码
-> Ctrl + S 保存
-> 重新测试
-> commit
-> push
```

对应命令：

```powershell
python -m pytest -q
python run_all.py --full

git add src/section4_sediment_influence.py
git add src/section5_dependency_analysis.py
git add src/plotting.py
git add notebooks/Module2_Timeseries_Analysis.ipynb
git commit -m "address review comments for section 4 and 5"
git push
```

GitHub 上的 PR 会自动更新。

## 24. 合并前更新自己的 branch（it's merge！！！）

在 PR 最后合并前，可以把最新 `main` 合进自己的 branch。

运行：

```powershell
git switch collaborator/section-4-5-plotting
git fetch origin
git merge origin/main
```

如果没有 conflict，继续运行：

```powershell
python -m pytest -q
python run_all.py --full
git push
```

如果出现 conflict，可以先别急着改，直接找另一位同学一起处理。

## 25. 如果出现 conflict(下面的全是debug，但愿我们遇不到嘿嘿！)

conflict 文件里可能出现：

```text
<<<<<<< HEAD
your branch version
=======
main branch version
>>>>>>> origin/main
```

遇到 conflict 时可以这样处理：

1. 先别急。
2. 先保留当前代码，等一起确认后再改。
3. VS Code 里的按钮如果不确定含义，可以先不点。
4. 找另一位同学一起看。
5. 修完后重新运行测试。

## 26. PR 被 merge 后

PR merge 之后，可以更新自己电脑上的 main：

```powershell
git switch main
git pull origin main
```

然后可以删除本地 branch：

```powershell
git branch -d collaborator/section-4-5-plotting
```

这样电脑就和 GitHub 上的最新版本同步了。

## 27. 常见情况和处理方式

### 情况 1：已经在 main 上改了代码

如果还没 commit，可以运行：

```powershell
git switch -c collaborator/section-4-5-plotting
```

### 情况 2：忘记保存文件

按：

```text
Ctrl + S
```

然后再运行：

```powershell
git status
```

### 情况 3：raw data 出现在 Git status 里

这些文件通常不用提交：

```text
data/raw/*.csv
```

如果不小心 stage 了：

```powershell
git restore --staged data/raw/FILENAME.csv
```

### 情况 4：不小心改了 Section 1、2、3 文件

可以先不提交，和另一位同学确认要不要保留。

如果确认不用保留，可以恢复某个文件：

```powershell
git restore src/section1_timeseries_review.py
```

注意：这个命令会删除你对这个文件的本地修改。建议只在确认这些修改确实不用保留时使用。

### 情况 5：测试还没通过

每次 push 前建议都运行：

```powershell
python -m pytest -q
python run_all.py --full
```

## 28. 开 PR 前的检查清单

开 PR 前可以逐项确认：

- [ ] 我现在在 `collaborator/section-4-5-plotting`，不是 `main`。
- [ ] 我主要改的是 Section 4、Section 5、plotting 和 notebook Section 4/5。
- [ ] Section 1、2、3 保持不动。
- [ ] raw data 没有被提交。
- [ ] 所有文件都保存了。
- [ ] `python -m pytest -q` 通过。
- [ ] `python run_all.py --full` 通过。
- [ ] 已经 commit。
- [ ] 已经 push。
- [ ] 已经在 GitHub 上开 Pull Request。

## 29. 最短命令版本

如果已经熟悉上面的步骤，可以用这个短版本：

```powershell
git switch main
git pull origin main
git switch -c collaborator/section-4-5-plotting

# 在 VS Code 中修改 Section 4/5/plotting/notebook

python -m pytest -q
python run_all.py --full

git status
git add src/section4_sediment_influence.py
git add src/section5_dependency_analysis.py
git add src/plotting.py
git add notebooks/Module2_Timeseries_Analysis.ipynb
git commit -m "simplify section 4 and 5 analysis code"
git push -u origin collaborator/section-4-5-plotting
```

然后去 GitHub 页面创建 Pull Request。

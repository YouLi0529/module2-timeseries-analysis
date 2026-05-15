# Git Workflow for Two Members

This guide assumes two students: Member A and Member B. The purpose is to keep `main` stable while each person develops sections on separate branches, opens pull requests, receives review, and merges only after approval.

## 1. Repository Setup by Member A

From the folder that should contain the repository:

```bash
git init -b main
git add .
git commit -m "set up module 2 repository structure"
```

Create a new private GitHub repository named `module2-timeseries-analysis`. Then connect the local repository:

```bash
git remote add origin https://github.com/YOUR-USERNAME/module2-timeseries-analysis.git
git push -u origin main
```

Invite Member B on GitHub:

```text
GitHub repository page -> Settings -> Collaborators -> Add people -> invite Member B
```

## 2. Clone by Member B

Member B runs:

```bash
git clone https://github.com/YOUR-USERNAME/module2-timeseries-analysis.git
cd module2-timeseries-analysis
```

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Never Work Directly on Main

Before starting work:

```bash
git switch main
git pull origin main
git switch -c member-a/section-1-timeseries-review
```

For Member B:

```bash
git switch main
git pull origin main
git switch -c member-b/section-2-timeseries-modelling
```

## 4. Commit Small Logical Steps

Check changes:

```bash
git status
git diff
```

Stage and commit:

```bash
git add src/section1_timeseries_review.py notebooks/Module2_Timeseries_Analysis.ipynb
git commit -m "implement section 1 trend tests"
```

Good commit messages:

```text
implement monthly aggregation helpers
add acf pacf order selection
fit ar and arma residual diagnostics
document sediment mass unit conversion
add peer review checklist
```

## 5. Push a Feature Branch

```bash
git push -u origin member-a/section-1-timeseries-review
```

## 6. Open a Pull Request on GitHub

On GitHub:

```text
Repository page -> Pull requests -> New pull request
base: main
compare: member-a/section-1-timeseries-review
Create pull request
```

Use a clear PR title:

```text
Section 1: Timeseries review and trend normalization
```

In the PR description, include:

```text
What changed:
- Added trend test and normalization functions.
- Updated notebook Section 1 cells.
- Added/updated plots.

How tested:
- pytest
- python run_all.py

Review focus:
- Is the 5% slope test interpreted correctly?
- Does the notebook keep logic in .py files?
- Are docstrings complete?
```

## 7. Peer Review

The other member reviews the PR on GitHub.

Useful review comments:

```text
Could you explain why the significant trend is removed instead of only subtracting the mean?
This function needs a clearer output description in the docstring.
The plot title should mention that values are monthly means.
Please confirm that C is still in g/L before the sediment mass calculation.
The Ljung-Box interpretation should state the 5% significance level.
```

The reviewer should check:

- The changed code is readable.
- The notebook still runs from top to bottom.
- Functions are in `.py` files, not hidden inside the notebook.
- Statistical results are interpreted cautiously.
- No raw data or generated outputs are accidentally committed.

## 8. Respond to Review Comments

The author edits locally, then runs:

```bash
git status
git add src/section1_timeseries_review.py notebooks/Module2_Timeseries_Analysis.ipynb
git commit -m "address review comments for section 1"
git push
```

The PR updates automatically.

## 9. Merge Main into Feature Branch Before Final Merge

Before the PR is merged, update the branch with latest `main`:

```bash
git switch member-a/section-1-timeseries-review
git fetch origin
git merge origin/main
```

If there are conflicts, Git marks the files. Open each conflicted file and look for:

```text
<<<<<<< HEAD
your branch version
=======
main branch version
>>>>>>> origin/main
```

Edit the file so it contains the correct final code, then:

```bash
git add conflicted-file.py
git commit -m "resolve merge conflicts with main"
git push
```

Run tests after resolving conflicts:

```bash
pytest
python run_all.py
```

## 10. Merge After Approval

On GitHub:

```text
Pull request page -> Confirm all checks passed -> Merge pull request -> Confirm merge
```

Prefer squash merge if your instructor allows a clean history. If unsure, use the normal GitHub merge button.

After merging, both members update local main:

```bash
git switch main
git pull origin main
```

## 11. Delete Branches

Delete remote branch on GitHub with the "Delete branch" button after merge.

Delete local branch:

```bash
git branch -d member-a/section-1-timeseries-review
```

If Git refuses because the branch is not merged, do not force delete unless you are sure it is safe.

## Required Branch Plan

| Branch | Responsible member | Task | Files to modify | PR title |
|---|---|---|---|---|
| `setup/repository-structure` | A | Initial structure, README, requirements | repository skeleton | Setup repository structure |
| `member-a/section-1-timeseries-review` | A | Monthly aggregation, stationarity, trend removal | `src/data_loading.py`, `src/section1_timeseries_review.py`, notebook Section 1 | Section 1: Timeseries review |
| `member-b/section-2-timeseries-modelling` | B | ACF/PACF and candidate order selection | `src/section2_timeseries_modelling.py`, `src/plotting.py`, notebook Section 2 | Section 2: ACF/PACF modelling |
| `member-a/section-3-model-evaluation` | A | AR/ARMA fitting and residual diagnostics | `src/section3_model_evaluation.py`, notebook Section 3 | Section 3: Model evaluation |
| `member-b/section-4-sediment-influence` | B | Synthetic series and sediment mass | `src/section4_sediment_influence.py`, notebook Section 4 | Section 4: Sediment influence |
| `member-a-or-b/section-5-dependency-analysis` | A or B | Q-C dependency tests | `src/section5_dependency_analysis.py`, notebook Section 5 | Section 5: Q-C dependency |
| `docs/project-explanation` | A or B | Explanation guide and methods docs | `docs/*.md`, `README.md` | Documentation: project explanation |
| `tests/basic-pipeline` | A or B | Tests and smoke runner | `tests/`, `run_all.py` | Tests: basic pipeline |

## Suggested Commit Messages by Branch

`member-a/section-1-timeseries-review`:

```text
add project data loading utilities
implement monthly trend review functions
update notebook section 1
```

`member-b/section-2-timeseries-modelling`:

```text
compute acf pacf diagnostics
select candidate ar arma orders
add acf pacf plots
```

`member-a/section-3-model-evaluation`:

```text
fit ar arma candidate models
add residual diagnostic tests
choose parsimonious final models
```

`member-b/section-4-sediment-influence`:

```text
simulate synthetic monthly series
compute sediment mass yields
estimate ill contribution ratios
```

`member-a-or-b/section-5-dependency-analysis`:

```text
add q c correlation tests
plot q c joint distributions
document independent model limitations
```

## Merge Checklist for Every PR

- Branch is up to date with `main`.
- `pytest` passes.
- `python run_all.py` runs, or missing raw data message is clear.
- Notebook section follows Title, MAIN, PLOT, PRINT, Comment.
- No raw data files are included in the PR.
- Reviewer has approved.
- Both members have had at least one branch merged by the end of the project.


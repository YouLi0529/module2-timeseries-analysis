# Peer Review Checklist

Use this checklist for every pull request.

## Reproducibility

- [ ] Does the notebook run from start to finish?
- [ ] Does `pytest` pass?
- [ ] Does `python run_all.py` pass or fail with a clear missing-data message?
- [ ] Is `main` still functional after the proposed change?
- [ ] Has `main` been merged into the feature branch before final merge?

## Code Organization

- [ ] Are functions in `.py` files rather than hidden in notebook cells?
- [ ] Is the notebook limited to MAIN, PLOT, PRINT, and comments?
- [ ] Are function docstrings complete?
- [ ] Are variable names readable for beginners?
- [ ] Are paths handled with `pathlib`?
- [ ] Are raw data and generated outputs excluded from Git?

## Scientific Content

- [ ] Are monthly means used before the main analysis?
- [ ] Is the 5% trend slope test implemented and interpreted correctly?
- [ ] Are mean subtraction and trend removal clearly distinguished?
- [ ] Are ACF and PACF plotted with approximate 95% confidence bounds?
- [ ] Are AR and ARMA orders justified quantitatively?
- [ ] Are residual ACF diagnostics included?
- [ ] Is the Portmanteau / Ljung-Box test included and interpreted at 5%?
- [ ] Is residual normality assessed with PPCC/probability plot or a defensible equivalent?
- [ ] Are plots readable, labelled, and saved?
- [ ] Are units handled correctly for sediment mass?
- [ ] Is `C[g/L] * Q[m3/s] = kg/s` explained?
- [ ] Is the Q-C dependence question answered with quantitative evidence?

## Interpretation

- [ ] Are results interpreted without overstating causation?
- [ ] Are physical explanations separated from statistical evidence?
- [ ] Is the non-synchronous station comparison discussed?
- [ ] Are limitations of independent Q and C simulation discussed?
- [ ] Can both students explain the changed section orally?

## Team Workflow

- [ ] Did the author create a feature branch?
- [ ] Did the author make small, meaningful commits?
- [ ] Did the reviewer leave at least one substantive review comment?
- [ ] Did the author respond to review comments?
- [ ] Did both members branch and merge at least once by the end of the project?


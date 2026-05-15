# Section-by-Section Methods

## Section 1: Timeseries Review

Research question:

Do the monthly Q and C series look stationary, and do they contain statistically significant linear trends?

Input data:

- Monthly mean Q and C for Gisingen.
- Monthly mean Q and C for Diepoldsau.

Method:

- Aggregate raw 10-minute and 15-minute data to monthly means.
- Fit a linear regression against monthly time index.
- Test slope significance at 5%.
- Run an ADF stationarity check.
- Remove the mean if trend is not significant.
- Remove significant linear trend if slope p-value is below 0.05.

Output figures:

- Full monthly Q and C timeseries for both stations.
- Linear trend line on each plot.

Output printed values:

- Slope.
- Slope p-value.
- Trend significance.
- ADF p-value and interpretation.
- Removed component.
- Mean and variance after removal.

Interpretation points:

- Trend significance is not physical proof.
- Discharge trends may reflect climate, regulation, rating changes, or measurement changes.
- Normalized data should have mean approximately zero.

Common mistakes:

- Fitting ARMA directly to non-stationary data.
- Forgetting that the slope is per month.
- Treating a p-value as proof of causation.

What each team member should explain:

- Why monthly aggregation happens first.
- Why trend removal is needed.
- What the 5% slope test means.

## Section 2: Timeseries Modelling

Research question:

What AR and ARMA orders are reasonable based on empirical autocorrelation structure?

Input data:

- Normalized/detrended monthly series from Section 1.

Method:

- Compute ACF and PACF.
- Add approximate 95% confidence bounds.
- Identify significant ACF/PACF lags.
- Select candidate AR and ARMA orders with capped complexity.

Output figures:

- ACF and PACF plots for all four station-variable series.

Output printed values:

- Candidate AR order.
- Candidate ARMA order.
- Significant ACF/PACF lags.
- Short order-selection justification.

Interpretation points:

- PACF is useful for AR order.
- ACF is useful for MA memory.
- Hydrological differences can justify different orders across stations.

Common mistakes:

- Choosing high orders only because many lags are significant.
- Ignoring parsimony.
- Using the same order for both stations without evidence.

What each team member should explain:

- What ACF and PACF measure.
- Why model order is a modelling choice, not a purely automatic answer.

## Section 3: Timeseries Application & Evaluation

Research question:

Do the fitted AR and ARMA models adequately describe temporal dependence?

Input data:

- Normalized series from Section 1.
- Candidate model orders from Section 2.

Method:

- Fit AR and ARMA candidate models.
- Compute empirical ACF and theoretical model ACF.
- Compute residual ACF.
- Run Ljung-Box test at 5%.
- Assess residual normality with probability plots and PPCC/Shapiro-style testing.
- Choose final model using residual independence, BIC, AIC, and parsimony.

Output figures:

- Empirical versus theoretical ACF.
- Residual ACF.
- Residual probability plots.

Output printed values:

- AIC and BIC.
- Ljung-Box p-value.
- Residual independence decision.
- PPCC and normality p-value.
- Chosen final model.

Interpretation points:

- Residuals should not show strong autocorrelation.
- A slightly better AIC may not justify a much more complex model.
- Normality is helpful but independence is usually more important for time dependence.

Common mistakes:

- Selecting the model only by AIC.
- Ignoring residual ACF.
- Saying a model is correct instead of saying it is adequate for the assignment purpose.

What each team member should explain:

- What residual diagnostics test.
- Why ARMA may or may not be worth the extra complexity.

## Section 4: Ill to Rhein Relative Sediment Influence

Research question:

How much does the Ill contribute to monthly and yearly sediment mass at Diepoldsau/Rhein, and can synthetic series estimate this contribution?

Input data:

- Monthly physical Q and C.
- Final fitted models.
- Normalization/trend metadata from Section 1.

Method:

- Generate 10 synthetic monthly normalized series for 10 years.
- Plot synthetic normalized series with historical normalized series.
- Restore synthetic series to physical scale for sediment mass calculation.
- Compute `M(t) = C(t) * Q(t)` in kg/s.
- Calculate monthly and yearly sediment summaries.
- Estimate Ill/Gisingen contribution relative to Diepoldsau/Rhein.

Output figures:

- Historical normalized series plus synthetic paths.
- Sediment mass climatology and synthetic contribution plots.

Output printed values:

- Observed mean mass rate.
- Mean monthly mass.
- Ill/Rhein contribution ratio.
- Synthetic path statistics.
- Number of negative restored values clipped to zero.

Interpretation points:

- Synthetic series compare long-term statistics, not exact timing.
- Non-synchronous records limit direct contribution inference.
- Independent Q and C simulation may distort mass because mass is a product.

Common mistakes:

- Forgetting `1 g/L = 1 kg/m3`.
- Computing mass from normalized values.
- Treating synthetic paths as deterministic forecasts.

What each team member should explain:

- Why C times Q gives kg/s.
- Why non-synchronous comparison is a limitation.
- Why synthetic estimates are preliminary.

## Section 5: Independent Variables?

Research question:

Can Q and C be treated as statistically independent at each station?

Input data:

- Aligned monthly Q and C for each station.

Method:

- Align Q and C by monthly timestamp.
- Compute Pearson correlation.
- Compute Spearman correlation.
- Compute Kendall correlation.
- Test whether association is statistically significant at 5%.
- Plot Q-C joint distributions.

Output figures:

- Scatter plots of Q versus C for each station.

Output printed values:

- Sample size.
- Pearson r and p-value.
- Spearman rho and p-value.
- Kendall tau and p-value.
- Independence interpretation.

Interpretation points:

- Correlation does not capture every form of dependence.
- Q-C relationships can be nonlinear and event-dependent.
- Independent univariate models are a simplification.

Common mistakes:

- Saying "not significant" proves independence.
- Ignoring nonlinearity.
- Forgetting that monthly aggregation can hide event-scale hysteresis.

What each team member should explain:

- Why Q and C may be dependent physically.
- How independent simulation can bias sediment mass estimates.
- Better alternatives: copulas, rating curves, VAR/VARMA, conditional simulation.


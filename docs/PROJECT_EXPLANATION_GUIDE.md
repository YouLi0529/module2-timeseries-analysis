# Project Explanation Guide

This guide helps both students understand and explain the full project, not just run the code.

## 1. Hydrological Meaning of Q and C

`Q` is discharge, usually measured in cubic metres per second. It describes how much water passes the station per unit time.

`C` is suspended sediment concentration, measured here in grams per litre. It describes how much suspended material is carried in a unit volume of water.

Together, Q and C estimate suspended sediment transport. High concentration alone does not imply high total sediment transport if discharge is small. High discharge with low concentration can still move a lot of sediment.

## 2. Why Monthly Aggregation Is Used

The raw observations are at 10-minute or 15-minute intervals. The assignment asks for monthly mean values. Monthly aggregation:

- puts stations with different time steps onto a common time scale;
- reduces noise from short events;
- makes AR/ARMA modelling more stable for a lab assignment;
- focuses on long-term regime behaviour rather than individual floods.

The cost is that flood peaks and short sediment pulses are smoothed out.

## 3. What Stationarity Means

A stationary timeseries has statistical properties that do not change over time. In this project, the key practical ideas are:

- the mean should be stable;
- the variance should be finite and reasonably stable;
- autocorrelation should depend mainly on lag, not on calendar time.

AR and ARMA models are usually fitted to stationary or approximately stationary data.

## 4. Why Trend Removal Is Needed

If a series has a significant trend, its mean changes over time. Fitting a stationary ARMA model directly to that series would mix long-term change with short-term autocorrelation.

The assignment asks to subtract the mean or any statistically significant linear trend. After this step, the normalized series should have mean approximately zero and finite variance.

## 5. What ACF and PACF Mean

The autocorrelation function, ACF, measures correlation between a series and lagged versions of itself. For monthly data, lag 1 means one month earlier, lag 12 means one year earlier.

The partial autocorrelation function, PACF, measures the direct relationship with a lag after removing the influence of shorter lags.

Simple interpretation:

- PACF cutting off after lag `p` suggests an AR(`p`) model.
- ACF cutting off after lag `q` suggests an MA(`q`) model.
- Both ACF and PACF tailing off can suggest an ARMA model.

## 6. Difference Between AR and ARMA

An AR model explains the present value using past values:

```text
z_t = a1 z_{t-1} + a2 z_{t-2} + ... + error_t
```

An ARMA model uses both past values and past errors:

```text
z_t = AR terms + current error + MA terms from previous errors
```

ARMA is more flexible, but also more complex. The project asks whether the final order is parsimonious, meaning it balances performance and simplicity.

## 7. What Residual Diagnostics Test

Residuals are what the model failed to explain. If the model is appropriate, residuals should behave like white noise.

The notebook checks:

- empirical ACF versus theoretical model ACF;
- residual ACF with confidence bounds;
- Ljung-Box test for remaining autocorrelation;
- probability plot and PPCC/Shapiro-style test for normality.

If residuals are still autocorrelated, the model has not captured all temporal dependence.

## 8. Why Synthetic Time Series Are Generated

The fitted models are used to generate 10 possible monthly sequences for the next 10 years. These are not forecasts of exact future events. They are stochastic samples from the fitted statistical process.

The objective is to compare long-term statistical properties: mean, variance, autocorrelation, and sediment mass estimates.

## 9. How Sediment Mass Is Computed

The assignment gives:

```text
M(t) = C(t) * Q(t)
```

Here:

```text
C = g/L
Q = m3/s
```

Because:

```text
1 g/L = 1 kg/m3
```

the unit becomes:

```text
kg/m3 * m3/s = kg/s
```

So `C[g/L] * Q[m3/s]` directly gives `kg/s`.

## 10. Why Q and C May Not Be Independent

Q and C often depend on each other. During high flow, rivers may mobilize more sediment, increasing concentration. However, the relationship may be nonlinear and can depend on season, sediment availability, and whether the hydrograph is rising or falling.

If Q and C are simulated independently, the model may combine high Q with unrealistically low C, or low Q with unrealistically high C. Since sediment mass is a product, this can distort mass estimates.

Better approaches include:

- sediment rating curves such as `C = f(Q)`;
- conditional simulation of C given Q;
- copulas for joint distributions;
- VAR or VARMA models;
- event-scale hysteresis analysis.

## 11. How to Explain the Project Orally

A clear presentation can follow this structure:

1. We studied Ill at Gisingen and Rhein downstream at Diepoldsau.
2. We aggregated raw 10/15-minute data to monthly means.
3. We tested trends and removed the mean or significant linear trend.
4. We used ACF and PACF to choose AR and ARMA candidate models.
5. We fitted models and checked residuals using ACF, Ljung-Box, and normality diagnostics.
6. We generated 10 synthetic 10-year monthly series for long-term comparison.
7. We calculated sediment mass as `C * Q`, with units kg/s.
8. We estimated Ill contribution relative to Diepoldsau/Rhein.
9. We tested Q-C dependence and explained why independent simulation is a limitation.
10. We kept all logic in `.py` files and used Git branches and pull requests for collaboration.


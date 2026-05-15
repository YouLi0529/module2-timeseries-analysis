"""Section 1: monthly timeseries review, trend tests, and normalization."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller

from .data_loading import StationData, flatten_station_data


def linear_trend_test(series: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
    """Fit a linear trend and test whether its slope differs from zero.

    Inputs:
        series (pd.Series): Monthly numeric timeseries.
        alpha (float): Significance level for the slope test.

    Outputs:
        dict: Slope, intercept, p-value, fitted trend series, and significance flag.
    """

    clean = series.dropna().astype(float)
    if len(clean) < 3:
        raise ValueError("At least three monthly observations are required for a trend test.")
    x = np.arange(len(clean), dtype=float)
    result = stats.linregress(x, clean.to_numpy())
    fitted = pd.Series(result.intercept + result.slope * x, index=clean.index, name="trend")
    return {
        "slope": float(result.slope),
        "intercept": float(result.intercept),
        "r_value": float(result.rvalue),
        "p_value": float(result.pvalue),
        "std_error": float(result.stderr),
        "significant": bool(result.pvalue < alpha),
        "alpha": alpha,
        "trend": fitted,
    }


def adf_stationarity_test(series: pd.Series) -> Dict[str, Any]:
    """Run an Augmented Dickey-Fuller stationarity test when enough data exist.

    Inputs:
        series (pd.Series): Monthly numeric timeseries.

    Outputs:
        dict: ADF statistic, p-value, used lag count, and an interpretation string.
    """

    clean = series.dropna().astype(float)
    if len(clean) < 12:
        return {
            "statistic": np.nan,
            "p_value": np.nan,
            "used_lags": None,
            "interpretation": "Too few observations for a reliable ADF test.",
        }
    try:
        statistic, p_value, used_lags, nobs, critical_values, _ = adfuller(clean, autolag="AIC")
    except Exception as exc:
        return {
            "statistic": np.nan,
            "p_value": np.nan,
            "used_lags": None,
            "interpretation": f"ADF test failed: {exc}",
        }
    interpretation = (
        "Reject unit-root null at 5%; evidence is consistent with stationarity."
        if p_value < 0.05
        else "Do not reject unit-root null at 5%; stationarity is not strongly supported."
    )
    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "used_lags": int(used_lags),
        "nobs": int(nobs),
        "critical_values": critical_values,
        "interpretation": interpretation,
    }


def normalize_or_detrend(series: pd.Series, trend_result: Dict[str, Any]) -> Dict[str, Any]:
    """Remove the mean or a statistically significant linear trend from a series.

    Inputs:
        series (pd.Series): Monthly numeric timeseries.
        trend_result (dict): Output from linear_trend_test.

    Outputs:
        dict: Normalized series, removed component metadata, mean, and variance.
    """

    clean = series.dropna().astype(float)
    if trend_result["significant"]:
        base = trend_result["trend"].reindex(clean.index)
        residual = clean - base
        offset = float(residual.mean())
        normalized = residual - offset
        removed = "linear_trend"
    else:
        offset = float(clean.mean())
        base = pd.Series(offset, index=clean.index, name="mean")
        normalized = clean - offset
        removed = "mean"

    normalized.name = f"{clean.name or 'series'}_normalized"
    return {
        "series": normalized,
        "removed": removed,
        "base": base,
        "offset": offset,
        "mean_after": float(normalized.mean()),
        "variance_after": float(normalized.var(ddof=1)),
        "n": int(normalized.count()),
    }


def review_one_series(series: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
    """Run Section 1 tests and normalization for one monthly series.

    Inputs:
        series (pd.Series): Monthly Q or C timeseries.
        alpha (float): Significance level for trend testing.

    Outputs:
        dict: Original series, trend test, ADF test, normalized series, and metadata.
    """

    trend = linear_trend_test(series, alpha=alpha)
    stationarity = adf_stationarity_test(series)
    normalization = normalize_or_detrend(series, trend)
    return {
        "original": series.dropna().astype(float),
        "trend": trend,
        "stationarity": stationarity,
        "normalization": normalization,
    }


def run_timeseries_review(monthly_data: StationData, alpha: float = 0.05) -> Dict[str, Dict[str, Any]]:
    """Run Section 1 for every station and variable.

    Inputs:
        monthly_data (StationData): Monthly mean Q and C data by station.
        alpha (float): Significance level for slope tests.

    Outputs:
        dict[str, dict]: Results keyed by labels such as "Gisingen_Q".
    """

    return {
        label: review_one_series(series.rename(label), alpha=alpha)
        for label, series in flatten_station_data(monthly_data).items()
    }


def normalized_series_collection(review_results: Dict[str, Dict[str, Any]]) -> Dict[str, pd.Series]:
    """Extract normalized/detrended series from Section 1 results.

    Inputs:
        review_results (dict): Output from run_timeseries_review.

    Outputs:
        dict[str, pd.Series]: Normalized monthly series keyed by station-variable label.
    """

    return {
        label: result["normalization"]["series"].rename(label)
        for label, result in review_results.items()
    }


def format_timeseries_review(review_results: Dict[str, Dict[str, Any]]) -> str:
    """Format Section 1 results for notebook printing.

    Inputs:
        review_results (dict): Output from run_timeseries_review.

    Outputs:
        str: Human-readable summary of slope tests and normalization choices.
    """

    lines = []
    for label, result in review_results.items():
        trend = result["trend"]
        norm = result["normalization"]
        adf = result["stationarity"]
        lines.append(f"{label}")
        lines.append(f"  slope per month: {trend['slope']:.6g}")
        lines.append(f"  slope p-value: {trend['p_value']:.4g}")
        lines.append(f"  significant trend at 5%: {trend['significant']}")
        lines.append(f"  ADF p-value: {adf['p_value']:.4g}" if np.isfinite(adf["p_value"]) else f"  ADF: {adf['interpretation']}")
        lines.append(f"  stationarity note: {adf['interpretation']}")
        lines.append(f"  removed component: {norm['removed']}")
        lines.append(f"  mean after removal: {norm['mean_after']:.6g}")
        lines.append(f"  variance after removal: {norm['variance_after']:.6g}")
    return "\n".join(lines)


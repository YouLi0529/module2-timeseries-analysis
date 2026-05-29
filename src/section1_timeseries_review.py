"""Section 1: monthly timeseries review and trend removal."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller

from .data_loading import StationData, flatten_station_data


def analyse_one_series(series: pd.Series, alpha: float = 0.05) -> dict:
    """Analyse trend, stationarity, and zero-mean transformation for one series.

    Inputs:
        series (pd.Series): Monthly Q or C values indexed by datetime.
        alpha (float): Significance level for the linear trend test.

    Outputs:
        dict: Original series, trend statistics, ADF p-value, normalized series,
        removed component, and variance after transformation.
    """

    clean = series.dropna().astype(float)
    if len(clean) < 12:
        raise ValueError("Section 1 needs at least 12 monthly values per series.")

    x = np.arange(len(clean), dtype=float)
    trend_fit = stats.linregress(x, clean.to_numpy())
    trend_line = pd.Series(
        trend_fit.intercept + trend_fit.slope * x,
        index=clean.index,
        name="trend",
    )
    significant_trend = bool(trend_fit.pvalue < alpha)

    adf_statistic, adf_p_value, *_ = adfuller(clean, autolag="AIC")

    if significant_trend:
        residual = clean - trend_line
        offset = float(residual.mean())
        normalized = residual - offset
        removed = "linear_trend"
    else:
        offset = float(clean.mean())
        normalized = clean - offset
        removed = "mean"

    normalized.name = clean.name
    return {
        "original": clean,
        "slope": float(trend_fit.slope),
        "intercept": float(trend_fit.intercept),
        "trend_p_value": float(trend_fit.pvalue),
        "significant_trend": significant_trend,
        "trend_line": trend_line,
        "adf_statistic": float(adf_statistic),
        "adf_p_value": float(adf_p_value),
        "adf_stationary_at_5": bool(adf_p_value < alpha),
        "removed": removed,
        "offset": offset,
        "normalized": normalized,
        "mean_after": float(normalized.mean()),
        "variance_after": float(normalized.var(ddof=1)),
    }


def run_timeseries_review(monthly_data: StationData, alpha: float = 0.05) -> Dict[str, dict]:
    """Run Section 1 analysis for all station-variable series.

    Inputs:
        monthly_data (StationData): Monthly mean Q and C data by station.
        alpha (float): Significance level for trend and ADF tests.

    Outputs:
        dict[str, dict]: Section 1 results keyed by labels such as "Gisingen_Q".
    """

    results: Dict[str, dict] = {}
    for label, series in flatten_station_data(monthly_data).items():
        results[label] = analyse_one_series(series.rename(label), alpha=alpha)
    return results


def normalized_series_collection(review_results: Dict[str, dict]) -> Dict[str, pd.Series]:
    """Collect normalized series from Section 1 results.

    Inputs:
        review_results (dict[str, dict]): Output from run_timeseries_review.

    Outputs:
        dict[str, pd.Series]: Normalized series keyed by station-variable label.
    """

    return {
        label: result["normalized"].rename(label)
        for label, result in review_results.items()
    }


def format_timeseries_review(review_results: Dict[str, dict]) -> str:
    """Format Section 1 results for notebook printing.

    Inputs:
        review_results (dict[str, dict]): Output from run_timeseries_review.

    Outputs:
        str: Readable summary of trend tests and transformations.
    """

    lines = []
    for label, result in review_results.items():
        adf_note = "stationary" if result["adf_stationary_at_5"] else "not clearly stationary"
        lines.append(f"{label}")
        lines.append(f"  slope per month: {result['slope']:.6g}")
        lines.append(f"  slope p-value: {result['trend_p_value']:.4g}")
        lines.append(f"  significant trend at 5%: {result['significant_trend']}")
        lines.append(f"  ADF p-value: {result['adf_p_value']:.4g} ({adf_note} at 5%)")
        lines.append(f"  removed component: {result['removed']}")
        lines.append(f"  mean after removal: {result['mean_after']:.6g}")
        lines.append(f"  variance after removal: {result['variance_after']:.6g}")
    return "\n".join(lines)


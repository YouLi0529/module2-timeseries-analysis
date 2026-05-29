"""Section 2: ACF/PACF analysis and simple AR/ARMA order selection."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf, pacf


def significant_lags(values: np.ndarray, confidence: float) -> list[int]:
    """Find lags that pass the approximate confidence bound.

    Inputs:
        values (np.ndarray): ACF or PACF values, including lag zero.
        confidence (float): Approximate 95% confidence bound.
    Outputs:
        list[int]: Significant lag numbers, excluding lag zero.
    """

    return [
        lag
        for lag, value in enumerate(values[1:], start=1)
        if abs(value) > confidence
    ]


def choose_order_from_lags(significant: list[int], maximum: int = 6) -> int:
    """Choose a small model order from significant lags.

    Inputs:
        significant (list[int]): Significant lag numbers.
        maximum (int): Largest allowed AR or MA order.
    Outputs:
        int: Chosen order between 1 and maximum.
    """

    return min(max(significant or [1]), maximum)


def analyse_acf_pacf_collection(
    normalized_series: dict[str, pd.Series],
    nlags: int = 24,
    max_order: int = 6,
) -> dict[str, dict]:
    """Compute ACF/PACF and choose candidate AR and ARMA orders.

    Inputs:
        normalized_series (dict[str, pd.Series]): Zero-mean series from Section 1.
        nlags (int): Number of monthly lags to calculate.
        max_order (int): Maximum AR or MA order to allow.
    Outputs:
        dict[str, dict]: ACF/PACF values, confidence bounds, and candidate orders.
    """

    results: dict[str, dict] = {}
    for label, series in normalized_series.items():
        clean = series.dropna().astype(float)
        acf_values = acf(clean, nlags=nlags, fft=True)
        pacf_values = pacf(clean, nlags=nlags, method="ywm")
        confidence = float(1.96 / np.sqrt(len(clean)))
        acf_lags = significant_lags(acf_values, confidence)
        pacf_lags = significant_lags(pacf_values, confidence)

        p = choose_order_from_lags(pacf_lags, maximum=max_order)
        q = choose_order_from_lags(acf_lags, maximum=max_order)

        results[label] = {
            "lags": np.arange(nlags + 1),
            "acf": acf_values,
            "pacf": pacf_values,
            "confidence": confidence,
            "significant_acf_lags": acf_lags,
            "significant_pacf_lags": pacf_lags,
            "ar_order": (p, 0, 0),
            "arma_order": (p, 0, q),
        }
    return results


def format_order_selection(order_results: dict[str, dict]) -> str:
    """Format Section 2 order-selection results for printing.

    Inputs:
        order_results (dict[str, dict]): Results from analyse_acf_pacf_collection.
    Outputs:
        str: Human-readable summary of significant lags and model orders.
    """

    lines = []
    for label, result in order_results.items():
        lines.append(f"{label}")
        lines.append(f"  significant PACF lags: {result['significant_pacf_lags'] or 'none'}")
        lines.append(f"  significant ACF lags: {result['significant_acf_lags'] or 'none'}")
        lines.append(f"  AR candidate order: {result['ar_order']}")
        lines.append(f"  ARMA candidate order: {result['arma_order']}")
        lines.append("  note: orders are capped at 6 to keep the models simple.")
    return "\n".join(lines)

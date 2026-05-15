"""Section 2: ACF/PACF analysis and candidate AR/ARMA order selection."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf, pacf


def default_nlags(series: pd.Series, maximum: int = 36) -> int:
    """Choose a safe number of lags for monthly ACF/PACF analysis.

    Inputs:
        series (pd.Series): Monthly normalized timeseries.
        maximum (int): Maximum lag count allowed.

    Outputs:
        int: Lag count, at least 1 and not more than one third of sample size.
    """

    n = len(series.dropna())
    return max(1, min(maximum, n // 3))


def compute_acf_pacf(series: pd.Series, nlags: int | None = None) -> Dict[str, Any]:
    """Compute empirical ACF, PACF, and approximate 95% confidence bounds.

    Inputs:
        series (pd.Series): Normalized monthly timeseries.
        nlags (int | None): Number of lags. If None, a safe default is used.

    Outputs:
        dict: ACF, PACF, lags, confidence bound, and sample size.
    """

    clean = series.dropna().astype(float)
    if len(clean) < 8:
        raise ValueError("At least eight observations are required for ACF/PACF analysis.")
    nlags = default_nlags(clean) if nlags is None else int(nlags)
    nlags = min(nlags, len(clean) // 2 - 1)
    acf_values = acf(clean, nlags=nlags, fft=True, missing="drop")
    pacf_values = pacf(clean, nlags=nlags, method="ywm")
    conf = 1.96 / np.sqrt(len(clean))
    return {
        "lags": np.arange(nlags + 1),
        "acf": acf_values,
        "pacf": pacf_values,
        "confidence": float(conf),
        "n": int(len(clean)),
    }


def significant_lags(values: np.ndarray, confidence: float) -> list[int]:
    """Identify lags whose correlation magnitude exceeds a confidence bound.

    Inputs:
        values (np.ndarray): ACF or PACF values including lag zero.
        confidence (float): Symmetric confidence bound.

    Outputs:
        list[int]: Significant lag numbers excluding lag zero.
    """

    return [int(lag) for lag, value in enumerate(values[1:], start=1) if abs(value) > confidence]


def select_candidate_orders(
    acf_pacf_result: Dict[str, Any],
    max_ar: int = 6,
    max_ma: int = 6,
) -> Dict[str, Any]:
    """Select candidate AR and ARMA orders from significant ACF/PACF lags.

    Inputs:
        acf_pacf_result (dict): Output from compute_acf_pacf.
        max_ar (int): Maximum AR order to propose.
        max_ma (int): Maximum MA order to propose.

    Outputs:
        dict: Candidate AR order, ARMA order, significant lags, and justification.
    """

    acf_lags = significant_lags(acf_pacf_result["acf"], acf_pacf_result["confidence"])
    pacf_lags = significant_lags(acf_pacf_result["pacf"], acf_pacf_result["confidence"])

    ar_p = min(max(pacf_lags) if pacf_lags else 1, max_ar)
    arma_p = max(1, min(ar_p, max_ar))
    arma_q = min(max(acf_lags) if acf_lags else 1, max_ma)

    justification = (
        f"PACF significant lags={pacf_lags or 'none'} suggest AR p={ar_p}; "
        f"ACF significant lags={acf_lags or 'none'} suggest MA q={arma_q}. "
        "Orders are capped to keep the model parsimonious and stable."
    )
    return {
        "ar_order": (int(ar_p), 0, 0),
        "arma_order": (int(arma_p), 0, int(arma_q)),
        "significant_acf_lags": acf_lags,
        "significant_pacf_lags": pacf_lags,
        "justification": justification,
    }


def analyse_acf_pacf_collection(
    normalized_series: Dict[str, pd.Series],
    nlags: int | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Run ACF/PACF analysis and order selection for all normalized series.

    Inputs:
        normalized_series (dict[str, pd.Series]): Series from Section 1.
        nlags (int | None): Number of lags for all series, or None for default.

    Outputs:
        dict[str, dict]: ACF/PACF arrays and selected candidate model orders.
    """

    results: Dict[str, Dict[str, Any]] = {}
    for label, series in normalized_series.items():
        acf_pacf_result = compute_acf_pacf(series, nlags=nlags)
        orders = select_candidate_orders(acf_pacf_result)
        results[label] = {"acf_pacf": acf_pacf_result, "orders": orders}
    return results


def format_order_selection(order_results: Dict[str, Dict[str, Any]]) -> str:
    """Format Section 2 order-selection results for notebook printing.

    Inputs:
        order_results (dict): Output from analyse_acf_pacf_collection.

    Outputs:
        str: Human-readable selected orders and justification.
    """

    lines = []
    for label, result in order_results.items():
        orders = result["orders"]
        lines.append(f"{label}")
        lines.append(f"  AR candidate order: {orders['ar_order']}")
        lines.append(f"  ARMA candidate order: {orders['arma_order']}")
        lines.append(f"  justification: {orders['justification']}")
    return "\n".join(lines)


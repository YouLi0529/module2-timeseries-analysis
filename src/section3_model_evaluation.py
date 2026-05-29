"""Section 3: fit AR/ARMA models and check residuals."""

from __future__ import annotations

from typing import Any, Dict
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.arima_process import ArmaProcess
from statsmodels.tsa.stattools import acf


def fit_model(series: pd.Series, order: tuple[int, int, int]) -> Any:
    """Fit one zero-mean AR or ARMA model.

    Inputs:
        series (pd.Series): Normalized monthly series from Section 1.
        order (tuple[int, int, int]): ARIMA order, with d=0 in this project.

    Outputs:
        statsmodels result: Fitted model object.
    """

    clean = series.dropna().astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ARIMA(
            clean,
            order=order,
            trend="n",
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit()


def model_theoretical_acf(fit_result: Any, nlags: int) -> np.ndarray:
    """Compute theoretical ACF from fitted ARMA parameters.

    Inputs:
        fit_result: Fitted statsmodels ARIMA result.
        nlags (int): Number of lags to include.

    Outputs:
        np.ndarray: Theoretical ACF from lag 0 to nlags.
    """

    ar = np.r_[1.0, -np.asarray(fit_result.arparams)]
    ma = np.r_[1.0, np.asarray(fit_result.maparams)]
    return ArmaProcess(ar, ma).acf(lags=nlags + 1)


def residual_normality(residuals: pd.Series) -> dict:
    """Calculate simple residual normality diagnostics.

    Inputs:
        residuals (pd.Series): Model residuals.

    Outputs:
        dict: PPCC and Shapiro-Wilk p-value.
    """

    clean = residuals.dropna().astype(float)
    (osm, osr), _ = stats.probplot(clean, dist="norm")
    ppcc = float(np.corrcoef(osm, osr)[0, 1])
    shapiro_p_value = float(stats.shapiro(clean).pvalue)
    return {
        "ppcc": ppcc,
        "shapiro_p_value": shapiro_p_value,
        "normal_at_5": bool(shapiro_p_value >= 0.05),
    }


def evaluate_one_model(
    series: pd.Series,
    order: tuple[int, int, int],
    nlags: int = 24,
    alpha: float = 0.05,
) -> dict:
    """Fit one candidate model and calculate diagnostics.

    Inputs:
        series (pd.Series): Normalized monthly series.
        order (tuple[int, int, int]): Candidate AR or ARMA order.
        nlags (int): Number of ACF lags for plots and diagnostics.
        alpha (float): Significance level for the Ljung-Box test.

    Outputs:
        dict: Fitted model, AIC/BIC, ACFs, residuals, and diagnostic p-values.
    """

    clean = series.dropna().astype(float)
    fit_result = fit_model(clean, order)
    residuals = pd.Series(fit_result.resid, index=clean.index[-len(fit_result.resid) :], name="residual").dropna()
    ljung = acorr_ljungbox(residuals, lags=[12], return_df=True)
    ljung_p_value = float(ljung["lb_pvalue"].iloc[0])

    return {
        "order": order,
        "fit": fit_result,
        "aic": float(fit_result.aic),
        "bic": float(fit_result.bic),
        "lags": np.arange(nlags + 1),
        "confidence": float(1.96 / np.sqrt(len(clean))),
        "empirical_acf": acf(clean, nlags=nlags, fft=True),
        "theoretical_acf": model_theoretical_acf(fit_result, nlags),
        "residuals": residuals,
        "residual_acf": acf(residuals, nlags=nlags, fft=True),
        "ljung_box_p_value": ljung_p_value,
        "residuals_independent": bool(ljung_p_value >= alpha),
        "normality": residual_normality(residuals),
        "model_type": "AR" if order[2] == 0 else "ARMA",
    }


def choose_model(ar_result: dict, arma_result: dict) -> str:
    """Choose AR or ARMA using residual independence first, then BIC.

    Inputs:
        ar_result (dict): Diagnostics for the AR candidate.
        arma_result (dict): Diagnostics for the ARMA candidate.

    Outputs:
        str: "AR" or "ARMA".
    """

    if ar_result["residuals_independent"] and not arma_result["residuals_independent"]:
        return "AR"
    if arma_result["residuals_independent"] and not ar_result["residuals_independent"]:
        return "ARMA"
    return "AR" if ar_result["bic"] <= arma_result["bic"] else "ARMA"


def evaluate_model_collection(
    normalized_series: Dict[str, pd.Series],
    order_results: Dict[str, dict],
    nlags: int = 24,
    alpha: float = 0.05,
) -> Dict[str, dict]:
    """Fit AR and ARMA candidates for all series and choose final models.

    Inputs:
        normalized_series (dict[str, pd.Series]): Normalized series from Section 1.
        order_results (dict[str, dict]): Candidate orders from Section 2.
        nlags (int): Number of lags for diagnostic plots.
        alpha (float): Significance level for the Ljung-Box test.

    Outputs:
        dict[str, dict]: AR diagnostics, ARMA diagnostics, and chosen model.
    """

    results: Dict[str, dict] = {}
    for label, series in normalized_series.items():
        ar_result = evaluate_one_model(series, order_results[label]["ar_order"], nlags, alpha)
        arma_result = evaluate_one_model(series, order_results[label]["arma_order"], nlags, alpha)
        chosen_name = choose_model(ar_result, arma_result)
        chosen = ar_result if chosen_name == "AR" else arma_result

        results[label] = {
            "AR": ar_result,
            "ARMA": arma_result,
            "chosen_name": chosen_name,
            "chosen": chosen,
        }
    return results


def format_model_evaluation(evaluation_results: Dict[str, dict]) -> str:
    """Format Section 3 model diagnostics for notebook printing.

    Inputs:
        evaluation_results (dict[str, dict]): Output from evaluate_model_collection.

    Outputs:
        str: Readable model comparison and final model choices.
    """

    lines = []
    for label, result in evaluation_results.items():
        lines.append(f"{label}")
        for model_name in ("AR", "ARMA"):
            model = result[model_name]
            normality = model["normality"]
            lines.append(
                f"  {model_name} order={model['order']} "
                f"AIC={model['aic']:.2f}, BIC={model['bic']:.2f}"
            )
            lines.append(
                f"    Ljung-Box p={model['ljung_box_p_value']:.4g}; "
                f"residuals independent at 5%: {model['residuals_independent']}"
            )
            lines.append(
                f"    PPCC={normality['ppcc']:.4f}; "
                f"Shapiro p={normality['shapiro_p_value']:.4g}; "
                f"normal at 5%: {normality['normal_at_5']}"
            )
        lines.append(f"  chosen model: {result['chosen_name']} {result['chosen']['order']}")
    return "\n".join(lines)


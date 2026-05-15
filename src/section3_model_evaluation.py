"""Section 3: AR/ARMA fitting, residual diagnostics, and model choice."""

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


def fit_arima_model(series: pd.Series, order: tuple[int, int, int]) -> Any:
    """Fit a zero-mean ARIMA model used here as AR or ARMA.

    Inputs:
        series (pd.Series): Normalized monthly timeseries with mean near zero.
        order (tuple[int, int, int]): ARIMA order (p, d, q). This project uses d=0.

    Outputs:
        statsmodels result: Fitted ARIMA results object.
    """

    clean = series.dropna().astype(float)
    if len(clean) < 12:
        raise ValueError("At least 12 observations are required to fit AR/ARMA models.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = ARIMA(
            clean,
            order=order,
            trend="n",
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        return model.fit()


def theoretical_arma_acf(fit_result: Any, nlags: int) -> np.ndarray:
    """Compute the theoretical ACF implied by a fitted ARMA model.

    Inputs:
        fit_result: Fitted statsmodels ARIMA results object.
        nlags (int): Number of lags to return, including lag zero.

    Outputs:
        np.ndarray: Theoretical ACF values from lag 0 through nlags.
    """

    try:
        ar = np.r_[1.0, -np.asarray(fit_result.arparams)]
        ma = np.r_[1.0, np.asarray(fit_result.maparams)]
        process = ArmaProcess(ar, ma)
        return process.acf(lags=nlags + 1)
    except Exception:
        return np.full(nlags + 1, np.nan)


def residual_normality_diagnostics(residuals: pd.Series) -> Dict[str, Any]:
    """Assess residual normality with probability-plot correlation and Shapiro test.

    Inputs:
        residuals (pd.Series): Model residual series.

    Outputs:
        dict: PPCC statistic, Shapiro p-value, and interpretation.
    """

    clean = residuals.dropna().astype(float)
    if len(clean) < 8:
        return {
            "ppcc": np.nan,
            "shapiro_p_value": np.nan,
            "interpretation": "Too few residuals for a reliable normality assessment.",
        }
    (osm, osr), _ = stats.probplot(clean, dist="norm")
    ppcc = float(np.corrcoef(osm, osr)[0, 1])
    if len(clean) <= 5000:
        shapiro_p = float(stats.shapiro(clean).pvalue)
    else:
        shapiro_p = float(stats.normaltest(clean).pvalue)
    interpretation = (
        "Do not reject normality at 5%."
        if shapiro_p >= 0.05
        else "Reject normality at 5%; residuals are not well described by a normal distribution."
    )
    return {
        "ppcc": ppcc,
        "shapiro_p_value": shapiro_p,
        "interpretation": interpretation,
    }


def evaluate_model(
    series: pd.Series,
    order: tuple[int, int, int],
    nlags: int = 24,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Fit one AR/ARMA model and calculate diagnostics.

    Inputs:
        series (pd.Series): Normalized monthly timeseries.
        order (tuple[int, int, int]): ARIMA order.
        nlags (int): Number of ACF lags for diagnostics.
        alpha (float): Significance level for residual independence tests.

    Outputs:
        dict: Fitted model, ACF comparison, residual diagnostics, and decision flags.
    """

    clean = series.dropna().astype(float)
    nlags = max(1, min(nlags, len(clean) // 3))
    fit_result = fit_arima_model(clean, order)
    residuals = pd.Series(fit_result.resid, index=clean.index[-len(fit_result.resid) :], name="residual")
    residuals = residuals.dropna()
    empirical_acf = acf(clean, nlags=nlags, fft=True, missing="drop")
    residual_acf = acf(residuals, nlags=nlags, fft=True, missing="drop")
    confidence = 1.96 / np.sqrt(len(clean))
    ljung_lag = max(1, min(12, len(residuals) // 4))
    ljung = acorr_ljungbox(residuals, lags=[ljung_lag], return_df=True)
    ljung_p = float(ljung["lb_pvalue"].iloc[-1])
    normality = residual_normality_diagnostics(residuals)
    return {
        "order": order,
        "fit": fit_result,
        "aic": float(fit_result.aic),
        "bic": float(fit_result.bic),
        "residuals": residuals,
        "empirical_acf": empirical_acf,
        "theoretical_acf": theoretical_arma_acf(fit_result, nlags),
        "residual_acf": residual_acf,
        "lags": np.arange(nlags + 1),
        "confidence": float(confidence),
        "ljung_box_lag": int(ljung_lag),
        "ljung_box_p_value": ljung_p,
        "residuals_independent": bool(ljung_p >= alpha),
        "normality": normality,
        "alpha": alpha,
        "model_type": "AR" if order[2] == 0 else "ARMA",
    }


def choose_best_model(candidate_results: Dict[str, Dict[str, Any]]) -> str:
    """Choose the most appropriate model using residual independence and BIC.

    Inputs:
        candidate_results (dict): Mapping from candidate name to evaluate_model output.

    Outputs:
        str: Candidate key selected as the final model.
    """

    independent = {
        name: result
        for name, result in candidate_results.items()
        if result["residuals_independent"]
    }
    pool = independent or candidate_results
    return min(pool, key=lambda name: (pool[name]["bic"], pool[name]["aic"]))


def evaluate_model_collection(
    normalized_series: Dict[str, pd.Series],
    order_results: Dict[str, Dict[str, Any]],
    nlags: int = 24,
    alpha: float = 0.05,
) -> Dict[str, Dict[str, Any]]:
    """Fit candidate AR and ARMA models for all series and select final models.

    Inputs:
        normalized_series (dict[str, pd.Series]): Section 1 normalized series.
        order_results (dict): Section 2 candidate order results.
        nlags (int): ACF lag count for model diagnostics.
        alpha (float): Significance level for Ljung-Box test.

    Outputs:
        dict[str, dict]: Candidate diagnostics and chosen model for each series.
    """

    output: Dict[str, Dict[str, Any]] = {}
    for label, series in normalized_series.items():
        orders = order_results[label]["orders"]
        candidates = {
            "AR": evaluate_model(series, orders["ar_order"], nlags=nlags, alpha=alpha),
            "ARMA": evaluate_model(series, orders["arma_order"], nlags=nlags, alpha=alpha),
        }
        chosen_key = choose_best_model(candidates)
        output[label] = {
            "candidates": candidates,
            "chosen_key": chosen_key,
            "chosen": candidates[chosen_key],
            "choice_reason": (
                f"Selected {chosen_key} because it has the best BIC among models "
                "with acceptable residual independence, or the best BIC overall if "
                "no candidate fully passed the Ljung-Box test."
            ),
        }
    return output


def format_model_evaluation(evaluation_results: Dict[str, Dict[str, Any]]) -> str:
    """Format Section 3 diagnostics for notebook printing.

    Inputs:
        evaluation_results (dict): Output from evaluate_model_collection.

    Outputs:
        str: Human-readable diagnostics and chosen models.
    """

    lines = []
    for label, result in evaluation_results.items():
        lines.append(f"{label}")
        for candidate_name, candidate in result["candidates"].items():
            normality = candidate["normality"]
            lines.append(
                f"  {candidate_name} order={candidate['order']} "
                f"AIC={candidate['aic']:.2f} BIC={candidate['bic']:.2f}"
            )
            lines.append(
                f"    Ljung-Box lag {candidate['ljung_box_lag']} p={candidate['ljung_box_p_value']:.4g}; "
                f"residuals independent at 5%: {candidate['residuals_independent']}"
            )
            lines.append(
                f"    PPCC={normality['ppcc']:.4f}; normality p={normality['shapiro_p_value']:.4g}; "
                f"{normality['interpretation']}"
            )
        lines.append(f"  chosen model: {result['chosen_key']} {result['chosen']['order']}")
        lines.append(f"  reason: {result['choice_reason']}")
    return "\n".join(lines)


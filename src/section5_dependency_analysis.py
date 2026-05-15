"""Section 5: Q-C dependency analysis for both stations."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from scipy import stats

from .data_loading import StationData, align_station_q_c


def correlation_tests(frame: pd.DataFrame) -> Dict[str, Any]:
    """Compute Pearson, Spearman, and Kendall dependency tests for Q and C.

    Inputs:
        frame (pd.DataFrame): DataFrame with aligned Q and C columns.

    Outputs:
        dict: Correlation coefficients, p-values, sample size, and interpretation.
    """

    clean = frame[["Q", "C"]].dropna().astype(float)
    if len(clean) < 3:
        raise ValueError("At least three aligned Q-C observations are required.")
    pearson = stats.pearsonr(clean["Q"], clean["C"])
    spearman = stats.spearmanr(clean["Q"], clean["C"])
    kendall = stats.kendalltau(clean["Q"], clean["C"])
    independent_at_5 = all(
        p_value >= 0.05
        for p_value in (pearson.pvalue, spearman.pvalue, kendall.pvalue)
    )
    interpretation = (
        "No correlation test rejects independence at 5%; independence is not disproved by these tests."
        if independent_at_5
        else "At least one correlation test rejects no association at 5%; treating Q and C as independent is questionable."
    )
    return {
        "n": int(len(clean)),
        "pearson_r": float(pearson.statistic),
        "pearson_p": float(pearson.pvalue),
        "spearman_rho": float(spearman.statistic),
        "spearman_p": float(spearman.pvalue),
        "kendall_tau": float(kendall.statistic),
        "kendall_p": float(kendall.pvalue),
        "independent_at_5": bool(independent_at_5),
        "interpretation": interpretation,
        "aligned_data": clean,
    }


def run_dependency_analysis(monthly_data: StationData) -> Dict[str, Dict[str, Any]]:
    """Run Q-C dependency analysis for each station.

    Inputs:
        monthly_data (StationData): Monthly Q and C data by station.

    Outputs:
        dict[str, dict]: Correlation results keyed by station name.
    """

    return {
        station: correlation_tests(align_station_q_c(monthly_data, station))
        for station in monthly_data
    }


def format_dependency_results(dependency_results: Dict[str, Dict[str, Any]]) -> str:
    """Format Section 5 dependency results for notebook printing.

    Inputs:
        dependency_results (dict): Output from run_dependency_analysis.

    Outputs:
        str: Human-readable correlation and independence summary.
    """

    lines = []
    for station, result in dependency_results.items():
        lines.append(f"{station}")
        lines.append(f"  aligned monthly observations: {result['n']}")
        lines.append(f"  Pearson r={result['pearson_r']:.4f}, p={result['pearson_p']:.4g}")
        lines.append(f"  Spearman rho={result['spearman_rho']:.4f}, p={result['spearman_p']:.4g}")
        lines.append(f"  Kendall tau={result['kendall_tau']:.4f}, p={result['kendall_p']:.4g}")
        lines.append(f"  independent at 5% by these tests: {result['independent_at_5']}")
        lines.append(f"  interpretation: {result['interpretation']}")
    return "\n".join(lines)


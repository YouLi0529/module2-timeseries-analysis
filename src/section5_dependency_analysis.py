"""Q-C dependency tests."""

from __future__ import annotations

import pandas as pd
from scipy import stats

from .data_loading import StationData, align_station_q_c


def correlation_tests(frame: pd.DataFrame) -> dict:
    clean = frame[["Q", "C"]].dropna().astype(float)
    if len(clean) < 3:
        raise ValueError("Need 3+ pairs.")
    
    pr = stats.pearsonr(clean["Q"], clean["C"])
    sr = stats.spearmanr(clean["Q"], clean["C"])
    kt = stats.kendalltau(clean["Q"], clean["C"])
    
    indep = all(pv >= 0.05 for pv in (pr.pvalue, sr.pvalue, kt.pvalue))
    note = "No test rejects independence." if indep else "At least one test rejects independence."
    
    return {
        "n": int(len(clean)),
        "pr": float(pr.statistic),
        "pp": float(pr.pvalue),
        "sr": float(sr.statistic),
        "sp": float(sr.pvalue),
        "kt": float(kt.statistic),
        "kp": float(kt.pvalue),
        "indep": bool(indep),
        "note": note,
        "data": clean,
    }


def run_dependency_analysis(monthly_data: StationData) -> dict:
    return {st: correlation_tests(align_station_q_c(monthly_data, st)) for st in monthly_data}


def format_dependency_results(res_dict: dict) -> str:
    lines = []
    for st, res in res_dict.items():
        lines.extend([
            f"{st}",
            f"  n={res['n']}",
            f"  Pearson r={res['pr']:.4f}, p={res['pp']:.4g}",
            f"  Spearman rho={res['sr']:.4f}, p={res['sp']:.4g}",
            f"  Kendall tau={res['kt']:.4f}, p={res['kp']:.4g}",
            f"  {res['note']}"
        ])
    return "\n".join(lines)
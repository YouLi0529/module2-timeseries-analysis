"""Section 4: synthetic series generation and sediment influence estimates."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd
from statsmodels.tsa.arima_process import ArmaProcess

from .data_loading import StationData, align_station_q_c


def concentration_gL_times_discharge_m3s_to_kg_s(concentration_gL: pd.Series, discharge_m3s: pd.Series) -> pd.Series:
    """Convert suspended sediment concentration and discharge to mass rate.

    Inputs:
        concentration_gL (pd.Series): Suspended sediment concentration in g/L.
        discharge_m3s (pd.Series): Discharge in m^3/s.

    Outputs:
        pd.Series: Sediment mass rate in kg/s. The conversion is direct because
        1 g/L equals 1 kg/m^3, so C[g/L] * Q[m^3/s] = kg/s.
    """

    aligned = pd.concat({"C": concentration_gL, "Q": discharge_m3s}, axis=1).dropna()
    mass = aligned["C"] * aligned["Q"]
    mass.name = "sediment_mass_kg_s"
    return mass


def compute_sediment_yields(mass_kg_s: pd.Series) -> Dict[str, Any]:
    """Compute monthly and yearly sediment mass summaries.

    Inputs:
        mass_kg_s (pd.Series): Monthly sediment mass rate in kg/s.

    Outputs:
        dict: Monthly table, monthly climatology, yearly table, and overall mean.
    """

    clean = mass_kg_s.dropna().astype(float).sort_index()
    if clean.empty:
        raise ValueError("Sediment mass series is empty after aligning Q and C.")
    monthly = pd.DataFrame({"mass_kg_s": clean})
    monthly["seconds_in_month"] = monthly.index.days_in_month * 24 * 60 * 60
    monthly["mass_kg_month"] = monthly["mass_kg_s"] * monthly["seconds_in_month"]
    monthly["mass_tonnes_month"] = monthly["mass_kg_month"] / 1000.0
    monthly["month"] = monthly.index.month
    monthly["year"] = monthly.index.year

    monthly_climatology = monthly.groupby("month")[["mass_kg_s", "mass_tonnes_month"]].mean()
    yearly = monthly.groupby("year").agg(
        mean_mass_kg_s=("mass_kg_s", "mean"),
        total_mass_tonnes=("mass_tonnes_month", "sum"),
    )
    return {
        "monthly": monthly,
        "monthly_climatology": monthly_climatology,
        "yearly": yearly,
        "overall_mean_kg_s": float(monthly["mass_kg_s"].mean()),
        "overall_mean_tonnes_per_month": float(monthly["mass_tonnes_month"].mean()),
    }


def _innovation_scale(fit_result: Any) -> float:
    residuals = np.asarray(fit_result.resid)
    residuals = residuals[np.isfinite(residuals)]
    if residuals.size < 2:
        return 1.0
    return float(np.std(residuals, ddof=1))


def simulate_normalized_paths(
    fit_result: Any,
    periods: int = 120,
    n_paths: int = 10,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate normalized synthetic paths from a fitted ARMA model.

    Inputs:
        fit_result: Fitted statsmodels ARIMA results object.
        periods (int): Number of future monthly steps to simulate.
        n_paths (int): Number of synthetic paths.
        seed (int): Random seed for reproducibility.

    Outputs:
        pd.DataFrame: Synthetic normalized values, columns path_1 ... path_n.
    """

    rng = np.random.default_rng(seed)
    ar = np.r_[1.0, -np.asarray(fit_result.arparams)]
    ma = np.r_[1.0, np.asarray(fit_result.maparams)]
    process = ArmaProcess(ar, ma)
    scale = _innovation_scale(fit_result)

    paths = {}
    for path_number in range(1, n_paths + 1):
        sample = process.generate_sample(
            nsample=periods,
            scale=scale,
            burnin=200,
            distrvs=rng.normal,
        )
        paths[f"path_{path_number}"] = sample
    return pd.DataFrame(paths)


def restore_physical_scale(
    normalized_paths: pd.DataFrame,
    review_result: Dict[str, Any],
    start_index: int,
    future_index: pd.DatetimeIndex,
    lower_bound: float = 0.0,
) -> Dict[str, Any]:
    """Restore normalized synthetic paths to physical Q or C scale for mass estimates.

    Inputs:
        normalized_paths (pd.DataFrame): Synthetic normalized series.
        review_result (dict): Section 1 result containing trend/mean metadata.
        start_index (int): First future integer time index after the observed record.
        future_index (pd.DatetimeIndex): Future monthly timestamps.
        lower_bound (float): Minimum allowed physical value, normally zero.

    Outputs:
        dict: Restored physical paths, clipping count, and transformation note.
    """

    normalized_paths = normalized_paths.copy()
    normalized_paths.index = future_index
    x = np.arange(start_index, start_index + len(normalized_paths), dtype=float)

    if review_result["removed"] == "linear_trend":
        base = review_result["intercept"] + review_result["slope"] * x + review_result["offset"]
        note = "Added back extrapolated linear trend and residual offset for physical-scale mass calculation."
    else:
        base = np.full(len(normalized_paths), review_result["offset"], dtype=float)
        note = "Added back historical mean for physical-scale mass calculation."

    restored = normalized_paths.add(base, axis=0)
    clipped_count = int((restored < lower_bound).sum().sum())
    if lower_bound is not None:
        restored = restored.clip(lower=lower_bound)
    return {"physical": restored, "clipped_count": clipped_count, "note": note}


def compare_synthetic_statistics(observed_normalized: pd.Series, synthetic_paths: pd.DataFrame) -> pd.DataFrame:
    """Compare observed normalized statistics against synthetic path statistics.

    Inputs:
        observed_normalized (pd.Series): Historical normalized monthly series.
        synthetic_paths (pd.DataFrame): Simulated normalized paths.

    Outputs:
        pd.DataFrame: Mean, standard deviation, variance, and lag-1 correlation.
    """

    observed = observed_normalized.dropna().astype(float)
    rows = {
        "observed": {
            "mean": observed.mean(),
            "std": observed.std(ddof=1),
            "variance": observed.var(ddof=1),
            "lag1_autocorrelation": observed.autocorr(lag=1),
        }
    }
    for column in synthetic_paths.columns:
        series = synthetic_paths[column].dropna().astype(float)
        rows[column] = {
            "mean": series.mean(),
            "std": series.std(ddof=1),
            "variance": series.var(ddof=1),
            "lag1_autocorrelation": series.autocorr(lag=1),
        }
    return pd.DataFrame(rows).T


def observed_sediment_summary(monthly_data: StationData) -> Dict[str, Any]:
    """Calculate observed sediment mass summaries for both stations.

    Inputs:
        monthly_data (StationData): Monthly Q and C data.

    Outputs:
        dict: Sediment mass and yield summaries by station plus contribution ratios.
    """

    station_results = {}
    for station in monthly_data:
        aligned = align_station_q_c(monthly_data, station)
        mass = concentration_gL_times_discharge_m3s_to_kg_s(aligned["C"], aligned["Q"])
        station_results[station] = {"aligned": aligned, "mass_kg_s": mass, "yields": compute_sediment_yields(mass)}

    common = pd.concat(
        {
            "Gisingen": station_results["Gisingen"]["mass_kg_s"],
            "Diepoldsau": station_results["Diepoldsau"]["mass_kg_s"],
        },
        axis=1,
    ).dropna()
    if common.empty:
        contribution = {
            "overlap_months": 0,
            "mean_ratio_percent": np.nan,
            "note": "No overlapping monthly Q-C mass records between stations.",
        }
    else:
        ratio = 100.0 * common["Gisingen"] / common["Diepoldsau"]
        contribution = {
            "overlap_months": int(common.shape[0]),
            "mean_ratio_percent": float(ratio.mean()),
            "median_ratio_percent": float(ratio.median()),
            "note": "Ratio is Ill/Gisingen mass divided by downstream Rhein/Diepoldsau mass for overlapping months.",
        }
    return {"stations": station_results, "observed_contribution": contribution}


def run_sediment_influence_analysis(
    monthly_data: StationData,
    review_results: Dict[str, Dict[str, Any]],
    evaluation_results: Dict[str, Dict[str, Any]],
    periods: int = 120,
    n_paths: int = 10,
    seed: int = 42,
) -> Dict[str, Any]:
    """Run Section 4 synthetic simulation and sediment influence analysis.

    Inputs:
        monthly_data (StationData): Monthly physical Q and C data.
        review_results (dict): Section 1 trend/normalization results.
        evaluation_results (dict): Section 3 fitted model results.
        periods (int): Number of monthly future values to simulate.
        n_paths (int): Number of synthetic paths.
        seed (int): Random seed.

    Outputs:
        dict: Observed yields, synthetic normalized paths, restored physical paths,
        synthetic sediment yields, and contribution summaries.
    """

    observed = observed_sediment_summary(monthly_data)
    synthetic: Dict[str, Any] = {}
    max_last_date = max(result["original"].index.max() for result in review_results.values())
    future_index = pd.date_range(max_last_date + pd.offsets.MonthBegin(1), periods=periods, freq="MS")

    for i, (label, evaluation) in enumerate(evaluation_results.items()):
        fit_result = evaluation["chosen"]["fit"]
        paths = simulate_normalized_paths(fit_result, periods=periods, n_paths=n_paths, seed=seed + i)
        paths.index = future_index
        restored = restore_physical_scale(
            paths,
            review_results[label],
            start_index=len(review_results[label]["original"]),
            future_index=future_index,
        )
        synthetic[label] = {
            "normalized": paths,
            "physical": restored["physical"],
            "clipped_count": restored["clipped_count"],
            "restore_note": restored["note"],
            "statistics": compare_synthetic_statistics(
                review_results[label]["normalized"],
                paths,
            ),
        }

    synthetic_mass = {}
    synthetic_contribution_rows = []
    for station in ("Gisingen", "Diepoldsau"):
        q_label = f"{station}_Q"
        c_label = f"{station}_C"
        if q_label not in synthetic or c_label not in synthetic:
            continue
        path_yields = {}
        for path_name in synthetic[q_label]["physical"].columns:
            mass = concentration_gL_times_discharge_m3s_to_kg_s(
                synthetic[c_label]["physical"][path_name],
                synthetic[q_label]["physical"][path_name],
            )
            path_yields[path_name] = compute_sediment_yields(mass)
        synthetic_mass[station] = path_yields

    if "Gisingen" in synthetic_mass and "Diepoldsau" in synthetic_mass:
        for path_name in synthetic_mass["Gisingen"]:
            ill_mean = synthetic_mass["Gisingen"][path_name]["overall_mean_kg_s"]
            rhein_mean = synthetic_mass["Diepoldsau"][path_name]["overall_mean_kg_s"]
            ratio = np.nan if rhein_mean == 0 else 100.0 * ill_mean / rhein_mean
            synthetic_contribution_rows.append(
                {"path": path_name, "ill_to_rhein_mean_mass_percent": ratio}
            )
    synthetic_contribution = pd.DataFrame(synthetic_contribution_rows)

    return {
        "future_index": future_index,
        "observed": observed,
        "synthetic": synthetic,
        "synthetic_mass": synthetic_mass,
        "synthetic_contribution": synthetic_contribution,
    }


def format_sediment_influence(results: Dict[str, Any]) -> str:
    """Format Section 4 results for notebook printing.

    Inputs:
        results (dict): Output from run_sediment_influence_analysis.

    Outputs:
        str: Human-readable sediment mass and contribution summary.
    """

    lines = ["Observed sediment mass summaries"]
    for station, station_result in results["observed"]["stations"].items():
        yields = station_result["yields"]
        lines.append(
            f"  {station}: mean mass rate={yields['overall_mean_kg_s']:.4g} kg/s; "
            f"mean monthly mass={yields['overall_mean_tonnes_per_month']:.4g} tonnes/month"
        )
    contribution = results["observed"]["observed_contribution"]
    lines.append("Observed Ill-to-Rhein contribution")
    lines.append(f"  overlap months: {contribution['overlap_months']}")
    lines.append(f"  mean ratio: {contribution['mean_ratio_percent']:.4g}%")
    lines.append(f"  note: {contribution['note']}")

    lines.append("Synthetic path contribution")
    synthetic_contribution = results["synthetic_contribution"]
    if synthetic_contribution.empty:
        lines.append("  Synthetic contribution could not be calculated.")
    else:
        lines.append(
            f"  mean across paths: {synthetic_contribution['ill_to_rhein_mean_mass_percent'].mean():.4g}%"
        )
        lines.append(
            f"  range across paths: {synthetic_contribution['ill_to_rhein_mean_mass_percent'].min():.4g}% "
            f"to {synthetic_contribution['ill_to_rhein_mean_mass_percent'].max():.4g}%"
        )
    for label, synthetic in results["synthetic"].items():
        lines.append(
            f"  {label}: clipped {synthetic['clipped_count']} negative restored values to zero; "
            f"{synthetic['restore_note']}"
        )
    return "\n".join(lines)

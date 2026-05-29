"""Section 4: sediment mass and synthetic series analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.arima_process import ArmaProcess

from .data_loading import StationData, align_station_q_c


def mass_rate(conc_gL: pd.Series, q_m3s: pd.Series) -> pd.Series:
    """Calculate sediment mass rate from concentration and discharge.

    Inputs:
        conc_gL (pd.Series): Suspended sediment concentration in g/L.
        q_m3s (pd.Series): Discharge in m3/s.
    Outputs:
        pd.Series: Sediment mass rate in kg/s.
    """

    df = pd.concat({"C": conc_gL, "Q": q_m3s}, axis=1).dropna()
    mass = df["C"] * df["Q"]
    mass.name = "sediment_mass_kg_s"
    return mass


def concentration_gL_times_discharge_m3s_to_kg_s(
    concentration_gL: pd.Series, discharge_m3s: pd.Series
) -> pd.Series:
    """Convert C and Q to sediment mass rate.

    Inputs:
        concentration_gL (pd.Series): Suspended sediment concentration in g/L.
        discharge_m3s (pd.Series): Discharge in m3/s.
    Outputs:
        pd.Series: Sediment mass rate in kg/s.
    """

    return mass_rate(concentration_gL, discharge_m3s)


def sediment_yields(mass: pd.Series) -> dict:
    """Calculate monthly and yearly sediment yield summaries.

    Inputs:
        mass (pd.Series): Sediment mass rate in kg/s, indexed by month.
    Outputs:
        dict: Monthly table, monthly climatology, yearly table, and mean values.
    """

    clean = mass.dropna().astype(float).sort_index()
    if clean.empty:
        raise ValueError("No valid mass data.")

    df = pd.DataFrame({"kg_s": clean})
    df["secs"] = df.index.days_in_month * 24 * 3600
    df["kg_mo"] = df["kg_s"] * df["secs"]
    df["tonne_mo"] = df["kg_mo"] / 1000.0
    df["m"] = df.index.month
    df["y"] = df.index.year

    monthly_avg = df.groupby("m")[["kg_s", "tonne_mo"]].mean()
    yearly_avg = df.groupby("y").agg(mean=("kg_s", "mean"), total=("tonne_mo", "sum"))

    return {
        "monthly": df,
        "by_month": monthly_avg,
        "by_year": yearly_avg,
        "mean_kg_s": float(df["kg_s"].mean()),
        "mean_tonne_mo": float(df["tonne_mo"].mean()),
    }


def _std(fit) -> float:
    """Estimate the innovation scale from model residuals.

    Inputs:
        fit: Fitted statsmodels ARIMA result object.
    Outputs:
        float: Sample standard deviation of finite residuals.
    """

    resid = np.asarray(fit.resid)
    resid = resid[np.isfinite(resid)]
    return float(np.std(resid, ddof=1)) if len(resid) >= 2 else 1.0


def simulate_paths(fit, n_months: int = 120, n_paths: int = 10, seed: int = 42) -> pd.DataFrame:
    """Generate normalized synthetic monthly paths from a fitted ARMA model.

    Inputs:
        fit: Fitted statsmodels ARIMA result object.
        n_months (int): Number of future months to simulate.
        n_paths (int): Number of synthetic paths to generate.
        seed (int): Random seed for reproducibility.
    Outputs:
        pd.DataFrame: Synthetic normalized paths, one column per path.
    """

    rng = np.random.default_rng(seed)
    ar = np.r_[1.0, -np.asarray(fit.arparams)]
    ma = np.r_[1.0, np.asarray(fit.maparams)]
    process = ArmaProcess(ar, ma)
    std = _std(fit)

    paths = {}
    for i in range(1, n_paths + 1):
        paths[f"p{i}"] = process.generate_sample(
            nsample=n_months,
            scale=std,
            burnin=200,
            distrvs=rng.normal,
        )
    return pd.DataFrame(paths)


def rescale(
    paths: pd.DataFrame,
    info: dict,
    start_idx: int,
    dates: pd.DatetimeIndex,
    floor: float = 0.0,
) -> dict:
    """Restore normalized synthetic paths to physical scale.

    Inputs:
        paths (pd.DataFrame): Normalized synthetic paths.
        info (dict): Section 1 result for the same series.
        start_idx (int): First future time index used for trend extrapolation.
        dates (pd.DatetimeIndex): Future monthly dates.
        floor (float): Lower bound used to avoid negative physical values.
    Outputs:
        dict: Physical-scale paths, number clipped to the floor, and a note.
    """

    paths = paths.copy()
    paths.index = dates
    x = np.arange(start_idx, start_idx + len(paths), dtype=float)

    if info["removed"] == "linear_trend":
        base = info["intercept"] + info["slope"] * x + info["offset"]
        note = "Trend extrapolated."
    else:
        base = np.full(len(paths), info["offset"], dtype=float)
        note = "Mean restored."

    restored = paths.add(base, axis=0)
    clipped = int((restored < floor).sum().sum())
    return {"physical": restored.clip(lower=floor), "clipped": clipped, "note": note}


def compare_stats(obs: pd.Series, synth: pd.DataFrame) -> pd.DataFrame:
    """Compare basic statistics of observed and synthetic series.

    Inputs:
        obs (pd.Series): Observed normalized monthly series.
        synth (pd.DataFrame): Synthetic normalized paths.
    Outputs:
        pd.DataFrame: Mean, standard deviation, variance, and lag-1 correlation.
    """

    observed = obs.dropna().astype(float)
    stats_dict = {
        "obs": {
            "mean": observed.mean(),
            "std": observed.std(ddof=1),
            "var": observed.var(ddof=1),
            "lag1": observed.autocorr(lag=1),
        }
    }
    for col in synth.columns:
        series = synth[col].dropna().astype(float)
        stats_dict[col] = {
            "mean": series.mean(),
            "std": series.std(ddof=1),
            "var": series.var(ddof=1),
            "lag1": series.autocorr(lag=1),
        }
    return pd.DataFrame(stats_dict).T


def observed_summary(data: StationData) -> dict:
    """Calculate observed sediment mass summaries for both stations.

    Inputs:
        data (StationData): Monthly Q and C data grouped by station.
    Outputs:
        dict: Observed station summaries and Ill/Rhein contribution ratio.
    """

    station_res = {}
    for station in data:
        aligned = align_station_q_c(data, station)
        mass = mass_rate(aligned["C"], aligned["Q"])
        station_res[station] = {"aligned": aligned, "mass": mass, "yields": sediment_yields(mass)}

    df_both = pd.concat(
        {"Gisingen": station_res["Gisingen"]["mass"], "Diepoldsau": station_res["Diepoldsau"]["mass"]},
        axis=1,
    ).dropna()

    if df_both.empty:
        ratio_info = {"months": 0, "mean_pct": np.nan, "median_pct": np.nan, "note": "No overlap."}
    else:
        ratio = 100.0 * df_both["Gisingen"] / df_both["Diepoldsau"]
        ratio_info = {
            "months": int(df_both.shape[0]),
            "mean_pct": float(ratio.mean()),
            "median_pct": float(ratio.median()),
            "note": "Ill/Gisingen divided by Rhein/Diepoldsau for overlapping months.",
        }

    return {"stations": station_res, "ratio": ratio_info}


def run_sediment_influence_analysis(
    monthly_data: StationData,
    review_results: dict,
    evaluation_results: dict,
    periods: int = 120,
    n_paths: int = 10,
    seed: int = 42,
) -> dict:
    """Run the Section 4 sediment influence analysis.

    Inputs:
        monthly_data (StationData): Monthly Q and C data grouped by station.
        review_results (dict): Section 1 results used to restore physical scale.
        evaluation_results (dict): Section 3 fitted model results.
        periods (int): Number of future months to simulate.
        n_paths (int): Number of synthetic paths for each series.
        seed (int): Random seed for reproducibility.
    Outputs:
        dict: Observed summaries, synthetic paths, mass summaries, and contribution table.
    """

    obs = observed_summary(monthly_data)
    synth = {}

    max_dt = max(result["original"].index.max() for result in review_results.values())
    future_dt = pd.date_range(max_dt + pd.offsets.MonthBegin(1), periods=periods, freq="MS")

    for i, (label, eval_result) in enumerate(evaluation_results.items()):
        fit = eval_result["chosen"]["fit"]
        paths = simulate_paths(fit, n_months=periods, n_paths=n_paths, seed=seed + i)
        paths.index = future_dt

        restored = rescale(
            paths,
            review_results[label],
            start_idx=len(review_results[label]["original"]),
            dates=future_dt,
        )
        synth[label] = {
            "norm": paths,
            "phys": restored["physical"],
            "clipped": restored["clipped"],
            "note": restored["note"],
            "stats": compare_stats(review_results[label]["normalized"], paths),
        }

    mass_dict = {}
    ratio_rows = []
    for station in ("Gisingen", "Diepoldsau"):
        q_label, c_label = f"{station}_Q", f"{station}_C"
        if q_label not in synth or c_label not in synth:
            continue

        path_yields = {}
        for path_name in synth[q_label]["phys"].columns:
            mass = mass_rate(synth[c_label]["phys"][path_name], synth[q_label]["phys"][path_name])
            path_yields[path_name] = sediment_yields(mass)
        mass_dict[station] = path_yields

    if "Gisingen" in mass_dict and "Diepoldsau" in mass_dict:
        for path_name in mass_dict["Gisingen"]:
            ill = mass_dict["Gisingen"][path_name]["mean_kg_s"]
            rhein = mass_dict["Diepoldsau"][path_name]["mean_kg_s"]
            pct = np.nan if rhein == 0 else 100.0 * ill / rhein
            ratio_rows.append({"path": path_name, "pct": pct})

    return {
        "dates": future_dt,
        "obs": obs,
        "synth": synth,
        "masses": mass_dict,
        "contrib": pd.DataFrame(ratio_rows),
    }


def format_sediment_influence(results: dict) -> str:
    """Format Section 4 results for printing.

    Inputs:
        results (dict): Results from run_sediment_influence_analysis.
    Outputs:
        str: Human-readable sediment mass and contribution summary.
    """

    lines = ["Sediment mass"]
    for station, result in results["obs"]["stations"].items():
        yields = result["yields"]
        lines.append(f"  {station}: {yields['mean_kg_s']:.4g} kg/s; {yields['mean_tonne_mo']:.4g} tonnes/mo")

    contribution = results["obs"]["ratio"]
    lines.extend(
        [
            "Contribution",
            f"  months: {contribution['months']}",
            f"  mean: {contribution['mean_pct']:.4g}%",
            f"  {contribution['note']}",
            "Synthetic",
        ]
    )

    synthetic_contribution = results["contrib"]
    if synthetic_contribution.empty:
        lines.append("  (none)")
    else:
        lines.append(f"  mean: {synthetic_contribution['pct'].mean():.4g}%")
        lines.append(f"  range: {synthetic_contribution['pct'].min():.4g}% to {synthetic_contribution['pct'].max():.4g}%")

    for label, result in results["synth"].items():
        lines.append(f"  {label}: {result['clipped']} clipped; {result['note']}")

    return "\n".join(lines)

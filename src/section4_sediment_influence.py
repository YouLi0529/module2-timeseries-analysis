"""Sediment analysis and synthetic generation."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from statsmodels.tsa.arima_process import ArmaProcess

from .data_loading import StationData, align_station_q_c


def mass_rate(conc_gL: pd.Series, q_m3s: pd.Series) -> pd.Series:
    df = pd.concat({"C": conc_gL, "Q": q_m3s}, axis=1).dropna()
    mass = df["C"] * df["Q"]
    mass.name = "sediment_mass_kg_s"
    return mass


def concentration_gL_times_discharge_m3s_to_kg_s(
    concentration_gL: pd.Series, discharge_m3s: pd.Series
) -> pd.Series:
    return mass_rate(concentration_gL, discharge_m3s)


def sediment_yields(mass: pd.Series) -> dict:
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
    resid = np.asarray(fit.resid)
    r = resid[np.isfinite(resid)]
    return float(np.std(r, ddof=1)) if len(r) >= 2 else 1.0


def simulate_paths(fit, n_months=120, n_paths=10, seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ar = np.r_[1.0, -np.asarray(fit.arparams)]
    ma = np.r_[1.0, np.asarray(fit.maparams)]
    proc = ArmaProcess(ar, ma)
    std = _std(fit)

    out = {}
    for i in range(1, n_paths + 1):
        out[f"p{i}"] = proc.generate_sample(
            nsample=n_months, scale=std, burnin=200, distrvs=rng.normal
        )
    return pd.DataFrame(out)


def rescale(paths: pd.DataFrame, info: dict, start_idx: int, dates: pd.DatetimeIndex, floor=0.0) -> dict:
    paths = paths.copy()
    paths.index = dates
    x = np.arange(start_idx, start_idx + len(paths), dtype=float)

    if info["removed"] == "linear_trend":
        base = info["intercept"] + info["slope"] * x + info["offset"]
        note = "Trend extrapolated."
    else:
        base = np.full(len(paths), info["offset"], dtype=float)
        note = "Mean restored."

    res = paths.add(base, axis=0)
    n_clipped = int((res < floor).sum().sum())
    return {"physical": res.clip(lower=floor), "clipped": n_clipped, "note": note}


def compare_stats(obs: pd.Series, synth: pd.DataFrame) -> pd.DataFrame:
    o = obs.dropna().astype(float)
    stats_dict = {
        "obs": {
            "mean": o.mean(),
            "std": o.std(ddof=1),
            "var": o.var(ddof=1),
            "lag1": o.autocorr(lag=1),
        }
    }
    for col in synth.columns:
        s = synth[col].dropna().astype(float)
        stats_dict[col] = {
            "mean": s.mean(), 
            "std": s.std(ddof=1), 
            "var": s.var(ddof=1), 
            "lag1": s.autocorr(lag=1)
        }
    return pd.DataFrame(stats_dict).T


def observed_summary(data: StationData) -> dict:
    station_res = {}
    for st in data:
        aligned = align_station_q_c(data, st)
        mass = mass_rate(aligned["C"], aligned["Q"])
        station_res[st] = {"aligned": aligned, "mass": mass, "yields": sediment_yields(mass)}

    df_both = pd.concat(
        {"Gisingen": station_res["Gisingen"]["mass"], "Diepoldsau": station_res["Diepoldsau"]["mass"]}, 
        axis=1
    ).dropna()
    
    if df_both.empty:
        ratio_info = {"months": 0, "mean_pct": np.nan, "note": "No overlap."}
    else:
        r = 100.0 * df_both["Gisingen"] / df_both["Diepoldsau"]
        ratio_info = {
            "months": int(df_both.shape[0]), 
            "mean_pct": float(r.mean()), 
            "median_pct": float(r.median()), 
            "note": "Ill/Gisingen ÷ Rhein."
        }
    
    if ratio_info["months"]:
        ratio_info["note"] = "Ill/Gisingen divided by Rhein/Diepoldsau for overlapping months."
    return {"stations": station_res, "ratio": ratio_info}


def run_sediment_influence_analysis(
    monthly_data: StationData, 
    review_results: dict, 
    evaluation_results: dict, 
    periods=120, 
    n_paths=10, 
    seed=42
) -> dict:
    obs = observed_summary(monthly_data)
    synth = {}
    
    max_dt = max(r["original"].index.max() for r in review_results.values())
    future_dt = pd.date_range(max_dt + pd.offsets.MonthBegin(1), periods=periods, freq="MS")

    for i, (lbl, eval_r) in enumerate(evaluation_results.items()):
        fit = eval_r["chosen"]["fit"]
        paths = simulate_paths(fit, n_months=periods, n_paths=n_paths, seed=seed + i)
        paths.index = future_dt
        
        r = rescale(paths, review_results[lbl], start_idx=len(review_results[lbl]["original"]), dates=future_dt)
        synth[lbl] = {
            "norm": paths,
            "phys": r["physical"],
            "clipped": r["clipped"],
            "note": r["note"],
            "stats": compare_stats(review_results[lbl]["normalized"], paths),
        }

    mass_dict = {}
    ratio_rows = []
    for st in ("Gisingen", "Diepoldsau"):
        q_lbl, c_lbl = f"{st}_Q", f"{st}_C"
        if q_lbl not in synth or c_lbl not in synth:
            continue
            
        py = {}
        for pname in synth[q_lbl]["phys"].columns:
            m = mass_rate(synth[c_lbl]["phys"][pname], synth[q_lbl]["phys"][pname])
            py[pname] = sediment_yields(m)
        mass_dict[st] = py

    if "Gisingen" in mass_dict and "Diepoldsau" in mass_dict:
        for pn in mass_dict["Gisingen"]:
            ill = mass_dict["Gisingen"][pn]["mean_kg_s"]
            rhein = mass_dict["Diepoldsau"][pn]["mean_kg_s"]
            pct = np.nan if rhein == 0 else 100.0 * ill / rhein
            ratio_rows.append({"path": pn, "pct": pct})
            
    return {
        "dates": future_dt, 
        "obs": obs, 
        "synth": synth, 
        "masses": mass_dict, 
        "contrib": pd.DataFrame(ratio_rows)
    }


def format_sediment_influence(results: dict) -> str:
    lines = ["Sediment mass"]
    for st, r in results["obs"]["stations"].items():
        y = r["yields"]
        lines.append(f"  {st}: {y['mean_kg_s']:.4g} kg/s; {y['mean_tonne_mo']:.4g} tonnes/mo")
    
    c = results["obs"]["ratio"]
    lines.extend([
        "Contribution",
        f"  months: {c['months']}",
        f"  mean: {c['mean_pct']:.4g}%",
        f"  {c['note']}",
        "Synthetic"
    ])
    
    cc = results["contrib"]
    if cc.empty:
        lines.append("  (none)")
    else:
        lines.append(f"  mean: {cc['pct'].mean():.4g}%")
        lines.append(f"  range: {cc['pct'].min():.4g}% to {cc['pct'].max():.4g}%")
    
    for lbl, s in results["synth"].items():
        lines.append(f"  {lbl}: {s['clipped']} clipped; {s['note']}")
    
    return "\n".join(lines)

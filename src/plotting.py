"""Plotting helpers for the Module 2 notebook."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from .data_loading import StationData


def _save(fig: plt.Figure, output_path: Path | None) -> plt.Figure:
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")
    return fig


def plot_monthly_timeseries(
    monthly_data: StationData,
    review_results: Dict[str, Dict[str, Any]],
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot monthly Q and C series for both stations with trend lines.

    Inputs:
        monthly_data (StationData): Monthly Q and C data by station.
        review_results (dict): Section 1 results containing fitted trend lines.
        output_path (Path | None): Optional path to save the figure.

    Outputs:
        plt.Figure: Matplotlib figure object.
    """

    fig, axes = plt.subplots(2, 2, figsize=(13, 7), sharex=False)
    variables = [("Q", "Discharge Q (m3/s)"), ("C", "SSC C (g/L)")]
    for row, station in enumerate(("Gisingen", "Diepoldsau")):
        for col, (variable, ylabel) in enumerate(variables):
            ax = axes[row, col]
            series = monthly_data[station][variable]
            label = f"{station}_{variable}"
            ax.plot(series.index, series.values, lw=1.2, label="monthly mean")
            trend = review_results[label]["trend"]["trend"]
            if review_results[label]["trend"]["significant"]:
                ax.plot(trend.index, trend.values, color="crimson", lw=1.4, label="significant trend")
            else:
                ax.plot(trend.index, trend.values, color="gray", lw=1.0, ls="--", label="linear fit")
            ax.set_title(f"{station} {variable}")
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.25)
            ax.legend(fontsize=8)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_acf_pacf_grid(
    order_results: Dict[str, Dict[str, Any]],
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot ACF and PACF for every normalized series.

    Inputs:
        order_results (dict): Section 2 ACF/PACF and order-selection results.
        output_path (Path | None): Optional path to save the figure.

    Outputs:
        plt.Figure: Matplotlib figure object.
    """

    labels = list(order_results)
    fig, axes = plt.subplots(len(labels), 2, figsize=(12, 2.7 * len(labels)), sharex=False)
    if len(labels) == 1:
        axes = np.array([axes])
    for row, label in enumerate(labels):
        acf_pacf = order_results[label]["acf_pacf"]
        for col, key in enumerate(("acf", "pacf")):
            ax = axes[row, col]
            lags = acf_pacf["lags"]
            values = acf_pacf[key]
            ax.stem(lags, values, basefmt=" ", linefmt="C0-", markerfmt="C0o")
            conf = acf_pacf["confidence"]
            ax.axhline(conf, color="crimson", ls="--", lw=1)
            ax.axhline(-conf, color="crimson", ls="--", lw=1)
            ax.axhline(0, color="black", lw=0.8)
            ax.set_title(f"{label} {key.upper()}")
            ax.set_xlabel("Lag (months)")
            ax.set_ylabel("Correlation")
            ax.grid(True, alpha=0.2)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_model_diagnostics(
    evaluation_results: Dict[str, Dict[str, Any]],
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot empirical/theoretical ACF, residual ACF, and residual QQ plots.

    Inputs:
        evaluation_results (dict): Section 3 model evaluation results.
        output_path (Path | None): Optional path to save the figure.

    Outputs:
        plt.Figure: Matplotlib figure object.
    """

    labels = list(evaluation_results)
    fig, axes = plt.subplots(len(labels), 3, figsize=(15, 2.9 * len(labels)))
    if len(labels) == 1:
        axes = np.array([axes])
    for row, label in enumerate(labels):
        chosen = evaluation_results[label]["chosen"]
        lags = chosen["lags"]
        conf = chosen["confidence"]

        ax = axes[row, 0]
        ax.plot(lags, chosen["empirical_acf"], marker="o", label="empirical")
        ax.plot(lags, chosen["theoretical_acf"], marker="s", label="theoretical")
        ax.axhline(conf, color="crimson", ls="--", lw=1)
        ax.axhline(-conf, color="crimson", ls="--", lw=1)
        ax.axhline(0, color="black", lw=0.8)
        ax.set_title(f"{label}: chosen {chosen['model_type']} ACF")
        ax.set_xlabel("Lag")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.2)

        ax = axes[row, 1]
        ax.stem(lags, chosen["residual_acf"], basefmt=" ", linefmt="C1-", markerfmt="C1o")
        ax.axhline(conf, color="crimson", ls="--", lw=1)
        ax.axhline(-conf, color="crimson", ls="--", lw=1)
        ax.axhline(0, color="black", lw=0.8)
        ax.set_title(f"{label}: residual ACF")
        ax.set_xlabel("Lag")
        ax.grid(True, alpha=0.2)

        ax = axes[row, 2]
        residuals = chosen["residuals"].dropna()
        (osm, osr), (slope, intercept, _) = stats.probplot(residuals, dist="norm")
        ax.scatter(osm, osr, s=18, alpha=0.75)
        ax.plot(osm, intercept + slope * osm, color="crimson", lw=1.2)
        ax.set_title(f"{label}: residual probability plot")
        ax.set_xlabel("Theoretical quantiles")
        ax.set_ylabel("Ordered residuals")
        ax.grid(True, alpha=0.2)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_synthetic_series(
    sediment_results: Dict[str, Any],
    review_results: Dict[str, Dict[str, Any]],
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot historical normalized data together with synthetic normalized paths.

    Inputs:
        sediment_results (dict): Section 4 output.
        review_results (dict): Section 1 output with historical normalized series.
        output_path (Path | None): Optional path to save the figure.

    Outputs:
        plt.Figure: Matplotlib figure object.
    """

    labels = list(sediment_results["synthetic"])
    fig, axes = plt.subplots(len(labels), 1, figsize=(12, 2.5 * len(labels)), sharex=False)
    if len(labels) == 1:
        axes = [axes]
    for ax, label in zip(axes, labels):
        historical = review_results[label]["normalization"]["series"]
        ax.plot(historical.index, historical.values, color="black", lw=1.0, label="historical normalized")
        synthetic = sediment_results["synthetic"][label]["normalized"]
        for column in synthetic.columns:
            ax.plot(synthetic.index, synthetic[column], lw=0.8, alpha=0.55)
        ax.set_title(f"{label}: historical normalized data and 10 synthetic paths")
        ax.axhline(0, color="gray", lw=0.8)
        ax.grid(True, alpha=0.2)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_sediment_yields(
    sediment_results: Dict[str, Any],
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot observed monthly climatology and synthetic contribution summaries.

    Inputs:
        sediment_results (dict): Section 4 sediment influence output.
        output_path (Path | None): Optional path to save the figure.

    Outputs:
        plt.Figure: Matplotlib figure object.
    """

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for station, result in sediment_results["observed"]["stations"].items():
        climatology = result["yields"]["monthly_climatology"]
        axes[0].plot(climatology.index, climatology["mass_kg_s"], marker="o", label=station)
    axes[0].set_title("Observed monthly sediment mass-rate climatology")
    axes[0].set_xlabel("Calendar month")
    axes[0].set_ylabel("Mean mass rate (kg/s)")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend()

    synthetic_contribution = sediment_results["synthetic_contribution"]
    if not synthetic_contribution.empty:
        axes[1].bar(
            synthetic_contribution["path"],
            synthetic_contribution["ill_to_rhein_mean_mass_percent"],
            color="steelblue",
        )
    axes[1].set_title("Synthetic Ill contribution by path")
    axes[1].set_ylabel("Ill / Rhein mass rate (%)")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    return _save(fig, output_path)


def plot_dependency_scatter(
    dependency_results: Dict[str, Dict[str, Any]],
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot Q-C joint distributions for each station.

    Inputs:
        dependency_results (dict): Section 5 dependency analysis output.
        output_path (Path | None): Optional path to save the figure.

    Outputs:
        plt.Figure: Matplotlib figure object.
    """

    stations = list(dependency_results)
    fig, axes = plt.subplots(1, len(stations), figsize=(6 * len(stations), 4.5))
    if len(stations) == 1:
        axes = [axes]
    for ax, station in zip(axes, stations):
        frame = dependency_results[station]["aligned_data"]
        ax.scatter(frame["Q"], frame["C"], s=22, alpha=0.7)
        ax.set_title(f"{station}: Q-C joint distribution")
        ax.set_xlabel("Q (m3/s)")
        ax.set_ylabel("C (g/L)")
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return _save(fig, output_path)


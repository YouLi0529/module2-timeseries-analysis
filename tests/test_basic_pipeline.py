"""Basic tests for reproducibility and core calculations."""

from __future__ import annotations

import importlib
from pathlib import Path

import pandas as pd
import pytest

from src.data_loading import (
    DataNotFoundError,
    aggregate_monthly_mean,
    load_project_raw_data,
)
from src.section4_sediment_influence import (
    concentration_gL_times_discharge_m3s_to_kg_s,
)


def test_missing_data_error_is_clear(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    with pytest.raises(DataNotFoundError, match="Expected raw data"):
        load_project_raw_data(raw_dir)


def test_monthly_aggregation_on_artificial_data() -> None:
    index = pd.to_datetime(
        [
            "2020-01-01 00:00",
            "2020-01-15 00:00",
            "2020-02-01 00:00",
            "2020-02-15 00:00",
        ]
    )
    series = pd.Series([1.0, 3.0, 10.0, 14.0], index=index)
    monthly = aggregate_monthly_mean(series)
    assert monthly.loc[pd.Timestamp("2020-01-01")] == pytest.approx(2.0)
    assert monthly.loc[pd.Timestamp("2020-02-01")] == pytest.approx(12.0)


def test_sediment_mass_unit_conversion() -> None:
    concentration = pd.Series([1.0, 0.5], index=pd.to_datetime(["2020-01-01", "2020-02-01"]))
    discharge = pd.Series([2.0, 10.0], index=pd.to_datetime(["2020-01-01", "2020-02-01"]))
    mass = concentration_gL_times_discharge_m3s_to_kg_s(concentration, discharge)
    assert mass.iloc[0] == pytest.approx(2.0)
    assert mass.iloc[1] == pytest.approx(5.0)


def test_main_source_files_import() -> None:
    modules = [
        "src.data_loading",
        "src.section1_timeseries_review",
        "src.section2_timeseries_modelling",
        "src.section3_model_evaluation",
        "src.section4_sediment_influence",
        "src.section5_dependency_analysis",
        "src.plotting",
    ]
    for module_name in modules:
        importlib.import_module(module_name)


def test_notebook_is_present() -> None:
    notebook = Path(__file__).resolve().parents[1] / "notebooks" / "Module2_Timeseries_Analysis.ipynb"
    assert notebook.exists()


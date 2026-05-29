"""Project-specific data loading and monthly aggregation for Module 2."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Mapping

import pandas as pd


StationData = Dict[str, Dict[str, pd.Series]]

TIMESTAMP_COLUMN = "timestamp"

RAW_SERIES = {
    "Gisingen": {
        "Q": {"filename": "Q_Gisingen_1976-2023.csv", "value_column": "q_m3s"},
        "C": {"filename": "SSC_Gisingen_2003-2020.csv", "value_column": "ssc_gL"},
    },
    "Diepoldsau": {
        "Q": {"filename": "Q_Diepoldsau_m3s.csv", "value_column": "q_m3s"},
        "C": {"filename": "SSC_Diepoldsau_gL.csv", "value_column": "ssc_gL"},
    },
}


class DataNotFoundError(FileNotFoundError):
    """Raised when one or more required raw CSV files are missing."""


def expected_data_message() -> str:
    """Describe the raw CSV files expected by this project.

    Inputs:
        None.

    Outputs:
        str: Human-readable description of required filenames and columns.
    """

    return (
        "Expected raw data in data/raw/ as four CSV files:\n"
        "  - Q_Gisingen_1976-2023.csv with columns timestamp, q_m3s\n"
        "  - SSC_Gisingen_2003-2020.csv with columns timestamp, ssc_gL\n"
        "  - Q_Diepoldsau_m3s.csv with columns timestamp, q_m3s\n"
        "  - SSC_Diepoldsau_gL.csv with columns timestamp, ssc_gL"
    )


def ensure_project_directories(project_root: Path) -> None:
    """Create the data and output folders used by the project.

    Inputs:
        project_root (Path): Repository root directory.

    Outputs:
        None: Missing folders are created on disk.
    """

    for relative_path in (
        "data/raw",
        "data/processed",
        "outputs/figures",
        "outputs/tables",
        "outputs/reports",
    ):
        (project_root / relative_path).mkdir(parents=True, exist_ok=True)


def read_required_csv(path: Path, value_column: str) -> pd.Series:
    """Read one required timestamp-value CSV file as a clean timeseries.

    Inputs:
        path (Path): CSV file path.
        value_column (str): Name of the numeric data column to read.

    Outputs:
        pd.Series: Numeric values indexed by cleaned and sorted timestamps.
    """

    path = Path(path)
    if not path.exists():
        raise DataNotFoundError(f"Missing raw data file: {path}\n{expected_data_message()}")

    frame = pd.read_csv(path)
    required_columns = {TIMESTAMP_COLUMN, value_column}
    missing_columns = required_columns.difference(frame.columns)
    if missing_columns:
        raise ValueError(
            f"{path.name} is missing required columns: {sorted(missing_columns)}. "
            f"Found columns: {list(frame.columns)}"
        )

    timestamps = pd.to_datetime(frame[TIMESTAMP_COLUMN], errors="coerce")
    values = pd.to_numeric(frame[value_column], errors="coerce")
    series = pd.Series(values.to_numpy(), index=timestamps, name=value_column)

    series = series[series.index.notna()]
    series = series.dropna()
    series = series.sort_index()
    series = series[~series.index.duplicated(keep="first")]

    if series.empty:
        raise ValueError(f"{path.name} has no valid timestamp/value rows after cleaning.")
    return series


def load_project_raw_data(data_dir: Path) -> StationData:
    """Load the four raw CSV timeseries required for the assignment.

    Inputs:
        data_dir (Path): Folder containing the four raw CSV files.

    Outputs:
        StationData: Nested dictionary such as data["Gisingen"]["Q"] = pd.Series.
    """

    data_dir = Path(data_dir)
    if not data_dir.exists():
        raise DataNotFoundError(f"{data_dir} does not exist.\n{expected_data_message()}")

    missing_files = []
    raw_data: StationData = {}

    for station, variables in RAW_SERIES.items():
        raw_data[station] = {}
        for variable, spec in variables.items():
            path = data_dir / spec["filename"]
            if not path.exists():
                missing_files.append(spec["filename"])
                continue
            raw_data[station][variable] = read_required_csv(path, spec["value_column"])

    if missing_files:
        raise DataNotFoundError(
            "Missing required raw CSV files:\n"
            + "\n".join(f"  - {filename}" for filename in missing_files)
            + "\n"
            + expected_data_message()
        )

    return raw_data


def aggregate_monthly_mean(series: pd.Series) -> pd.Series:
    """Aggregate a timestamp-indexed timeseries to monthly mean values.

    Inputs:
        series (pd.Series): Numeric timeseries with a pandas DatetimeIndex.

    Outputs:
        pd.Series: Monthly mean values indexed by month-start timestamps.
    """

    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError("Monthly aggregation requires a pandas DatetimeIndex.")
    monthly = series.sort_index().resample("MS").mean().dropna()
    monthly.name = series.name
    return monthly


def aggregate_project_monthly(raw_data: StationData) -> StationData:
    """Aggregate every raw project series to monthly means.

    Inputs:
        raw_data (StationData): Nested dictionary of raw Q and C timeseries.

    Outputs:
        StationData: Same nested structure, but each series is monthly mean data.
    """

    monthly_data: StationData = {}
    for station, variables in raw_data.items():
        monthly_data[station] = {}
        for variable, series in variables.items():
            monthly_data[station][variable] = aggregate_monthly_mean(series)
    return monthly_data


def load_project_monthly_data(data_dir: Path) -> StationData:
    """Load raw project CSV files and aggregate them to monthly means.

    Inputs:
        data_dir (Path): Folder containing the four required raw CSV files.

    Outputs:
        StationData: Monthly mean Q and C series by station.
    """

    raw_data = load_project_raw_data(data_dir)
    return aggregate_project_monthly(raw_data)


def flatten_station_data(data: StationData) -> Dict[str, pd.Series]:
    """Convert nested station data into labels like 'Gisingen_Q'.

    Inputs:
        data (StationData): Nested dictionary by station and variable.

    Outputs:
        dict[str, pd.Series]: Flat dictionary keyed by station-variable labels.
    """

    flat_data: Dict[str, pd.Series] = {}
    for station, variables in data.items():
        for variable, series in variables.items():
            flat_data[f"{station}_{variable}"] = series
    return flat_data


def align_station_q_c(monthly_data: StationData, station: str) -> pd.DataFrame:
    """Align monthly Q and C values for one station.

    Inputs:
        monthly_data (StationData): Monthly Q and C data by station.
        station (str): Station name, for example "Gisingen" or "Diepoldsau".

    Outputs:
        pd.DataFrame: Rows where both Q and C exist, with columns Q and C.
    """

    if station not in monthly_data:
        raise KeyError(f"Station {station!r} not found in monthly data.")

    station_data = monthly_data[station]
    if "Q" not in station_data or "C" not in station_data:
        raise KeyError(f"Station {station!r} must contain both Q and C series.")

    aligned = pd.concat({"Q": station_data["Q"], "C": station_data["C"]}, axis=1).dropna()
    aligned.index.name = "datetime"
    return aligned


def save_monthly_tables(monthly_data: StationData, output_dir: Path) -> Mapping[str, Path]:
    """Save monthly mean series as CSV tables.

    Inputs:
        monthly_data (StationData): Monthly Q and C data by station.
        output_dir (Path): Folder where processed CSV files should be written.

    Outputs:
        Mapping[str, Path]: Written CSV paths keyed by labels like "Gisingen_Q".
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written_files: dict[str, Path] = {}
    for station, variables in monthly_data.items():
        for variable, series in variables.items():
            label = f"{station}_{variable}"
            path = output_dir / f"monthly_{label}.csv"
            series.rename(variable).to_csv(path, index_label="datetime")
            written_files[label] = path
    return written_files


"""Project-specific data loading and monthly aggregation for Module 2."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


StationData = dict[str, dict[str, pd.Series]]

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
    """Used when a required raw data file cannot be found."""


def expected_data_message() -> str:
    """Return the filenames and columns expected in data/raw."""

    return (
        "Expected raw data in data/raw/ as four CSV files:\n"
        "  - Q_Gisingen_1976-2023.csv with columns timestamp, q_m3s\n"
        "  - SSC_Gisingen_2003-2020.csv with columns timestamp, ssc_gL\n"
        "  - Q_Diepoldsau_m3s.csv with columns timestamp, q_m3s\n"
        "  - SSC_Diepoldsau_gL.csv with columns timestamp, ssc_gL"
    )


def ensure_project_directories(project_root: Path) -> None:
    """Create the folders used by the project."""

    for relative_path in (
        "data/raw",
        "data/processed",
        "outputs/figures",
        "outputs/tables",
        "outputs/reports",
    ):
        (project_root / relative_path).mkdir(parents=True, exist_ok=True)


def read_required_csv(path: Path, value_column: str) -> pd.Series:
    """Read one CSV file and return a timestamp-indexed series."""

    path = Path(path)
    if not path.exists():
        raise DataNotFoundError(f"Missing raw data file: {path}\n{expected_data_message()}")

    required_columns = {TIMESTAMP_COLUMN, value_column}
    frame = pd.read_csv(path)
    missing_columns = required_columns.difference(frame.columns)
    if missing_columns:
        raise ValueError(
            f"{path.name} is missing required columns: {sorted(missing_columns)}. "
            f"Found columns: {list(frame.columns)}"
        )

    frame = frame[[TIMESTAMP_COLUMN, value_column]].copy()
    frame[TIMESTAMP_COLUMN] = pd.to_datetime(frame[TIMESTAMP_COLUMN], errors="coerce")
    frame[value_column] = pd.to_numeric(frame[value_column], errors="coerce")
    frame = frame.dropna().sort_values(TIMESTAMP_COLUMN).drop_duplicates(TIMESTAMP_COLUMN)

    if frame.empty:
        raise ValueError(f"{path.name} has no valid timestamp/value rows after cleaning.")

    return frame.set_index(TIMESTAMP_COLUMN)[value_column].rename(value_column)


def load_project_raw_data(data_dir: Path) -> StationData:
    """Load the four raw CSV files used in this assignment."""

    data_dir = Path(data_dir)

    raw_data: StationData = {}
    for station, variables in RAW_SERIES.items():
        raw_data[station] = {}
        for variable, spec in variables.items():
            path = data_dir / spec["filename"]
            raw_data[station][variable] = read_required_csv(path, spec["value_column"])
    return raw_data


def aggregate_monthly_mean(series: pd.Series) -> pd.Series:
    """Aggregate a timestamp-indexed series to monthly means."""

    monthly = series.dropna().sort_index().resample("MS").mean().dropna()
    monthly.name = series.name
    return monthly


def aggregate_project_monthly(raw_data: StationData) -> StationData:
    """Aggregate every raw project series to monthly means."""

    monthly_data: StationData = {}
    for station, variables in raw_data.items():
        monthly_data[station] = {}
        for variable, series in variables.items():
            monthly_data[station][variable] = aggregate_monthly_mean(series)
    return monthly_data


def load_project_monthly_data(data_dir: Path) -> StationData:
    """Load raw CSV files and return monthly mean Q and C series."""

    raw_data = load_project_raw_data(data_dir)
    return aggregate_project_monthly(raw_data)


def flatten_station_data(data: StationData) -> dict[str, pd.Series]:
    """Convert nested station data into labels like Gisingen_Q."""

    flat_data: dict[str, pd.Series] = {}
    for station, variables in data.items():
        for variable, series in variables.items():
            flat_data[f"{station}_{variable}"] = series
    return flat_data


def align_station_q_c(monthly_data: StationData, station: str) -> pd.DataFrame:
    """Align monthly Q and C values for one station."""

    station_data = monthly_data[station]
    aligned = pd.concat({"Q": station_data["Q"], "C": station_data["C"]}, axis=1).dropna()
    aligned.index.name = "datetime"
    return aligned


def save_monthly_tables(monthly_data: StationData, output_dir: Path) -> dict[str, Path]:
    """Save monthly mean series as CSV tables."""

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

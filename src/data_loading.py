"""Data loading and monthly aggregation utilities for Module 2."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping

import pandas as pd


StationData = Dict[str, Dict[str, pd.Series]]


class DataNotFoundError(FileNotFoundError):
    """Raised when the expected raw data files cannot be found."""


@dataclass(frozen=True)
class SeriesSpec:
    """Expected metadata for one project timeseries."""

    station: str
    variable: str
    filename_keywords: tuple[str, ...]
    preferred_value_columns: tuple[str, ...]


SERIES_SPECS: tuple[SeriesSpec, ...] = (
    SeriesSpec(
        station="Gisingen",
        variable="Q",
        filename_keywords=("q", "gisingen"),
        preferred_value_columns=("q_m3s", "q", "discharge", "flow"),
    ),
    SeriesSpec(
        station="Gisingen",
        variable="C",
        filename_keywords=("ssc", "gisingen"),
        preferred_value_columns=("ssc_gL", "ssc_gl", "c_gL", "c_gl", "c", "concentration"),
    ),
    SeriesSpec(
        station="Diepoldsau",
        variable="Q",
        filename_keywords=("q", "diepoldsau"),
        preferred_value_columns=("q_m3s", "q", "discharge", "flow"),
    ),
    SeriesSpec(
        station="Diepoldsau",
        variable="C",
        filename_keywords=("ssc", "diepoldsau"),
        preferred_value_columns=("ssc_gL", "ssc_gl", "c_gL", "c_gl", "c", "concentration"),
    ),
)


def expected_data_message() -> str:
    """Return a beginner-friendly description of the expected raw data.

    Inputs:
        None.

    Outputs:
        str: Description of accepted files, column names, and example layout.
    """

    return (
        "Expected raw data in data/raw/ as CSV or Excel files. The repository "
        "can read the provided four-file layout:\n"
        "  - Q_Gisingen_*.csv with columns timestamp, q_m3s\n"
        "  - SSC_Gisingen_*.csv with columns timestamp, ssc_gL\n"
        "  - Q_Diepoldsau_*.csv with columns timestamp, q_m3s\n"
        "  - SSC_Diepoldsau_*.csv with columns timestamp, ssc_gL\n"
        "It also accepts similar column names such as datetime, Q, C, discharge, "
        "or concentration. A combined long-format file should contain columns "
        "like datetime, station, variable, and value."
    )


def ensure_project_directories(project_root: Path) -> None:
    """Create output and data directories used by the project.

    Inputs:
        project_root (Path): Repository root directory.

    Outputs:
        None: Directories are created on disk if missing.
    """

    for relative in (
        "data/raw",
        "data/processed",
        "outputs/figures",
        "outputs/tables",
        "outputs/reports",
    ):
        (project_root / relative).mkdir(parents=True, exist_ok=True)


def list_supported_data_files(data_dir: Path) -> list[Path]:
    """List supported raw data files in a directory.

    Inputs:
        data_dir (Path): Directory containing raw CSV or Excel files.

    Outputs:
        list[Path]: Sorted paths ending in .csv, .xlsx, or .xls.
    """

    data_dir = Path(data_dir)
    if not data_dir.exists():
        raise DataNotFoundError(f"{data_dir} does not exist. {expected_data_message()}")
    suffixes = {".csv", ".xlsx", ".xls"}
    return sorted(path for path in data_dir.iterdir() if path.is_file() and path.suffix.lower() in suffixes)


def _normalise_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("/", "_")


def _find_datetime_column(columns: Iterable[str]) -> str | None:
    preferred = ("timestamp", "datetime", "date_time", "date", "time")
    normalised = {_normalise_name(col): col for col in columns}
    for name in preferred:
        if name in normalised:
            return normalised[name]
    return None


def _find_value_column(columns: Iterable[str], preferred: Iterable[str]) -> str | None:
    normalised = {_normalise_name(col): col for col in columns}
    for name in preferred:
        key = _normalise_name(name)
        if key in normalised:
            return normalised[key]
    return None


def read_timeseries_file(
    path: Path,
    preferred_value_columns: Iterable[str] | None = None,
    datetime_column: str | None = None,
) -> pd.Series:
    """Read one timestamp-value timeseries from CSV or Excel.

    Inputs:
        path (Path): CSV, XLSX, or XLS file to read.
        preferred_value_columns (Iterable[str] | None): Candidate names for the
            numerical value column, for example ["q_m3s", "Q"].
        datetime_column (str | None): Optional explicit datetime column name.

    Outputs:
        pd.Series: Numeric values indexed by a sorted DatetimeIndex.
    """

    path = Path(path)
    if not path.exists():
        raise DataNotFoundError(f"Raw data file not found: {path}. {expected_data_message()}")

    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        frame = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported data file type for {path}. Use CSV, XLSX, or XLS.")

    if frame.empty:
        raise ValueError(f"{path} is empty.")

    datetime_col = datetime_column or _find_datetime_column(frame.columns)
    if datetime_col is None:
        raise ValueError(
            f"Could not find a datetime column in {path}. Expected one of "
            "timestamp, datetime, date, or time."
        )

    preferred_value_columns = tuple(preferred_value_columns or ())
    value_col = _find_value_column(frame.columns, preferred_value_columns)
    if value_col is None:
        numeric_candidates = [
            col
            for col in frame.columns
            if col != datetime_col and pd.api.types.is_numeric_dtype(frame[col])
        ]
        if not numeric_candidates:
            for col in frame.columns:
                if col == datetime_col:
                    continue
                converted = pd.to_numeric(frame[col], errors="coerce")
                if converted.notna().any():
                    numeric_candidates.append(col)
        if not numeric_candidates:
            raise ValueError(
                f"Could not find a numeric value column in {path}. "
                f"Tried preferred names: {preferred_value_columns}."
            )
        value_col = numeric_candidates[0]

    timestamps = pd.to_datetime(frame[datetime_col], errors="coerce")
    values = pd.to_numeric(frame[value_col], errors="coerce")
    series = pd.Series(values.to_numpy(), index=timestamps, name=value_col)
    series = series[series.index.notna()].sort_index()
    series = series[~series.index.duplicated(keep="first")]
    series = series.dropna()

    if series.empty:
        raise ValueError(f"No valid timestamp/value rows could be read from {path}.")
    return series


def _find_file_for_spec(files: Iterable[Path], spec: SeriesSpec) -> Path | None:
    for path in files:
        lowered = path.name.lower()
        if all(keyword in lowered for keyword in spec.filename_keywords):
            return path
    return None


def _try_load_combined_long_file(files: Iterable[Path]) -> StationData | None:
    """Try to load a single long-format file if the four-file layout is absent."""

    required = {"station", "variable"}
    for path in files:
        try:
            frame = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
        except Exception:
            continue
        normalised = {_normalise_name(col): col for col in frame.columns}
        datetime_col = _find_datetime_column(frame.columns)
        value_col = _find_value_column(frame.columns, ("value", "q", "c", "q_m3s", "ssc_gL"))
        if datetime_col is None or value_col is None or not required.issubset(normalised):
            continue

        frame = frame.copy()
        frame[datetime_col] = pd.to_datetime(frame[datetime_col], errors="coerce")
        frame[value_col] = pd.to_numeric(frame[value_col], errors="coerce")
        frame = frame.dropna(subset=[datetime_col, value_col])

        station_col = normalised["station"]
        variable_col = normalised["variable"]
        output: StationData = {"Gisingen": {}, "Diepoldsau": {}}
        for station in output:
            for variable in ("Q", "C"):
                mask = (
                    frame[station_col].astype(str).str.lower().str.contains(station.lower())
                    & frame[variable_col].astype(str).str.upper().str.startswith(variable)
                )
                subset = frame.loc[mask, [datetime_col, value_col]]
                if subset.empty:
                    break
                series = pd.Series(
                    subset[value_col].to_numpy(),
                    index=pd.DatetimeIndex(subset[datetime_col]),
                    name=f"{station}_{variable}",
                ).sort_index()
                output[station][variable] = series.dropna()
        if all(variable in output[station] for station in output for variable in ("Q", "C")):
            return output
    return None


def load_project_raw_data(data_dir: Path) -> StationData:
    """Load all project raw timeseries into a nested station/variable dictionary.

    Inputs:
        data_dir (Path): Directory containing raw CSV or Excel files.

    Outputs:
        StationData: Nested dictionary such as data["Gisingen"]["Q"] = pd.Series.
    """

    files = list_supported_data_files(Path(data_dir))
    output: StationData = {"Gisingen": {}, "Diepoldsau": {}}
    missing: list[str] = []

    for spec in SERIES_SPECS:
        path = _find_file_for_spec(files, spec)
        if path is None:
            missing.append(f"{spec.station} {spec.variable}")
            continue
        output[spec.station][spec.variable] = read_timeseries_file(
            path,
            preferred_value_columns=spec.preferred_value_columns,
        )

    if missing:
        combined = _try_load_combined_long_file(files)
        if combined is not None:
            return combined
        raise DataNotFoundError(
            "Missing required raw series: "
            + ", ".join(missing)
            + ". "
            + expected_data_message()
        )

    return output


def aggregate_monthly_mean(series: pd.Series) -> pd.Series:
    """Aggregate a high-frequency timeseries to monthly mean values.

    Inputs:
        series (pd.Series): Numeric timeseries indexed by timestamps. The index
            can be 10-minute, 15-minute, daily, or irregular.

    Outputs:
        pd.Series: Monthly mean values indexed by month start timestamps.
    """

    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError("Monthly aggregation requires a pandas DatetimeIndex.")
    monthly = series.sort_index().resample("MS").mean().dropna()
    monthly.name = series.name
    return monthly


def aggregate_project_monthly(raw_data: StationData) -> StationData:
    """Aggregate every project series to monthly means.

    Inputs:
        raw_data (StationData): Nested dictionary of raw station/variable series.

    Outputs:
        StationData: Same nested structure with monthly mean series.
    """

    return {
        station: {
            variable: aggregate_monthly_mean(series)
            for variable, series in variables.items()
        }
        for station, variables in raw_data.items()
    }


def load_project_monthly_data(data_dir: Path) -> StationData:
    """Load raw project data and return monthly mean series.

    Inputs:
        data_dir (Path): Directory containing raw CSV or Excel files.

    Outputs:
        StationData: Nested dictionary of monthly mean Q and C series.
    """

    return aggregate_project_monthly(load_project_raw_data(data_dir))


def flatten_station_data(data: StationData) -> Dict[str, pd.Series]:
    """Flatten nested station data into labels like 'Gisingen_Q'.

    Inputs:
        data (StationData): Nested dictionary by station and variable.

    Outputs:
        dict[str, pd.Series]: Flat dictionary keyed by station and variable.
    """

    return {
        f"{station}_{variable}": series
        for station, variables in data.items()
        for variable, series in variables.items()
    }


def align_station_q_c(monthly_data: StationData, station: str) -> pd.DataFrame:
    """Align monthly Q and C series for one station.

    Inputs:
        monthly_data (StationData): Nested dictionary with monthly Q and C.
        station (str): Station name, for example "Gisingen" or "Diepoldsau".

    Outputs:
        pd.DataFrame: Columns Q and C aligned on the same monthly timestamps.
    """

    if station not in monthly_data:
        raise KeyError(f"Station {station!r} not found in monthly data.")
    variables = monthly_data[station]
    if "Q" not in variables or "C" not in variables:
        raise KeyError(f"Station {station!r} must contain both Q and C series.")
    frame = pd.concat({"Q": variables["Q"], "C": variables["C"]}, axis=1).dropna()
    frame.index.name = "datetime"
    return frame


def save_monthly_tables(monthly_data: StationData, output_dir: Path) -> Mapping[str, Path]:
    """Save monthly aggregated series as CSV tables.

    Inputs:
        monthly_data (StationData): Nested dictionary of monthly Q and C series.
        output_dir (Path): Directory where CSV tables should be written.

    Outputs:
        Mapping[str, Path]: Mapping from table label to written CSV path.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for station, variables in monthly_data.items():
        for variable, series in variables.items():
            path = output_dir / f"monthly_{station}_{variable}.csv"
            series.rename(variable).to_csv(path, index_label="datetime")
            written[f"{station}_{variable}"] = path
    return written


# Module 2 - Timeseries Analysis

This repository supports the Module 2 water resources lab assignment on timeseries analysis for the Rhein-Ill confluence.

The project studies monthly discharge `Q` and suspended sediment concentration `C` at:

- Gisingen station on the Ill River
- Diepoldsau, Rietbrucke station on the Rhein River downstream of the confluence

The scientific goal is to evaluate long-term hydrological and suspended sediment behaviour, fit AR/ARMA models, generate synthetic monthly series, estimate sediment mass rates, and discuss whether independent Q and C models are scientifically defensible.

## Repository Structure

```text
module2-timeseries-analysis/
├── notebooks/
│   └── Module2_Timeseries_Analysis.ipynb
├── src/
│   ├── data_loading.py
│   ├── section1_timeseries_review.py
│   ├── section2_timeseries_modelling.py
│   ├── section3_model_evaluation.py
│   ├── section4_sediment_influence.py
│   ├── section5_dependency_analysis.py
│   └── plotting.py
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── reports/
├── docs/
├── tests/
├── requirements.txt
├── environment.yml
├── run_all.py
└── README.md
```

## Install Dependencies

Using `venv`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Using Conda:

```bash
conda env create -f environment.yml
conda activate module2-timeseries-analysis
```

## Raw Data Location

Place raw files in:

```text
data/raw/
```

The current local project can read the provided four-file layout:

```text
Q_Gisingen_1976-2023.csv       columns: timestamp, q_m3s
SSC_Gisingen_2003-2020.csv     columns: timestamp, ssc_gL
Q_Diepoldsau_m3s.csv           columns: timestamp, q_m3s
SSC_Diepoldsau_gL.csv          columns: timestamp, ssc_gL
```

The loader also accepts CSV or Excel files with similar names and columns such as:

```text
datetime, Q, C, station, variable, value
```

Raw data are ignored by Git so large files are not pushed accidentally.

## Run the Notebook

From the repository root:

```bash
jupyter notebook notebooks/Module2_Timeseries_Analysis.ipynb
```

Run all notebook cells from top to bottom. Generated figures are saved in `outputs/figures/`; generated tables are saved in `outputs/tables/`.

## Run Tests

```bash
pytest
```

## Run a Smoke Test

Basic loading, monthly aggregation, Section 1, and Section 2:

```bash
python run_all.py
```

Full pipeline including AR/ARMA fitting:

```bash
python run_all.py --full
```

## Git Workflow

The main branch must always run from start to finish. Use feature branches and pull requests for every substantial change. Both team members must branch and merge at least once.

Read:

- `docs/GIT_WORKFLOW_FOR_TWO_MEMBERS.md`
- `docs/PEER_REVIEW_CHECKLIST.md`

## Important Scientific Reminder

Do not invent final numerical results. The notebook computes final values only from the real raw data in `data/raw/`. Demo data may be used in tests, but never as scientific evidence.


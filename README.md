# Module 2 - Timeseries Analysis

This repository contains the code and notebook for Assignment 2, Module 2:
timeseries analysis of discharge `Q` and suspended sediment concentration `C`.

The analysis uses two stations:

- Gisingen on the Ill River
- Diepoldsau, Rietbrucke on the Rhein River

The raw high-frequency data are aggregated to monthly mean values before the
main analysis.

## Project Structure

```text
module2-timeseries-analysis/
|-- notebooks/
|   `-- Module2_Timeseries_Analysis.ipynb
|-- src/
|   |-- data_loading.py
|   |-- section1_timeseries_review.py
|   |-- section2_timeseries_modelling.py
|   |-- section3_model_evaluation.py
|   |-- section4_sediment_influence.py
|   |-- section5_dependency_analysis.py
|   `-- plotting.py
|-- data/
|   |-- raw/
|   `-- processed/
|-- outputs/
|   |-- figures/
|   |-- reports/
|   `-- tables/
|-- tests/
|-- requirements.txt
|-- environment.yml
|-- run_all.py
|-- .gitignore
`-- README.md
```

## Installation

Using a Python virtual environment:

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

If you run the notebook in VS Code, choose the Python environment from this
project as the notebook kernel.

## Raw Data

Place the four raw CSV files in:

```text
data/raw/
```

Expected files and columns:

```text
Q_Gisingen_1976-2023.csv       columns: timestamp, q_m3s
SSC_Gisingen_2003-2020.csv     columns: timestamp, ssc_gL
Q_Diepoldsau_m3s.csv           columns: timestamp, q_m3s
SSC_Diepoldsau_gL.csv          columns: timestamp, ssc_gL
```

Raw data files are not uploaded to GitHub.

## Run the Notebook

Open and run:

```text
notebooks/Module2_Timeseries_Analysis.ipynb
```

The notebook follows the five assignment sections:

1. Timeseries review
2. Timeseries modelling
3. Timeseries application and evaluation
4. Ill to Rhein relative sediment influence
5. Independent variables

Generated figures and tables are saved under `outputs/`.

## Run From the Terminal

Basic smoke test:

```bash
python run_all.py
```

Full analysis:

```bash
python run_all.py --full
```

Run tests:

```bash
python -m pytest -q
```

## GitHub Workflow

Use feature branches and pull requests for collaboration. The `main` branch
should stay runnable from start to finish.

Only the files needed to run and review the assignment are tracked here:

- source code in `src/`
- the main notebook
- environment files
- tests
- repository configuration files

Local explanation notes in `docs/` are ignored by Git.

## Notes

The notebook computes numerical results from the raw data placed in
`data/raw/`. Do not treat test data or generated examples as final scientific
evidence.

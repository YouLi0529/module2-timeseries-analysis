"""Smoke-test runner for the Module 2 project.

Run from the repository root:

    python run_all.py

Use --full to also fit AR/ARMA models and run the sediment/dependency sections.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.data_loading import (
    DataNotFoundError,
    ensure_project_directories,
    load_project_monthly_data,
    save_monthly_tables,
)
from src.section1_timeseries_review import (
    format_timeseries_review,
    normalized_series_collection,
    run_timeseries_review,
)
from src.section2_timeseries_modelling import (
    analyse_acf_pacf_collection,
    format_order_selection,
)
from src.section3_model_evaluation import (
    evaluate_model_collection,
    format_model_evaluation,
)
from src.section4_sediment_influence import (
    format_sediment_influence,
    run_sediment_influence_analysis,
)
from src.section5_dependency_analysis import (
    format_dependency_results,
    run_dependency_analysis,
)


def main() -> int:
    """Run a basic reproducibility check of the pipeline.

    Inputs:
        None from Python code. Command-line flag --full controls the depth.

    Outputs:
        int: Process exit code, 0 for success and 1 for missing data.
    """

    parser = argparse.ArgumentParser(description="Run Module 2 smoke checks.")
    parser.add_argument("--full", action="store_true", help="Run all analysis sections, including AR/ARMA fitting.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    ensure_project_directories(project_root)

    try:
        monthly_data = load_project_monthly_data(project_root / "data" / "raw")
    except DataNotFoundError as exc:
        print("Raw data are not available yet.")
        print(exc)
        return 1

    save_monthly_tables(monthly_data, project_root / "data" / "processed")
    print("Loaded and aggregated monthly data:")
    for station, variables in monthly_data.items():
        for variable, series in variables.items():
            print(f"  {station} {variable}: {len(series)} monthly values")

    review_results = run_timeseries_review(monthly_data)
    print("\nSection 1 completed")
    print(format_timeseries_review(review_results))

    normalized = normalized_series_collection(review_results)
    order_results = analyse_acf_pacf_collection(normalized)
    print("\nSection 2 completed")
    print(format_order_selection(order_results))

    if args.full:
        evaluation_results = evaluate_model_collection(normalized, order_results)
        print("\nSection 3 completed")
        print(format_model_evaluation(evaluation_results))

        sediment_results = run_sediment_influence_analysis(monthly_data, review_results, evaluation_results)
        print("\nSection 4 completed")
        print(format_sediment_influence(sediment_results))

        dependency_results = run_dependency_analysis(monthly_data)
        print("\nSection 5 completed")
        print(format_dependency_results(dependency_results))

    print("\nSmoke test finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from finguard.data_loader import find_dataset_path, load_dataset
from finguard.data_validation import validate_dataset
from finguard.feature_engineering import add_derived_features
from finguard.eda import generate_eda_plots


def main() -> int:
    dataset_path = find_dataset_path()
    if not dataset_path.exists():
        print(f"Dataset missing: {dataset_path}")
        print("Download the Kaggle dataset and place it in data/raw/creditcard.csv before running the pipeline.")
        return 1

    df = load_dataset(dataset_path)
    validation = validate_dataset(df)
    if not validation["is_valid"]:
        print("Dataset validation failed.")
        print(json.dumps(validation, indent=2))
        return 2

    processed_dir = Path(__file__).resolve().parents[1] / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    processed_path = processed_dir / "creditcard_processed.csv"
    feature_frame = add_derived_features(df).copy()
    feature_frame.to_csv(processed_path, index=False)

    report_dir = Path(__file__).resolve().parents[1] / "reports"
    generate_eda_plots(feature_frame, report_dir / "figures")
    print(f"Processed dataset saved to {processed_path}")
    print(json.dumps({"rows": len(df), "columns": len(df.columns), "valid": validation["is_valid"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

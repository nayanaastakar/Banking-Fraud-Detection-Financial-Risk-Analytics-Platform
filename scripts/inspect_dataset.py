from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from finguard.config import get_data_paths, load_config
from finguard.data_loader import find_dataset_path, load_dataset
from finguard.data_validation import validate_dataset
from finguard.eda import generate_eda_plots
from finguard.reporting import write_data_quality_summary


def main() -> int:
    config = load_config()
    dataset_path = find_dataset_path()
    print(f"Dataset path: {dataset_path}")
    if not dataset_path.exists():
        print("Dataset not found. Download the Kaggle Credit Card Fraud dataset and place it in data/raw/creditcard.csv.")
        return 1

    df = load_dataset(dataset_path)
    validation = validate_dataset(df)
    print(json.dumps({
        "rows": validation["rows"],
        "cols": validation["cols"],
        "missing_columns": validation["missing_columns"],
        "target_values": validation["target_values"],
        "empty": validation["empty"],
    }, indent=2))

    report_dir = Path(__file__).resolve().parents[1] / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    quality_path = report_dir / "data_quality_summary.csv"
    quality_data = []
    for column in df.columns:
        quality_data.append({
            "column": column,
            "null_count": int(df[column].isna().sum()),
            "null_pct": round(float(df[column].isna().mean() * 100), 4),
            "dtype": str(df[column].dtype),
        })
    import pandas as pd  # noqa: F401
    pd.DataFrame(quality_data).to_csv(quality_path, index=False)

    profile_path = report_dir / "data_profile.json"
    profile = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "class_distribution": df["Class"].value_counts().to_dict() if "Class" in df.columns else {},
    }
    profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

    figure_dir = report_dir / "figures"
    generate_eda_plots(df, figure_dir)
    print(f"Saved data quality summary: {quality_path}")
    print(f"Saved data profile: {profile_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

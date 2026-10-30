from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from finguard.data_loader import find_dataset_path, load_dataset
from finguard.reporting import create_executive_summary


def main() -> int:
    dataset_path = find_dataset_path()
    if not dataset_path.exists():
        print("Dataset missing. The executive summary will note that the actual dataset has not yet been loaded.")
        summary = {
            "total_transactions": 0,
            "fraudulent_transactions": 0,
            "fraud_rate": 0.0,
        }
    else:
        df = load_dataset(dataset_path)
        total = len(df)
        fraudulent = int(df["Class"].sum()) if "Class" in df.columns else 0
        summary = {
            "total_transactions": total,
            "fraudulent_transactions": fraudulent,
            "fraud_rate": float(fraudulent / total) if total else 0.0,
        }

    output_dir = Path(__file__).resolve().parents[1] / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "executive_summary.md"
    create_executive_summary(summary, target)
    print(f"Executive summary written to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

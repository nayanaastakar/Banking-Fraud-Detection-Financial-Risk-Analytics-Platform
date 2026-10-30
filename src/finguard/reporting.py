from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


def write_data_quality_summary(df: pd.DataFrame, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    quality = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_values": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
    }
    output_path.write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return output_path


def write_csv_report(data: list[dict], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not data:
        output_path.write_text("", encoding="utf-8")
        return output_path
    rows = pd.DataFrame(data)
    rows.to_csv(output_path, index=False)
    return output_path


def create_executive_summary(metrics: dict, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = [
        "# Executive Summary",
        "",
        "This report is generated from the real dataset when available and remains intentionally conservative if the dataset has not yet been downloaded.",
        "",
        f"Fraudulent transaction rate: {metrics.get('fraud_rate', 0.0):.4f}",
        f"Total transactions: {metrics.get('total_transactions', 0)}",
        f"Fraudulent transactions: {metrics.get('fraudulent_transactions', 0)}",
        "",
        "## Business interpretation",
        "- Fraud is a minority event and therefore should be evaluated with precision-recall oriented metrics.",
        "- Transaction amount and time-based patterns should be reviewed alongside model output to assess operational workload.",
        "- The model is an analytical tool, not an automated real-world decision engine.",
    ]
    output_path.write_text("\n".join(text), encoding="utf-8")
    return output_path

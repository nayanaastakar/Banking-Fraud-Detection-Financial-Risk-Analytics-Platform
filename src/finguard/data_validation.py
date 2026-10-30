from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from finguard.config import load_config


def validate_required_columns(df: pd.DataFrame, required_columns: list[str] | None = None) -> list[str]:
    if required_columns is None:
        required_columns = load_config().get("dataset", {}).get("expected_columns", [])
    return [col for col in required_columns if col not in df.columns]


def validate_target_values(df: pd.DataFrame, target_col: str = "Class") -> list[int]:
    if target_col not in df.columns:
        return []
    return sorted(set(pd.Series(df[target_col]).dropna().astype(int).unique().tolist()))


def validate_numeric_columns(df: pd.DataFrame, columns: list[str] | None = None) -> list[str]:
    if columns is None:
        columns = [c for c in df.columns if c != "Class"]
    invalid = []
    for col in columns:
        if col in df.columns:
            try:
                pd.to_numeric(df[col], errors="raise")
            except (TypeError, ValueError):
                invalid.append(col)
    return invalid


def report_nulls(df: pd.DataFrame) -> pd.DataFrame:
    null_summary = df.isna().sum().rename("null_count").to_frame()
    null_summary["null_pct"] = null_summary["null_count"] / len(df) * 100
    return null_summary.sort_values(["null_count", "null_pct"], ascending=False)


def detect_duplicates(df: pd.DataFrame) -> dict:
    exact = df.duplicated().sum()
    return {
        "exact_duplicates": int(exact),
        "duplicate_ratio": float(exact / len(df)) if len(df) else 0.0,
    }


def profile_dataframe(df: pd.DataFrame) -> dict:
    numeric = df.select_dtypes(include=["number"]).copy()
    description = numeric.describe().to_dict()
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_values": df.isna().sum().to_dict(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "duplicate_rows": int(df.duplicated().sum()),
        "class_distribution": df.iloc[:, -1].value_counts().to_dict() if len(df.columns) else {},
        "numeric_summary": description,
    }


def validate_dataset(df: pd.DataFrame, required_columns: list[str] | None = None) -> dict:
    cfg = load_config()
    target_col = cfg.get("dataset", {}).get("target_column", "Class")
    req_cols = required_columns or cfg.get("dataset", {}).get("expected_columns", [])
    missing_cols = validate_required_columns(df, req_cols)
    empty = df.empty
    target_values = validate_target_values(df, target_col)
    invalid_numeric = validate_numeric_columns(df, [c for c in req_cols if c != target_col])
    nulls = report_nulls(df)
    duplicates = detect_duplicates(df)
    return {
        "is_valid": not missing_cols and not empty and set(target_values).issubset({0, 1}) and not invalid_numeric,
        "missing_columns": missing_cols,
        "empty": empty,
        "target_values": target_values,
        "invalid_numeric_columns": invalid_numeric,
        "null_summary": nulls.to_dict(),
        "duplicate_summary": duplicates,
        "rows": int(len(df)),
        "cols": int(len(df.columns)),
    }


def save_profile_summary(df: pd.DataFrame, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    profile = profile_dataframe(df)
    output_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    return output_path

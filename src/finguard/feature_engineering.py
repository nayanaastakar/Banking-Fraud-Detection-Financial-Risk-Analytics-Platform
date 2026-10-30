from __future__ import annotations

import numpy as np
import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if "Time" in result.columns:
        result["time_hours"] = result["Time"] / 3600.0
        result["time_band"] = pd.cut(
            result["time_hours"],
            bins=[0, 6, 12, 18, 24, 48, 72, np.inf],
            labels=["0-6h", "6-12h", "12-18h", "18-24h", "1-2d", "2-3d", "3d+"],
            right=False,
        )
    return result


def add_amount_bands(df: pd.DataFrame, amount_column: str = "Amount") -> pd.DataFrame:
    result = df.copy()
    if amount_column in result.columns:
        bins = [0, 10, 50, 100, 250, 500, 1000, 5000, float("inf")]
        labels = ["0-10", "10-50", "50-100", "100-250", "250-500", "500-1000", "1000-5000", "5000+"]
        result["amount_band"] = pd.cut(result[amount_column], bins=bins, labels=labels, right=False)
    return result


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    result = add_time_features(df)
    result = add_amount_bands(result)
    return result

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def get_feature_columns(df: pd.DataFrame, target_column: str = "Class") -> list[str]:
    protected_columns = {
        target_column,
        "transaction_hash",
        "transaction_id",
        "prediction_id",
        "model_run_id",
        "id",
    }
    return [column for column in df.columns if column not in protected_columns]


def prepare_model_data(df: pd.DataFrame, target_column: str = "Class") -> tuple[pd.DataFrame, pd.Series]:
    features = get_feature_columns(df, target_column)
    X = df[features].copy()
    y = df[target_column].astype(int)
    return X, y


def make_train_test_split(df: pd.DataFrame, target_column: str = "Class", test_size: float = 0.2, random_state: int = 42):
    X, y = prepare_model_data(df, target_column)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    return X_train, X_test, y_train, y_test


def add_missing_indicator(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    result = df.copy()
    for column in columns or []:
        result[f"{column}_missing"] = result[column].isna().astype(int)
    return result


def check_target_leakage(features: list[str], target_column: str = "Class") -> bool:
    return target_column in features

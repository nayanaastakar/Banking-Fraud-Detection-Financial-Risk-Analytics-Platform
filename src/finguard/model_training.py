from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from finguard.feature_engineering import add_derived_features
from finguard.model_evaluation import calculate_model_metrics, threshold_analysis
from finguard.preprocessing import get_feature_columns


def train_validation_split(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)


def build_model_specs():
    return {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler(with_mean=False)),
                ("model", LogisticRegression(class_weight="balanced", solver="liblinear", max_iter=2000, random_state=42)),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
            min_samples_leaf=5,
            n_jobs=-1,
        ),
    }


def select_best_threshold(y_valid, y_prob_valid, candidate_thresholds=None):
    candidate_thresholds = candidate_thresholds or [0.3, 0.4, 0.5, 0.6, 0.7]
    best = None
    for threshold in candidate_thresholds:
        metrics = calculate_model_metrics(y_valid, y_prob_valid, threshold=threshold)
        score = (metrics["precision"] + metrics["recall"] + metrics["f1"]) / 3
        candidate = {"threshold": threshold, "score": score, **metrics}
        if best is None or candidate["score"] > best["score"]:
            best = candidate
    return best


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    protected_columns = {"transaction_hash", "transaction_id", "prediction_id", "model_run_id", "id"}
    numeric_columns = [
        column for column in X.columns
        if column not in protected_columns and pd.api.types.is_numeric_dtype(X[column])
    ]
    categorical_columns = [
        column for column in X.columns
        if column not in protected_columns
        and not pd.api.types.is_numeric_dtype(X[column])
        and X[column].nunique(dropna=False) <= 50
    ]
    transformers = []

    if numeric_columns:
        transformers.append(("numeric", StandardScaler(with_mean=False), numeric_columns))
    if categorical_columns:
        transformers.append(("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_columns))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def train_model_suite(df: pd.DataFrame, target_column: str = "Class"):
    frame = add_derived_features(df).copy()
    feature_columns = get_feature_columns(frame, target_column)
    X = frame[feature_columns]
    y = frame[target_column].astype(int)
    X_train, X_valid, y_train, y_valid = train_validation_split(X, y, test_size=0.2, random_state=42)
    results = []
    fitted_models = {}
    for model_name, model in build_model_specs().items():
        pipeline = Pipeline([
            ("preprocessor", build_preprocessor(X_train)),
            ("model", model),
        ])
        fitted = pipeline.fit(X_train, y_train)
        y_prob_valid = fitted.predict_proba(X_valid)[:, 1]
        best_threshold = select_best_threshold(y_valid, y_prob_valid)
        metrics = calculate_model_metrics(y_valid, y_prob_valid, threshold=best_threshold["threshold"])
        fitted_models[model_name] = {
            "model": fitted,
            "threshold": best_threshold["threshold"],
            "feature_columns": feature_columns,
            "metrics": metrics,
        }
        results.append({
            "model_name": model_name,
            "selected_threshold": best_threshold["threshold"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "roc_auc": metrics["roc_auc"],
            "average_precision": metrics["average_precision"],
            "specificity": metrics["specificity"],
            "false_positive_rate": metrics["false_positive_rate"],
            "confusion_matrix": metrics["confusion_matrix"],
        })
    return pd.DataFrame(results), fitted_models


def train_models(df: pd.DataFrame, target_column: str = "Class"):
    results, _ = train_model_suite(df, target_column=target_column)
    return results


def save_model_artifacts(model_name: str, model_obj, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / f"{model_name}.joblib"
    joblib.dump(model_obj, artifact_path)
    return artifact_path

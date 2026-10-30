from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from finguard.config import get_data_paths, get_env_value, load_config


def find_dataset_path() -> Path:
    config = load_config()
    env_path = get_env_value("DATASET_PATH")
    if env_path:
        candidate = Path(env_path)
        if candidate.exists():
            return candidate
    dataset_cfg = config.get("dataset", {})
    default_path = Path(dataset_cfg.get("raw_dir", "data/raw")) / dataset_cfg.get("file_name", "creditcard.csv")
    if default_path.exists():
        return default_path
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "data" / "raw"
    expected = raw_dir / dataset_cfg.get("file_name", "creditcard.csv")
    return expected


def load_dataset(path: str | Path | None = None) -> pd.DataFrame:
    dataset_path = Path(path) if path is not None else find_dataset_path()
    dataset_path = dataset_path.expanduser().resolve()
    if not dataset_path.exists():
        raise FileNotFoundError(
            "Dataset not found. Place the Kaggle Credit Card Fraud dataset at "
            f"{dataset_path} or set DATASET_PATH in the .env file."
        )
    return pd.read_csv(dataset_path, low_memory=False)


def save_processed_dataset(df: pd.DataFrame, filename: str) -> Path:
    paths = get_data_paths()
    destination = paths["processed_dir"] / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)
    return destination

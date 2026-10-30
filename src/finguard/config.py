from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config(path: str | Path = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_environment() -> None:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv(PROJECT_ROOT / ".env.example")


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_data_paths() -> dict:
    cfg = load_config()
    raw_dir = PROJECT_ROOT / cfg.get("dataset", {}).get("raw_dir", "data/raw")
    processed_dir = PROJECT_ROOT / cfg.get("dataset", {}).get("processed_dir", "data/processed")
    export_dir = PROJECT_ROOT / cfg.get("dataset", {}).get("export_dir", "data/exports")
    reports_dir = PROJECT_ROOT / cfg.get("dataset", {}).get("reports_dir", "reports")
    models_dir = PROJECT_ROOT / cfg.get("dataset", {}).get("models_dir", "models")
    file_name = cfg.get("dataset", {}).get("file_name", "creditcard.csv")
    return {
        "root": PROJECT_ROOT,
        "raw_dir": raw_dir,
        "processed_dir": processed_dir,
        "export_dir": export_dir,
        "reports_dir": reports_dir,
        "models_dir": models_dir,
        "dataset_path": raw_dir / file_name,
    }


def get_env_value(name: str, default: str | None = None) -> str | None:
    load_environment()
    return os.getenv(name, default)

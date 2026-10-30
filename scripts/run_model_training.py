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
from finguard.database import connect_mysql
from finguard.database_loader import (
    compute_transaction_hash,
    deduplicate_transaction_records,
    load_dataframe_to_mysql,
    load_model_run_to_mysql,
    load_prediction_records_to_mysql,
)
from finguard.feature_engineering import add_derived_features
from finguard.model_training import save_model_artifacts, train_model_suite


def main() -> int:
    dataset_path = find_dataset_path()
    if not dataset_path.exists():
        print("Dataset missing. Download the real dataset before training models.")
        return 1

    df = load_dataset(dataset_path)
    deduped_df = deduplicate_transaction_records(df)
    comparison, fitted_models = train_model_suite(deduped_df)

    # Save model artifacts
    models_dir = PROJECT_ROOT / "models"
    for model_name, spec in fitted_models.items():
        saved_path = save_model_artifacts(model_name, spec["model"], models_dir)
        print(f"Saved {model_name} model artifact to {saved_path}")

    load_result = load_dataframe_to_mysql(deduped_df, table_name="transactions")
    if load_result["status"] == "loaded":
        connection = connect_mysql()
        transaction_rows = connection.cursor()
        transaction_rows.execute("SELECT transaction_id, transaction_hash FROM transactions")
        rows = transaction_rows.fetchall()
        transaction_rows.close()
        connection.close()
        hash_to_id = {record[1]: int(record[0]) for record in rows}

        predictions_base = add_derived_features(deduped_df).copy()
        if "transaction_hash" not in predictions_base.columns:
            predictions_base["transaction_hash"] = predictions_base.apply(compute_transaction_hash, axis=1)
        predictions_base["transaction_id"] = predictions_base["transaction_hash"].map(hash_to_id)

        for model_name, spec in fitted_models.items():
            model = spec["model"]
            threshold = spec["threshold"]
            feature_columns = spec["feature_columns"]
            predictions_df = predictions_base.copy()
            predictions_df["predicted_probability"] = model.predict_proba(predictions_df[feature_columns])[:, 1]
            predictions_df["predicted_label"] = (predictions_df["predicted_probability"] >= threshold).astype(int)

            prediction_result = load_prediction_records_to_mysql(
                predictions_df[["transaction_id", "predicted_probability", "predicted_label"]],
                model_name=model_name,
                threshold_used=threshold,
            )
            model_run_result = load_model_run_to_mysql(
                model_name=model_name,
                threshold_used=threshold,
                metrics=spec["metrics"],
                training_dataset_size=len(deduped_df),
                validation_dataset_size=max(1, int(len(deduped_df) * 0.2)),
            )
            print(f"{model_name}: {prediction_result} | {model_run_result}")
    else:
        print(f"Transaction load skipped: {load_result}")

    output_dir = PROJECT_ROOT / "reports" / "model_metrics"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "model_comparison.csv"
    comparison.to_csv(csv_path, index=False)
    print(json.dumps(comparison.to_dict(orient="records"), indent=2))
    print(f"Saved model comparison to {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

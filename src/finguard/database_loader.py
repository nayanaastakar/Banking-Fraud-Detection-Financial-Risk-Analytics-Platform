from __future__ import annotations

import hashlib
from datetime import datetime

import pandas as pd

from finguard.database import connect_mysql


def compute_transaction_hash(row: pd.Series | dict) -> str:
    if isinstance(row, dict):
        time_val = int(row.get("Time", 0))
        amt_val = float(row.get("Amount", 0.0))
        class_val = int(row.get("Class", 0))
        v_vals = [str(float(row.get(f"V{i}", 0.0))) for i in range(1, 29)]
    else:
        time_val = int(row.get("Time", 0))
        amt_val = float(row.get("Amount", 0.0))
        class_val = int(row.get("Class", 0))
        v_vals = [str(float(row.get(f"V{i}", 0.0))) for i in range(1, 29)]
    payload = f"{time_val}|{amt_val}|{class_val}|" + "|".join(v_vals)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def deduplicate_transaction_records(df: pd.DataFrame, hash_column: str = "transaction_hash") -> pd.DataFrame:
    if df.empty:
        return df.copy()

    work = df.copy()
    if hash_column not in work.columns:
        work[hash_column] = work.apply(compute_transaction_hash, axis=1)

    deduped = work.drop_duplicates(subset=[hash_column], keep="first").reset_index(drop=True)
    return deduped


def build_transactions_insert_sql() -> str:
    return """
    INSERT INTO transactions (
        transaction_time, transaction_amount, class_label, transaction_hash,
        v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
        v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
        v21, v22, v23, v24, v25, v26, v27, v28
    ) VALUES (
        %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        transaction_amount = VALUES(transaction_amount),
        class_label = VALUES(class_label)
    """


def build_predictions_insert_sql() -> str:
    return """
    INSERT INTO transaction_predictions (
        transaction_id, model_name, predicted_probability, predicted_label, threshold_used, prediction_timestamp
    ) VALUES (
        %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        predicted_probability = VALUES(predicted_probability),
        predicted_label = VALUES(predicted_label),
        threshold_used = VALUES(threshold_used),
        prediction_timestamp = VALUES(prediction_timestamp)
    """


def build_model_run_insert_sql() -> str:
    return """
    INSERT INTO model_runs (
        model_name, run_timestamp, training_dataset_size, validation_dataset_size,
        decision_threshold, precision_value, recall_value, f1_value,
        average_precision_value, roc_auc_value
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """


def _execute_batch_insert(cursor, sql: str, records: list[tuple], batch_size: int = 1000) -> None:
    for start in range(0, len(records), batch_size):
        chunk = records[start : start + batch_size]
        if not chunk:
            continue
        cursor.executemany(sql, chunk)


def remove_duplicate_prediction_rows(model_name: str | None = None) -> int:
    try:
        connection = connect_mysql()
    except Exception:
        return 0
    cursor = connection.cursor()
    if model_name:
        cursor.execute(
            """
            DELETE p1
            FROM transaction_predictions p1
            INNER JOIN transaction_predictions p2
                ON p1.model_name = p2.model_name
               AND p1.transaction_id = p2.transaction_id
               AND p1.prediction_id > p2.prediction_id
            WHERE p1.model_name = %s
            """,
            (model_name,),
        )
    else:
        cursor.execute(
            """
            DELETE p1
            FROM transaction_predictions p1
            INNER JOIN transaction_predictions p2
                ON p1.model_name = p2.model_name
               AND p1.transaction_id = p2.transaction_id
               AND p1.prediction_id > p2.prediction_id
            """
        )
    affected = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()
    return int(affected)


def load_dataframe_to_mysql(df: pd.DataFrame, table_name: str = "transactions") -> dict:
    try:
        connection = connect_mysql()
    except Exception as exc:  # pragma: no cover - environment dependency
        return {
            "status": "skipped",
            "reason": f"MySQL unavailable: {exc}",
            "inserted": 0,
            "skipped": len(df),
            "failed": 0,
        }

    cursor = connection.cursor()
    deduped_df = deduplicate_transaction_records(df)

    if table_name == "transactions":
        cursor.execute("SELECT COUNT(*) FROM transactions")
        row = cursor.fetchone()
        current_count = row[0] if row else 0
        if current_count >= len(deduped_df):
            cursor.close()
            connection.close()
            return {
                "status": "loaded",
                "inserted": 0,
                "skipped": len(df) - len(deduped_df),
                "failed": 0,
            }

        records = []
        for r in deduped_df.itertuples(index=False):
            values = [
                int(getattr(r, "Time", 0)),
                float(getattr(r, "Amount", 0.0)),
                int(getattr(r, "Class", 0)),
                getattr(r, "transaction_hash"),
            ]
            for feature in [f"V{i}" for i in range(1, 29)]:
                values.append(float(getattr(r, feature, 0.0)))
            records.append(tuple(values))

        sql = build_transactions_insert_sql()
        _execute_batch_insert(cursor, sql, records, batch_size=2000)
        connection.commit()
        inserted = len(records)
        skipped = len(df) - len(deduped_df)
        failed = 0
    else:
        inserted = 0
        skipped = len(deduped_df)
        failed = 0

    cursor.close()
    connection.close()
    return {
        "status": "loaded",
        "inserted": int(inserted),
        "skipped": int(skipped),
        "failed": int(failed),
    }


def load_model_run_to_mysql(
    model_name: str,
    threshold_used: float,
    metrics: dict,
    training_dataset_size: int,
    validation_dataset_size: int,
) -> dict:
    record = (
        model_name,
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        int(training_dataset_size),
        int(validation_dataset_size),
        float(threshold_used),
        float(metrics["precision"]),
        float(metrics["recall"]),
        float(metrics["f1"]),
        float(metrics["average_precision"]),
        float(metrics["roc_auc"]),
    )

    try:
        connection = connect_mysql()
    except Exception as exc:  # pragma: no cover - environment dependency
        return {"status": "skipped", "reason": str(exc), "model_run_id": None}

    cursor = connection.cursor()
    cursor.execute(build_model_run_insert_sql(), record)
    connection.commit()
    model_run_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return {"status": "loaded", "model_run_id": int(model_run_id)}


def load_prediction_records_to_mysql(
    prediction_frame: pd.DataFrame,
    model_name: str,
    threshold_used: float,
) -> dict:
    if prediction_frame.empty:
        return {"status": "loaded", "inserted": 0, "skipped": 0, "failed": 0}

    required_columns = {"transaction_id", "predicted_probability", "predicted_label"}
    missing = required_columns - set(prediction_frame.columns)
    if missing:
        raise ValueError(f"Prediction frame is missing required columns: {sorted(missing)}")

    deduped = prediction_frame.drop_duplicates(subset=["transaction_id"], keep="first").reset_index(drop=True)
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    records = [
        (
            int(getattr(r, "transaction_id")),
            model_name,
            float(getattr(r, "predicted_probability")),
            int(getattr(r, "predicted_label")),
            float(threshold_used),
            ts,
        )
        for r in deduped.itertuples(index=False)
    ]

    try:
        connection = connect_mysql()
    except Exception as exc:  # pragma: no cover - environment dependency
        return {
            "status": "skipped",
            "reason": f"MySQL unavailable: {exc}",
            "inserted": 0,
            "skipped": len(prediction_frame),
            "failed": 0,
        }

    cursor = connection.cursor()
    sql = build_predictions_insert_sql()
    _execute_batch_insert(cursor, sql, records, batch_size=5000)
    connection.commit()
    cursor.close()
    connection.close()
    return {
        "status": "loaded",
        "inserted": int(len(records)),
        "skipped": int(len(prediction_frame) - len(deduped)),
        "failed": 0,
    }

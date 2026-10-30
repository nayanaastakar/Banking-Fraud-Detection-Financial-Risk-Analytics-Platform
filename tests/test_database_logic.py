import pandas as pd
import pytest

from finguard.database import get_schema_sql, load_mysql_env
from finguard.database_loader import deduplicate_transaction_records


def test_mysql_schema_contains_expected_tables_and_constraints():
    sql = get_schema_sql()
    assert "CREATE TABLE IF NOT EXISTS transactions" in sql
    assert "CREATE TABLE IF NOT EXISTS model_runs" in sql
    assert "CREATE TABLE IF NOT EXISTS transaction_predictions" in sql
    assert "FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)" in sql
    assert "UNIQUE KEY uq_prediction_transaction_model (transaction_id, model_name)" in sql


def test_deduplicate_transaction_records_keeps_one_row_per_transaction_hash():
    df = pd.DataFrame(
        [
            {"transaction_hash": "aaa", "Time": 1, "Amount": 10.0, "Class": 0, "V1": 1.0, "V2": 2.0},
            {"transaction_hash": "aaa", "Time": 1, "Amount": 10.0, "Class": 0, "V1": 1.0, "V2": 2.0},
            {"transaction_hash": "bbb", "Time": 2, "Amount": 25.0, "Class": 1, "V1": 3.0, "V2": 4.0},
        ]
    )

    deduped = deduplicate_transaction_records(df)

    assert len(deduped) == 2
    assert deduped["transaction_hash"].nunique() == 2


def test_load_mysql_env_requires_local_credentials(monkeypatch):
    for key in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]:
        monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("DB_PASSWORD", "")
    monkeypatch.setenv("DB_USER", "")

    with pytest.raises(RuntimeError, match="DB_PASSWORD|.env"):
        load_mysql_env()

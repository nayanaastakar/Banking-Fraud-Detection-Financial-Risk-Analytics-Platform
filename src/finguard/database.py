from __future__ import annotations

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

from finguard.config import get_project_root


def load_mysql_env() -> dict:
    env_path = get_project_root() / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    database = os.getenv("DB_NAME", "finguard_analytics")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD")

    placeholder_values = {"", "your_mysql_password", "your_mysql_user", "changeme", "password"}
    if password is None or password.strip() == "" or password.lower() in {v.lower() for v in placeholder_values if v}:
        raise RuntimeError(
            "MySQL credentials are not configured for this local project. "
            "Create a local .env file in the project root with valid DB_USER and DB_PASSWORD values, "
            "or set DB_USER/DB_PASSWORD in the current environment. Do not share or commit credentials."
        )

    return {
        "host": host,
        "port": port,
        "database": database,
        "user": user,
        "password": password,
    }


def connect_mysql() -> mysql.connector.MySQLConnection:
    creds = load_mysql_env()
    return mysql.connector.connect(
        host=creds["host"],
        port=creds["port"],
        database=creds["database"],
        user=creds["user"],
        password=creds["password"],
        autocommit=False,
    )


def get_schema_sql() -> str:
    return """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transaction_time INT,
    transaction_amount DECIMAL(18, 4),
    class_label TINYINT,
    transaction_hash CHAR(64) NOT NULL,
    v1 DOUBLE,
    v2 DOUBLE,
    v3 DOUBLE,
    v4 DOUBLE,
    v5 DOUBLE,
    v6 DOUBLE,
    v7 DOUBLE,
    v8 DOUBLE,
    v9 DOUBLE,
    v10 DOUBLE,
    v11 DOUBLE,
    v12 DOUBLE,
    v13 DOUBLE,
    v14 DOUBLE,
    v15 DOUBLE,
    v16 DOUBLE,
    v17 DOUBLE,
    v18 DOUBLE,
    v19 DOUBLE,
    v20 DOUBLE,
    v21 DOUBLE,
    v22 DOUBLE,
    v23 DOUBLE,
    v24 DOUBLE,
    v25 DOUBLE,
    v26 DOUBLE,
    v27 DOUBLE,
    v28 DOUBLE,
    UNIQUE KEY uq_transaction_hash (transaction_hash),
    INDEX idx_class_time (class_label, transaction_time),
    INDEX idx_amount (transaction_amount),
    INDEX idx_time (transaction_time)
);

CREATE TABLE IF NOT EXISTS model_runs (
    model_run_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100),
    run_timestamp DATETIME,
    training_dataset_size INT,
    validation_dataset_size INT,
    decision_threshold DECIMAL(5, 4),
    precision_value DECIMAL(10, 6),
    recall_value DECIMAL(10, 6),
    f1_value DECIMAL(10, 6),
    average_precision_value DECIMAL(10, 6),
    roc_auc_value DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transaction_predictions (
    prediction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transaction_id BIGINT,
    model_name VARCHAR(100),
    predicted_probability DECIMAL(10, 6),
    predicted_label TINYINT,
    threshold_used DECIMAL(5, 4),
    prediction_timestamp DATETIME,
    UNIQUE KEY uq_prediction_transaction_model (transaction_id, model_name),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);
"""

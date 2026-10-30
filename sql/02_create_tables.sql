USE finguard_analytics;

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id BIGINT NOT NULL AUTO_INCREMENT,
    transaction_time INT,
    transaction_amount DECIMAL(18,4),
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
    PRIMARY KEY (transaction_id),
    UNIQUE KEY uq_transaction_hash (transaction_hash),
    KEY idx_class_time (class_label, transaction_time),
    KEY idx_amount (transaction_amount),
    KEY idx_time (transaction_time)
);

CREATE TABLE IF NOT EXISTS model_runs (
    model_run_id BIGINT NOT NULL AUTO_INCREMENT,
    model_name VARCHAR(100) NOT NULL,
    run_timestamp DATETIME NOT NULL,
    training_dataset_size INT,
    validation_dataset_size INT,
    decision_threshold DECIMAL(5,4),
    precision_value DECIMAL(10,6),
    recall_value DECIMAL(10,6),
    f1_value DECIMAL(10,6),
    average_precision_value DECIMAL(10,6),
    roc_auc_value DECIMAL(10,6),
    PRIMARY KEY (model_run_id)
);

CREATE TABLE IF NOT EXISTS transaction_predictions (
    prediction_id BIGINT NOT NULL AUTO_INCREMENT,
    transaction_id BIGINT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    predicted_probability DECIMAL(10,6),
    predicted_label TINYINT,
    threshold_used DECIMAL(5,4),
    prediction_timestamp DATETIME,
    PRIMARY KEY (prediction_id),
    UNIQUE KEY uq_prediction_transaction_model (transaction_id, model_name),
    KEY idx_transaction (transaction_id),
    KEY idx_model_threshold (model_name, threshold_used),
    CONSTRAINT fk_prediction_transaction FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id)
);

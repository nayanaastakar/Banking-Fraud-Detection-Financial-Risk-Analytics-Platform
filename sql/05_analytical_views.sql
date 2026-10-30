USE finguard_analytics;

DROP VIEW IF EXISTS vw_fraud_overview;
CREATE VIEW vw_fraud_overview AS
SELECT
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraudulent_transactions,
    ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate,
    ROUND(SUM(transaction_amount), 4) AS total_transaction_amount,
    ROUND(SUM(CASE WHEN class_label = 1 THEN transaction_amount ELSE 0 END), 4) AS fraud_transaction_amount
FROM transactions;

DROP VIEW IF EXISTS vw_fraud_by_time_band;
CREATE VIEW vw_fraud_by_time_band AS
SELECT
    CASE
        WHEN transaction_time BETWEEN 0 AND 3599 THEN '0-1h'
        WHEN transaction_time BETWEEN 3600 AND 7199 THEN '1-2h'
        WHEN transaction_time BETWEEN 7200 AND 10799 THEN '2-3h'
        ELSE '3h+'
    END AS time_band,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraudulent_transactions,
    ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY time_band;

DROP VIEW IF EXISTS vw_amount_band_analysis;
CREATE VIEW vw_amount_band_analysis AS
SELECT
    CASE
        WHEN transaction_amount < 10 THEN '0-10'
        WHEN transaction_amount < 50 THEN '10-50'
        WHEN transaction_amount < 100 THEN '50-100'
        WHEN transaction_amount < 250 THEN '100-250'
        WHEN transaction_amount < 500 THEN '250-500'
        WHEN transaction_amount < 1000 THEN '500-1000'
        ELSE '1000+'
    END AS amount_band,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraudulent_transactions,
    ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY amount_band;

DROP VIEW IF EXISTS vw_model_performance;
CREATE VIEW vw_model_performance AS
SELECT
    model_name,
    AVG(precision_value) AS avg_precision,
    AVG(recall_value) AS avg_recall,
    AVG(f1_value) AS avg_f1,
    MAX(decision_threshold) AS selected_threshold,
    MAX(average_precision_value) AS average_precision_value,
    MAX(roc_auc_value) AS roc_auc_value
FROM model_runs
GROUP BY model_name;

DROP VIEW IF EXISTS vw_prediction_outcomes;
CREATE VIEW vw_prediction_outcomes AS
SELECT
    p.prediction_id,
    p.transaction_id,
    p.model_name,
    p.predicted_probability,
    p.predicted_label,
    p.threshold_used,
    t.class_label,
    CASE
        WHEN p.predicted_label = 1 AND t.class_label = 1 THEN 'True Positive'
        WHEN p.predicted_label = 1 AND t.class_label = 0 THEN 'False Positive'
        WHEN p.predicted_label = 0 AND t.class_label = 1 THEN 'False Negative'
        ELSE 'True Negative'
    END AS outcome
FROM transaction_predictions p
JOIN transactions t ON t.transaction_id = p.transaction_id;

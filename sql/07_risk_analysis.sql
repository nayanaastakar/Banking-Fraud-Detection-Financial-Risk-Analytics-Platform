USE finguard_analytics;

-- 11. Feature columns available for analytics
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'finguard_analytics'
  AND TABLE_NAME = 'transactions' AND COLUMN_NAME LIKE 'v%'
ORDER BY CAST(REPLACE(COLUMN_NAME, 'v', '') AS UNSIGNED);

-- 12. Average feature magnitude by class
SELECT
    'V1' AS feature_name,
    AVG(v1) AS avg_value,
    SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraud_count
FROM transactions
UNION ALL
SELECT 'V2', AVG(v2), SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) FROM transactions
UNION ALL
SELECT 'V3', AVG(v3), SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) FROM transactions;

-- 13. Mean amount by transaction time buckets
SELECT
    CASE
        WHEN transaction_time < 3600 THEN '0-1h'
        WHEN transaction_time < 7200 THEN '1-2h'
        ELSE '2h+'
    END AS time_bucket,
    ROUND(AVG(transaction_amount), 4) AS avg_amount,
    ROUND(AVG(CASE WHEN class_label = 1 THEN transaction_amount ELSE NULL END), 4) AS avg_fraud_amount
FROM transactions
GROUP BY time_bucket;

-- 14. Highest value fraudulent transactions by band
SELECT
    CASE
        WHEN transaction_amount < 50 THEN 'low'
        WHEN transaction_amount < 100 THEN 'medium'
        ELSE 'high'
    END AS amount_bucket,
    COUNT(*) AS fraud_count,
    ROUND(SUM(transaction_amount), 4) AS fraud_amount_total
FROM transactions
WHERE class_label = 1
GROUP BY amount_bucket;

-- 15. Fraud ratio by amount band and time bucket
SELECT
    CASE WHEN transaction_amount < 50 THEN 'low' ELSE 'high' END AS amount_bucket,
    CASE WHEN transaction_time < 7200 THEN 'early' ELSE 'later' END AS time_bucket,
    COUNT(*) AS total_count,
    SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY amount_bucket, time_bucket;

-- 16. Fraud concentration by amount percentile
WITH ranked AS (
    SELECT
        transaction_amount,
        class_label,
        NTILE(10) OVER (ORDER BY transaction_amount) AS percentile_band
    FROM transactions
)
SELECT percentile_band,
       COUNT(*) AS total_transactions,
       SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraud_count,
       ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate
FROM ranked
GROUP BY percentile_band
ORDER BY percentile_band;

-- 17. Model precision and recall totals (if prediction table is populated)
SELECT
    COUNT(*) AS flagged_transactions,
    SUM(CASE WHEN predicted_label = 1 THEN 1 ELSE 0 END) AS flagged_count,
    SUM(CASE WHEN predicted_label = 1 AND class_label = 1 THEN 1 ELSE 0 END) AS true_positives,
    SUM(CASE WHEN predicted_label = 1 AND class_label = 0 THEN 1 ELSE 0 END) AS false_positives,
    SUM(CASE WHEN predicted_label = 0 AND class_label = 1 THEN 1 ELSE 0 END) AS false_negatives
FROM vw_prediction_outcomes;

-- 18. False positive monetary impact
SELECT
    ROUND(SUM(CASE WHEN outcome = 'False Positive' THEN t.transaction_amount ELSE 0 END), 4) AS legitimate_amount_flagged
FROM vw_prediction_outcomes v
JOIN transactions t ON t.transaction_id = v.transaction_id;

-- 19. Missed fraud monetary exposure
SELECT
    ROUND(SUM(CASE WHEN outcome = 'False Negative' THEN t.transaction_amount ELSE 0 END), 4) AS fraud_amount_missed
FROM vw_prediction_outcomes v
JOIN transactions t ON t.transaction_id = v.transaction_id;

-- 20. Latest model run summary
SELECT model_name,
       run_timestamp,
       training_dataset_size,
       validation_dataset_size,
       decision_threshold,
       precision_value,
       recall_value,
       f1_value,
       average_precision_value,
       roc_auc_value
FROM model_runs
ORDER BY run_timestamp DESC
LIMIT 10;

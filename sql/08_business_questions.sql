USE finguard_analytics;

-- Business question 1: How many transactions are present?
SELECT COUNT(*) AS total_transactions FROM transactions;

-- Business question 2: How many fraudulent transactions are present?
SELECT COUNT(*) AS fraudulent_transactions FROM transactions WHERE class_label = 1;

-- Business question 3: What percentage of transactions are fraudulent?
SELECT ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate_pct
FROM transactions;

-- Business question 4: What is the total transaction amount?
SELECT ROUND(SUM(transaction_amount), 4) AS total_transaction_amount FROM transactions;

-- Business question 5: What is the total amount associated with fraudulent transactions?
SELECT ROUND(SUM(CASE WHEN class_label = 1 THEN transaction_amount ELSE 0 END), 4) AS fraud_amount_total
FROM transactions;

-- Business question 6: What is the average transaction amount by class?
SELECT class_label, ROUND(AVG(transaction_amount), 4) AS average_amount
FROM transactions
GROUP BY class_label;

-- Business question 7: How do fraudulent and legitimate transactions differ in amount?
SELECT class_label, AVG(transaction_amount) AS avg_amount, STDDEV(transaction_amount) AS amount_stddev
FROM transactions
GROUP BY class_label;

-- Business question 8: How are fraud cases distributed across transaction-time intervals?
SELECT CASE WHEN transaction_time < 3600 THEN '0-1h' WHEN transaction_time < 7200 THEN '1-2h' ELSE '2h+' END AS time_window,
       COUNT(*) AS cases,
       SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraud_cases
FROM transactions
GROUP BY time_window
ORDER BY fraud_cases DESC;

-- Business question 9: Which time intervals have the highest observed fraud concentration?
SELECT CASE WHEN transaction_time < 3600 THEN '0-1h' WHEN transaction_time < 7200 THEN '1-2h' ELSE '2h+' END AS time_window,
       ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY time_window
ORDER BY fraud_rate DESC;

-- Business question 10: How do fraud rates vary across transaction amount bands?
SELECT CASE WHEN transaction_amount < 50 THEN 'low' WHEN transaction_amount < 250 THEN 'medium' ELSE 'high' END AS amount_band,
       ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate,
       COUNT(*) AS total_transactions
FROM transactions
GROUP BY amount_band
ORDER BY fraud_rate DESC;

-- Business question 11: Which numerical features show the largest differences between fraud and non-fraud groups?
SELECT 'V1' AS feature_name, AVG(CASE WHEN class_label = 1 THEN v1 ELSE NULL END) - AVG(CASE WHEN class_label = 0 THEN v1 ELSE NULL END) AS mean_gap FROM transactions
UNION ALL
SELECT 'V2', AVG(CASE WHEN class_label = 1 THEN v2 ELSE NULL END) - AVG(CASE WHEN class_label = 0 THEN v2 ELSE NULL END) FROM transactions;

-- Business question 12: Which features have strongest univariate association with the target?
SELECT 'v1' AS feature, ABS(AVG(v1 * class_label) - AVG(v1) * AVG(class_label)) AS association_metric FROM transactions
UNION ALL
SELECT 'v2', ABS(AVG(v2 * class_label) - AVG(v2) * AVG(class_label)) FROM transactions;

-- Business question 13: What are the model precision, recall and F1 for the selected threshold?
SELECT model_name, precision_value, recall_value, f1_value
FROM model_runs
ORDER BY run_timestamp DESC
LIMIT 1;

-- Business question 14: How many false positives and false negatives occur?
SELECT
    SUM(CASE WHEN predicted_label = 1 AND class_label = 0 THEN 1 ELSE 0 END) AS false_positives,
    SUM(CASE WHEN predicted_label = 0 AND class_label = 1 THEN 1 ELSE 0 END) AS false_negatives
FROM vw_prediction_outcomes;

-- Business question 15: What is the false-positive rate?
SELECT
    ROUND(100.0 * SUM(CASE WHEN predicted_label = 1 AND t.class_label = 0 THEN 1 ELSE 0 END) / SUM(CASE WHEN t.class_label = 0 THEN 1 ELSE 0 END), 4) AS false_positive_rate_pct
FROM vw_prediction_outcomes v
JOIN transactions t ON t.transaction_id = v.transaction_id;

-- Business question 16: How many transactions are flagged per 1,000 transactions?
SELECT ROUND(1000.0 * SUM(CASE WHEN predicted_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS flagged_per_1000
FROM vw_prediction_outcomes;

-- Business question 17: How does threshold change the burden of alerts?
SELECT threshold_used, COUNT(*) AS flagged_transactions
FROM transaction_predictions
GROUP BY threshold_used
ORDER BY threshold_used;

-- Business question 18: How much legitimate transaction value would be associated with false-positive alerts?
SELECT ROUND(SUM(CASE WHEN outcome = 'False Positive' THEN t.transaction_amount ELSE 0 END), 4) AS false_positive_amount
FROM vw_prediction_outcomes v
JOIN transactions t ON t.transaction_id = v.transaction_id;

-- Business question 19: How much fraud remains undetected at threshold?
SELECT ROUND(SUM(CASE WHEN outcome = 'False Negative' THEN t.transaction_amount ELSE 0 END), 4) AS undetected_fraud_amount
FROM vw_prediction_outcomes v
JOIN transactions t ON t.transaction_id = v.transaction_id;

-- Business question 20: What is the distribution of model outcome categories?
SELECT outcome, COUNT(*) AS outcome_count
FROM vw_prediction_outcomes
GROUP BY outcome
ORDER BY outcome_count DESC;

USE finguard_analytics;

-- 1. Total transaction count
SELECT COUNT(*) AS total_transactions FROM transactions;

-- 2. Fraudulent transaction count
SELECT COUNT(*) AS fraudulent_transactions
FROM transactions
WHERE class_label = 1;

-- 3. Fraud percentage
SELECT ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_percentage
FROM transactions;

-- 4. Total transaction amount
SELECT ROUND(SUM(transaction_amount), 4) AS total_amount FROM transactions;

-- 5. Fraud-associated amount
SELECT ROUND(SUM(CASE WHEN class_label = 1 THEN transaction_amount ELSE 0 END), 4) AS fraud_amount
FROM transactions;

-- 6. Average transaction amount by class
SELECT class_label,
       ROUND(AVG(transaction_amount), 4) AS avg_transaction_amount
FROM transactions
GROUP BY class_label;

-- 7. Fraud and legitimate transaction amount comparison
SELECT class_label,
       COUNT(*) AS transaction_count,
       ROUND(AVG(transaction_amount), 4) AS avg_amount,
       ROUND(MIN(transaction_amount), 4) AS min_amount,
       ROUND(MAX(transaction_amount), 4) AS max_amount
FROM transactions
GROUP BY class_label;

-- 8. Fraud by transaction-time intervals
SELECT
    CASE
        WHEN transaction_time < 3600 THEN '0-1h'
        WHEN transaction_time < 7200 THEN '1-2h'
        WHEN transaction_time < 10800 THEN '2-3h'
        ELSE '3h+'
    END AS time_band,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY time_band
ORDER BY fraud_rate DESC;

-- 9. High-risk transaction amount bands
SELECT
    CASE
        WHEN transaction_amount < 10 THEN '0-10'
        WHEN transaction_amount < 50 THEN '10-50'
        WHEN transaction_amount < 100 THEN '50-100'
        WHEN transaction_amount < 250 THEN '100-250'
        WHEN transaction_amount < 500 THEN '250-500'
        ELSE '500+'
    END AS amount_band,
    COUNT(*) AS transaction_count,
    SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(100.0 * SUM(CASE WHEN class_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS fraud_rate
FROM transactions
GROUP BY amount_band
ORDER BY fraud_rate DESC;

-- 10. Top 10 fraud transactions by amount
SELECT transaction_id, transaction_time, transaction_amount, class_label
FROM transactions
WHERE class_label = 1
ORDER BY transaction_amount DESC
LIMIT 10;

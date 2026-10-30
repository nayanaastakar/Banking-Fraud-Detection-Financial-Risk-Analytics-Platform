USE finguard_analytics;

SELECT 'Transaction row count' AS check_name, COUNT(*) AS value FROM transactions;

SELECT 'Fraudulent transaction count' AS check_name, COUNT(*) AS value
FROM transactions
WHERE class_label = 1;

SELECT 'Missing amounts' AS check_name, COUNT(*) AS value
FROM transactions
WHERE transaction_amount IS NULL;

SELECT 'Duplicate transaction IDs' AS check_name, COUNT(*) AS value
FROM (
  SELECT transaction_id
  FROM transactions
  GROUP BY transaction_id
  HAVING COUNT(*) > 1
) dupes;

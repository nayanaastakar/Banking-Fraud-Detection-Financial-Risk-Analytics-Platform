USE finguard_analytics;

-- This script expects the processed dataset to already exist in the project folder.
-- Replace the CSV path below with the actual location on your MySQL host if needed.
-- Example:
-- LOAD DATA LOCAL INFILE 'data/processed/creditcard_processed.csv'
-- INTO TABLE transactions
-- FIELDS TERMINATED BY ','
-- OPTIONALLY ENCLOSED BY '"'
-- IGNORE 1 LINES
-- (
--   transaction_time, transaction_amount, class_label,
--   v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
--   v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
--   v21, v22, v23, v24, v25, v26, v27, v28
-- );

SELECT 'Update the CSV path and run this script in a configured MySQL environment.' AS status;

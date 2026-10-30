# DAX Measures

## Recommended measures
- Total Transactions = DISTINCTCOUNT(transactions[transaction_id])
- Fraud Transactions = CALCULATE(DISTINCTCOUNT(transactions[transaction_id]), transactions[class_label] = 1)
- Legitimate Transactions = CALCULATE(DISTINCTCOUNT(transactions[transaction_id]), transactions[class_label] = 0)
- Fraud Rate = DIVIDE([Fraud Transactions], [Total Transactions])
- Total Transaction Amount = SUM(transactions[transaction_amount])
- Fraud-Associated Transaction Amount = CALCULATE(SUM(transactions[transaction_amount]), transactions[class_label] = 1)
- Average Transaction Amount = AVERAGE(transactions[transaction_amount])
- Flagged Transactions = COUNTROWS(FILTER(transaction_predictions, transaction_predictions[predicted_label] = 1))
- Flag Rate = DIVIDE([Flagged Transactions], [Total Transactions])
- Precision = DIVIDE([True Positives], [True Positives] + [False Positives])
- Recall = DIVIDE([True Positives], [True Positives] + [False Negatives])
- F1 Score = DIVIDE(2 * [Precision] * [Recall], [Precision] + [Recall])

## Important note
These measures should be implemented in the final Power BI model after the actual dataset and predictions are loaded. The project does not fabricate results or dashboard values.

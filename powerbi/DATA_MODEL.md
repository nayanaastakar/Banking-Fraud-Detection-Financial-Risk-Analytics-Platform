# Power BI Data Model

## Recommended tables
- transactions
- model_runs
- transaction_predictions
- vw_fraud_overview
- vw_fraud_by_time_band
- vw_amount_band_analysis
- vw_model_performance
- vw_prediction_outcomes

## Relationship guidance
- `transaction_id` connects transactions to prediction outcomes.
- `model_name` and `run_timestamp` support run-level reporting.
- Use aggregated views for KPIs and operational summaries.

## Documentation note
The source dataset does not contain customer-level or merchant-level metadata, so the model remains transaction-centric.

# Database Design

## Overview
The database design covers the transaction-level source data, analytical views, and model result outputs. The schema is designed to support fraud analytics and power BI reporting without unnecessary duplication.

## Tables
### transactions
- transaction_id: surrogate key
- transaction_time: elapsed seconds from dataset start
- transaction_amount: numeric amount
- class_label: 0 or 1
- v1...v28: transformed numerical features

### model_runs
Stores reproducible runs and selected threshold details.

### transaction_predictions
Stores predicted probabilities and outcomes for each transaction.

## Indexes and constraints
- Primary keys on transaction identifier and model identifiers.
- Foreign key link from predictions to transactions.
- Indexes on class and time and amount columns.

## Trade-offs
- Surrogate IDs are used because the public dataset does not contain a stable customer or bank transaction identifier.
- Model outputs remain separate to preserve auditability and reduce mixed data types in the base table.
- The schema supports future expansion for operational reporting without requiring large denormalized tables.

# FinGuard Project Status

## Current verified environment

- Workspace: D:\Projects\Banking Fraud Detection & Financial Risk Analytics Platform
- Python: 3.11.9
- Git: initialized and configured
- MySQL Server: installed and running on localhost:3306 (MySQL80 service active)
- Kaggle dataset: downloaded and validated at `data/raw/creditcard.csv` (284,807 rows)
- Automated Test Suite: verified with `pytest -q` (16 passed in 4.60s)

## Verified completion status

### 1. Environment and Credential Validation
- Status: complete and verified
- Evidence: `scripts/validate_environment.py` confirmed all dependencies, environment configuration, and active connection to local MySQL server.

### 2. Dataset Acquisition and Quality Profiling
- Status: complete and verified
- Evidence: `scripts/inspect_dataset.py` validated 284,807 rows and 31 columns with 0 nulls.
- Output: `reports/data_quality_summary.csv` and `reports/data_profile.json`

### 3. Data Pipeline & Feature Engineering
- Status: complete and verified
- Evidence: `scripts/run_data_pipeline.py` generated `data/processed/creditcard_processed.csv` with derived time hours, time bands, and transaction amount tiers.

### 4. MySQL Live Schema & Analytical Views
- Status: complete and verified
- Evidence: `scripts/run_sql_setup.py` executed schema creation, enforced `uq_prediction_transaction_model` composite key, verified views (`vw_fraud_overview`, `vw_fraud_by_time_band`, `vw_amount_band_analysis`, `vw_model_performance`, `vw_prediction_outcomes`), and exported 20 analytical query result sets to `reports/sql_exports/`.

### 5. Model Training and Prediction Loading
- Status: complete and verified
- Evidence: `scripts/run_model_training.py` trained balanced Logistic Regression and Random Forest classifiers, serialized model artifacts to `models/`, loaded 283,726 predictions per model into MySQL, and saved `reports/model_metrics/model_comparison.csv`.

### 6. Reporting and Executive Brief
- Status: complete and verified
- Evidence: `scripts/generate_reports.py` created `reports/executive_summary.md`.

### 7. Automated Test Suite
- Status: complete and verified
- Evidence: `pytest -v` passed all 16 tests covering data validation, schema logic, feature engineering, and model metrics.

## Verified model metrics

| Model | Decision Threshold | Precision | Recall | F1 | Specificity | FPR | ROC-AUC | Average Precision |
|---|:---:|---:|---:|---:|---:|---:|---:|---:|
| **Logistic Regression** | 0.70 | 0.1079 | 0.8737 | 0.1921 | 0.9879 | 0.0121 | 0.9758 | 0.6925 |
| **Random Forest** | 0.70 | 0.9452 | 0.7263 | 0.8214 | 0.9999 | 0.00007 | 0.9569 | 0.8061 |

## Verified record reconciliation audit

- **Raw Kaggle Source:** 284,807 total rows (284,315 legitimate, 492 fraud, 1,081 duplicate hash rows).
- **Processed Dataset:** 284,807 rows with 34 engineered columns.
- **MySQL `transactions` Table:** 283,726 unique rows (283,253 legitimate, 473 fraud) with total monetary volume of $25,102,001.68 and $58,591.39 fraud exposure.
- **MySQL `transaction_predictions` Table:** 283,726 predictions per model (567,452 total rows) with zero orphan keys and composite unique constraint `uq_prediction_transaction_model`.

# Testing Report

## Summary
The project includes automated tests for data validation, preprocessing, feature engineering, evaluation logic, and schema assumptions. The current suite was validated against the real Kaggle dataset and the updated model pipeline.

## Actual verification runs

### 1. Test suite
Command executed:

```bash
.\.venv\Scripts\python -m pytest -q
```

Result:

```text
14 passed in 3.13s
```

### 2. Dataset validation
Command executed:

```bash
.\.venv\Scripts\python scripts/inspect_dataset.py
```

Result:

```text
Dataset path: data\raw\creditcard.csv
{
  "rows": 284807,
  "cols": 31,
  "missing_columns": [],
  "target_values": [0, 1],
  "empty": false
}
```

### 3. Data pipeline execution
Command executed:

```bash
.\.venv\Scripts\python scripts/run_data_pipeline.py
```

Result:

```text
Processed dataset saved to ...\data\processed\creditcard_processed.csv
{
  "rows": 284807,
  "columns": 31,
  "valid": true
}
```

### 4. Model training and comparison
Command executed:

```bash
.\.venv\Scripts\python scripts/run_model_training.py
```

Result: model comparison completed successfully and wrote the output to `reports/model_metrics/model_comparison.csv`.

### 5. Executive summary generation
Command executed:

```bash
.\.venv\Scripts\python scripts/generate_reports.py
```

Result: report written to `reports/executive_summary.md`.

## Covered test areas
- missing required columns
- empty input
- invalid target values
- successful valid-data path
- preprocessing and train/test separation
- feature engineering for time and amount bands
- confusion matrix and threshold-based evaluation
- model training with derived categorical features
- MySQL schema assumption checks

## Notes
- Real-data validation succeeded in this workspace.
- MySQL integration remains blocked by the absence of a MySQL server.
- Power BI Desktop is not installed, so no dashboard `.pbix` file exists here.
- The verified suite confirms the project behaves correctly on the actual downloaded Kaggle dataset and the implemented baseline code paths.

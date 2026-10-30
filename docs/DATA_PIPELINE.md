# Data Pipeline

## Stages
1. Locate the source dataset in `data/raw/`.
2. Validate required schema and target values.
3. Save a quality summary and data profile.
4. Perform feature enrichment and prepared model data splits.
5. Train and compare models.
6. Store results in `reports/model_metrics/` and MySQL-compatible tables.

## Known limitations
The pipeline is ready for execution once the real Kaggle dataset is available. In the current environment, the exact dataset IS not present, so only scaffolded execution is possible until the file is downloaded.

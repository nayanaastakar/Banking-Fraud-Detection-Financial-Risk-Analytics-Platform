# Data Dictionary

## Transaction fields
- Time: seconds elapsed from the first transaction in the dataset. Not a real timestamp.
- Amount: transaction amount in the source dataset currency context.
- Class: target label where 0 = legitimate and 1 = fraudulent.
- V1-V28: transformed numerical variables produced by PCA-style processing. Their original business meaning is not provided.

## Derived fields used in analysis
- time_hours: Time divided by 3600 to express elapsed time in hours.
- time_band: coarse time bucket for risk analysis.
- amount_band: coarse amount bucket for profiling.

## Notes
- No customer demographic, merchant, or location fields are assumed in this dataset.
- Feature-level interpretations should remain descriptive and observational.

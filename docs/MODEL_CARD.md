# Model Card

## Model purpose
The model is an analytical demonstration for identifying transactions associated with fraud risk using public transaction data.

## Dataset source
Public Kaggle credit card fraud dataset.

## Training procedure
- Read and validate the dataset.
- Split the data into train/validation/test sets with stratification.
- Fit baseline models on the training data.
- Tune threshold using validation data.
- Evaluate on the held-out test set.

## Target definition
- 0 = legitimate transaction
- 1 = fraudulent transaction

## Features used
- Amount, Time, and transformed V1-V28 features.

## Preprocessing
- Numeric validation
- Train/test separation before model fitting
- Standard scaling is used for logistic regression

## Evaluation methodology
- Confusion matrix and threshold analysis
- Precision, recall, F1, specificity, ROC-AUC, average precision
- Focus on precision-recall trade-offs because fraud is rare

## Threshold selection
The selected threshold is documented as part of the actual model run and should be reviewed against operational workload.

## Known limitations
- This is not a production banking system.
- The features are transformed and do not carry business semantics.
- Results depend on the exact dataset and the selected evaluation split.

## Appropriate uses
- Exploratory fraud-risk analysis
- Academic or portfolio-ready demonstration
- Dashboard and analytics workflow support

## Inappropriate uses
- Autonomous financial decisions
- Real-world customer risk decisions without governance oversight

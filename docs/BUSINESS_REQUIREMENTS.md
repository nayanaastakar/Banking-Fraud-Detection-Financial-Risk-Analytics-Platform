# Business Requirements

## Objective
This document explains the business questions asked in the project and how the metrics relate to operational decisions.

## Fraud overview questions
1. Total transaction count: informs dataset scope and investigation volume.
2. Fraudulent transaction count: establishes baseline risk prevalence.
3. Fraud percentage: highlights class imbalance.
4. Total transaction amount: indicates exposure in the observed dataset.
5. Fraud-associated amount: identifies how much of the transaction volume appears in the fraud class.
6. Average amount by class: shows whether fraudulent activity differs materially in value.

## Transaction behavior questions
1. Amount difference between classes: helps analysts identify atypical transaction sizes.
2. Time-based fraud distribution: identifies intervals where risk is elevated.
3. Best-performing time bands: supports prioritization of monitoring activity.
4. Risk by amount band: helps define operating thresholds and review queues.

## Feature analytics questions
1. Largest mean differences by feature: indicates candidate signals for investigation.
2. Strongest univariate associations: highlights variables that move with the fraud target.
3. Communicating feature findings: should remain descriptive and avoid causal claims because the dataset includes transformed features without business meanings.

## Model and operational analytics
1. Precision, recall, and F1 score: show how many alerts are actionable.
2. False positive and false negative counts: measure review burden and missed fraud.
3. False-positive rate: quantifies how often legitimate transactions are flagged.
4. Flagged transactions per 1,000: operationalized alert volume.
5. Threshold sensitivity: shows how investigation workload changes with alerting policy.

## Business risk
The project treats flagged transactions and fraud-associated amounts as analytical signals, not confirmed losses. This distinction is critical for responsible reporting.

## Business interpretation guidance
- A detected fraud case is not a confirmed loss by itself.
- A flagged transaction is not automatically fraudulent.
- Fraud analytics should support investigation decisions, not autonomous financial action.

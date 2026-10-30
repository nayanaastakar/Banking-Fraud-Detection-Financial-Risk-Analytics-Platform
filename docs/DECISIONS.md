# Decision Log

## 1. Project structure
The project uses a conventional data-science repository layout with separate areas for source code, SQL, notebooks, tests, and documentation. This keeps the workflow readable for beginners and professional reviewers.

## 2. Dataset source
The project is designed around the public Kaggle credit card fraud dataset (`mlg-ulb/creditcardfraud`). Because Kaggle CLI is unavailable here, the project will include a documented manual download path and will fail gracefully until the file is placed in the expected folder.

## 3. Environment assumptions
MySQL is not available in this environment, so SQL scripts are implemented and documented for a MySQL 8-compatible environment without claiming that a live database has been created here.

## 4. Modeling approach
The workflow uses interpretable baselines, including logistic regression and random forest, with a strong emphasis on precision-recall trade-offs because fraud detection is highly imbalanced.

## 5. Reporting approach
Outputs are generated from real loaded data only. The project avoids fabricated metrics and explicitly documents manual steps still required when data or software is unavailable.

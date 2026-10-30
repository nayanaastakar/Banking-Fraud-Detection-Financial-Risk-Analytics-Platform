from __future__ import annotations

import pandas as pd


def logistic_regression_coefficients(model, feature_names):
    if hasattr(model, "named_steps"):
        estimator = model.named_steps["model"]
    else:
        estimator = model
    if hasattr(estimator, "coef_"):
        coefficients = estimator.coef_[0]
        return pd.DataFrame({"feature": feature_names, "coefficient": coefficients}).sort_values("coefficient", ascending=False)
    return pd.DataFrame({"feature": feature_names, "coefficient": [0] * len(feature_names)})


def random_forest_importance(model, feature_names):
    if hasattr(model, "named_steps"):
        estimator = model.named_steps["model"]
    else:
        estimator = model
    if hasattr(estimator, "feature_importances_"):
        scores = estimator.feature_importances_
        return pd.DataFrame({"feature": feature_names, "importance": scores}).sort_values("importance", ascending=False)
    return pd.DataFrame({"feature": feature_names, "importance": [0] * len(feature_names)})

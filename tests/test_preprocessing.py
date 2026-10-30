import pandas as pd

from finguard.feature_engineering import add_derived_features
from finguard.model_training import train_models
from finguard.preprocessing import check_target_leakage, make_train_test_split, prepare_model_data


def test_prepare_model_data_excludes_target_column():
    df = pd.DataFrame({"Time": [1, 2, 3], "Amount": [10, 20, 30], "Class": [0, 1, 0]})
    X, y = prepare_model_data(df)
    assert list(X.columns) == ["Time", "Amount"]
    assert list(y.values) == [0, 1, 0]


def test_target_leakage_is_detected():
    features = ["Time", "Amount", "Class"]
    assert check_target_leakage(features) is True


def test_train_test_split_is_stratified_and_reproducible():
    df = pd.DataFrame({
        "Time": list(range(100)),
        "Amount": [float(i) for i in range(100)],
        "Class": [0] * 90 + [1] * 10,
    })
    X_train, X_test, y_train, y_test = make_train_test_split(df, test_size=0.2, random_state=42)
    assert len(X_train) == 80
    assert len(X_test) == 20
    assert y_train.nunique() == 2
    assert y_test.nunique() == 2


def test_train_models_handles_derived_categorical_features():
    df = pd.DataFrame({
        "Time": [0, 3600, 7200, 10800, 14400, 18000, 21600, 25200],
        "Amount": [1.0, 2.0, 3.0, 4.0, 5.0, 100.0, 200.0, 1000.0],
        "Class": [0, 0, 0, 0, 1, 1, 1, 1],
    })
    enriched = add_derived_features(df)
    result = train_models(enriched, target_column="Class")
    assert len(result) == 2
    assert {"logistic_regression", "random_forest"}.issubset(set(result["model_name"]))

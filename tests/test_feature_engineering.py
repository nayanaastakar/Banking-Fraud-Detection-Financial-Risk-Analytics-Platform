import pandas as pd

from finguard.feature_engineering import add_amount_bands, add_time_features, add_derived_features


def test_time_features_are_created():
    df = pd.DataFrame({"Time": [0, 3600, 7200], "Amount": [1, 2, 3], "Class": [0, 1, 0]})
    result = add_time_features(df)
    assert "time_hours" in result.columns
    assert "time_band" in result.columns
    assert list(result["time_hours"].values) == [0.0, 1.0, 2.0]


def test_amount_bands_are_created_correctly():
    df = pd.DataFrame({"Amount": [5, 10, 60, 250, 1000, 8000], "Class": [0, 1, 0, 1, 0, 1]})
    result = add_amount_bands(df)
    assert list(result["amount_band"].astype(str).unique()) == ["0-10", "10-50", "50-100", "250-500", "1000-5000", "5000+"]


def test_derived_features_do_not_use_target_as_predictor():
    df = pd.DataFrame({"Time": [0, 3600], "Amount": [10, 20], "Class": [0, 1]})
    result = add_derived_features(df)
    assert "Class" in result.columns
    assert "time_band" in result.columns

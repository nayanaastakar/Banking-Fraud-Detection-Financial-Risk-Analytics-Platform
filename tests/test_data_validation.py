import pandas as pd

from finguard.data_validation import validate_dataset, validate_required_columns, validate_target_values


def test_missing_required_columns_are_detected():
    df = pd.DataFrame({"Amount": [10.0, 20.0], "Class": [0, 1]})
    missing = validate_required_columns(df, ["Time", "Amount", "Class"])
    assert missing == ["Time"]


def test_empty_dataset_is_invalid():
    df = pd.DataFrame(columns=["Time", "Amount", "Class"])
    result = validate_dataset(df, ["Time", "Amount", "Class"])
    assert result["empty"] is True
    assert result["is_valid"] is False


def test_invalid_target_values_are_reported():
    df = pd.DataFrame({"Time": [1, 2], "Amount": [10.0, 20.0], "Class": [0, 2]})
    values = validate_target_values(df)
    assert set(values) == {0, 2}


def test_valid_input_dataset_is_accepted():
    df = pd.DataFrame(
        {
            "Time": [10, 20, 30, 40],
            "Amount": [30.0, 100.0, 250.0, 500.0],
            "Class": [0, 1, 0, 1],
        }
    )
    result = validate_dataset(df, ["Time", "Amount", "Class"])
    assert result["is_valid"] is True
    assert result["missing_columns"] == []

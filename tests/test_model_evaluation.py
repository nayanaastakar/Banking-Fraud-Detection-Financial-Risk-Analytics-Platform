import numpy as np

from finguard.model_evaluation import calculate_model_metrics, threshold_analysis


def test_calculate_model_metrics_confusion_counts_are_correct():
    y_true = np.array([0, 0, 1, 1, 1])
    y_prob = np.array([0.1, 0.6, 0.4, 0.9, 0.8])
    metrics = calculate_model_metrics(y_true, y_prob, threshold=0.5)
    assert metrics["confusion_matrix"] == {"tn": 1, "fp": 1, "fn": 1, "tp": 2}
    assert metrics["precision"] == 2 / 3
    assert metrics["recall"] == 2 / 3


def test_threshold_analysis_returns_rows_for_each_threshold():
    y_true = np.array([0, 1, 0, 1])
    y_prob = np.array([0.1, 0.9, 0.3, 0.8])
    df = threshold_analysis(y_true, y_prob, candidate_thresholds=[0.5, 0.7])
    assert len(df) == 2
    assert set(df["threshold"].tolist()) == {0.5, 0.7}

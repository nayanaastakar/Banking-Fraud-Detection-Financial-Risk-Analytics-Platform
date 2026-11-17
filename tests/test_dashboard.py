from __future__ import annotations

import io
import json
import urllib.parse
from http.server import HTTPServer

import pytest

from finguard.dashboard.data_service import DashboardDataService, data_service
from finguard.dashboard.server import DashboardRequestHandler


def test_dashboard_data_service_kpis():
    kpis = data_service.get_summary_kpis(model="random_forest")
    assert "total_transactions" in kpis
    assert kpis["total_transactions"] >= 280000
    assert "fraud_count" in kpis
    assert kpis["fraud_count"] > 0
    assert "precision_pct" in kpis
    assert "recall_pct" in kpis
    assert "prevented_fraud_amount" in kpis


def test_dashboard_data_service_time_bands():
    bands = data_service.get_time_band_metrics()
    assert len(bands) >= 3
    band_names = [b["time_band"] for b in bands]
    assert "0-1h" in band_names
    assert "3h+" in band_names


def test_dashboard_data_service_amount_bands():
    bands = data_service.get_amount_band_metrics()
    assert len(bands) >= 5
    tier_names = [b["amount_band"] for b in bands]
    assert "0-10" in tier_names
    assert "1000+" in tier_names


def test_dashboard_data_service_confusion_matrix():
    matrix_data = data_service.get_confusion_matrix(model="random_forest")
    assert "matrix" in matrix_data
    m = matrix_data["matrix"]
    assert m["tp"] > 0
    assert m["tn"] > 0
    assert "rates" in matrix_data
    assert matrix_data["rates"]["accuracy"] > 95.0


def test_dashboard_data_service_threshold_tradeoff():
    curve = data_service.get_threshold_tradeoff(model="random_forest")
    assert len(curve) >= 5
    first_pt = curve[0]
    assert "threshold" in first_pt
    assert "precision" in first_pt
    assert "recall" in first_pt
    assert "net_benefit" in first_pt


def test_dashboard_data_service_simulation():
    sim = data_service.simulate_threshold(model="random_forest", threshold=0.70, investigation_cost=15.0)
    assert sim["threshold"] == 0.70
    assert sim["true_positives"] > 0
    assert sim["net_financial_benefit"] > 0


def test_dashboard_data_service_features():
    features = data_service.get_feature_importance()
    assert len(features) >= 5
    f_names = [f["feature"] for f in features]
    assert "V14" in f_names
    assert "V10" in f_names


def test_dashboard_data_service_transactions():
    res = data_service.get_transactions(page=1, limit=10, model="random_forest")
    assert "records" in res
    assert "pagination" in res
    assert len(res["records"]) <= 10
    assert res["pagination"]["total_records"] > 0

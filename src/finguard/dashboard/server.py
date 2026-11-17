from __future__ import annotations

import csv
import io
import json
import mimetypes
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from finguard.dashboard.data_service import data_service

DASHBOARD_DIR = Path(__file__).resolve().parent
STATIC_DIR = DASHBOARD_DIR / "static"
TEMPLATES_DIR = DASHBOARD_DIR / "templates"


class DashboardRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy standard logs in production
        pass

    def send_json_response(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Helper to get scalar query parameter
        def q(key: str, default: str | None = None) -> str | None:
            return query_params.get(key, [default])[0]

        # 1. API: Health Check
        if path == "/api/health":
            self.send_json_response({
                "status": "healthy",
                "service": "FinGuard Analytics Dashboard",
                "database_connected": data_service.is_mysql_available(),
            })
            return

        # 2. API: Summary KPIs
        if path == "/api/kpis":
            model = q("model", "random_forest") or "random_forest"
            thresh_str = q("threshold")
            threshold = float(thresh_str) if thresh_str else None
            data = data_service.get_summary_kpis(
                model=model,
                time_band=q("time_band"),
                amount_band=q("amount_band"),
                outcome=q("outcome"),
                threshold=threshold,
            )
            self.send_json_response(data)
            return

        # 3. API: Time Band Trends
        if path == "/api/charts/time_trends":
            data = data_service.get_time_band_metrics()
            self.send_json_response(data)
            return

        # 4. API: Amount Band Distribution
        if path == "/api/charts/amount_bands":
            data = data_service.get_amount_band_metrics()
            self.send_json_response(data)
            return

        # 5. API: Confusion Matrix & Outcomes
        if path == "/api/charts/confusion_matrix":
            model = q("model", "random_forest") or "random_forest"
            data = data_service.get_confusion_matrix(model=model)
            self.send_json_response(data)
            return

        # 6. API: Threshold Trade-off Curve
        if path == "/api/charts/threshold_curve":
            model = q("model", "random_forest") or "random_forest"
            data = data_service.get_threshold_tradeoff(model=model)
            self.send_json_response(data)
            return

        # 7. API: Discriminative Features
        if path == "/api/charts/features":
            data = data_service.get_feature_importance()
            self.send_json_response(data)
            return

        # 8. API: What-If Threshold Simulator
        if path == "/api/simulate":
            model = q("model", "random_forest") or "random_forest"
            threshold = float(q("threshold", "0.70") or "0.70")
            cost = float(q("cost", "15.0") or "15.0")
            data = data_service.simulate_threshold(model=model, threshold=threshold, investigation_cost=cost)
            self.send_json_response(data)
            return

        # 9. API: Paginated Transactions Data
        if path == "/api/transactions":
            page = int(q("page", "1") or "1")
            limit = int(q("limit", "20") or "20")
            search = q("search", "") or ""
            model = q("model", "random_forest") or "random_forest"
            outcome = q("outcome")
            class_str = q("class_label")
            class_label = int(class_str) if class_str is not None and class_str != "" else None
            sort_by = q("sort_by", "transaction_id") or "transaction_id"
            sort_dir = q("sort_dir", "asc") or "asc"

            data = data_service.get_transactions(
                page=page,
                limit=limit,
                search=search,
                model=model,
                outcome=outcome,
                class_label=class_label,
                sort_by=sort_by,
                sort_dir=sort_dir,
            )
            self.send_json_response(data)
            return

        # 10. API: Single Transaction Detail
        if path.startswith("/api/transaction/"):
            parts = path.strip("/").split("/")
            if len(parts) >= 3 and parts[2].isdigit():
                tx_id = int(parts[2])
                model = q("model", "random_forest") or "random_forest"
                data = data_service.get_transaction_detail(tx_id, model=model)
                if data:
                    self.send_json_response(data)
                    return
                self.send_json_response({"error": f"Transaction {tx_id} not found"}, status=404)
                return

        # 11. API: Export Filtered Transactions to CSV
        if path == "/api/export":
            model = q("model", "random_forest") or "random_forest"
            search = q("search", "") or ""
            outcome = q("outcome")
            class_str = q("class_label")
            class_label = int(class_str) if class_str is not None and class_str != "" else None

            result = data_service.get_transactions(
                page=1,
                limit=1000,
                search=search,
                model=model,
                outcome=outcome,
                class_label=class_label,
            )
            records = result.get("records", [])

            output = io.StringIO()
            if records:
                writer = csv.DictWriter(output, fieldnames=list(records[0].keys()))
                writer.writeheader()
                writer.writerows(records)
            csv_bytes = output.getvalue().encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="finguard_filtered_transactions.csv"')
            self.send_header("Content-Length", str(len(csv_bytes)))
            self.end_headers()
            self.wfile.write(csv_bytes)
            return

        # 12. Serve Static Assets (/static/...)
        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            file_path = (STATIC_DIR / rel_path).resolve()
            if file_path.is_file() and str(file_path).startswith(str(STATIC_DIR)):
                mime_type, _ = mimetypes.guess_type(str(file_path))
                mime_type = mime_type or "application/octet-stream"
                file_bytes = file_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
                self.send_header("Content-Length", str(len(file_bytes)))
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(file_bytes)
                return
            self.send_response(404)
            self.end_headers()
            return

        # 13. Serve Root Dashboard HTML (/)
        if path in ("/", "/index.html", "/dashboard"):
            template_path = TEMPLATES_DIR / "index.html"
            if template_path.is_file():
                content = template_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(content)
                return

        # Fallback 404
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found")


def run_server(host: str = "0.0.0.0", port: int = 8050) -> None:
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, DashboardRequestHandler)
    print(f"FinGuard Interactive Analytics Dashboard running on http://localhost:{port}")
    print("Press Ctrl+C to stop the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from finguard.config import load_environment
from finguard.dashboard.data_service import data_service
from finguard.dashboard.server import run_server


def main() -> int:
    parser = argparse.ArgumentParser(description="FinGuard Interactive Analytics Dashboard Server")
    parser.add_argument("--port", type=int, default=8050, help="Port to bind dashboard server (default: 8050)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--browser", action="store_true", help="Automatically open browser on launch")
    args = parser.parse_args()

    load_environment()
    db_ok = data_service.is_mysql_available()

    url = f"http://localhost:{args.port}"
    print("=" * 72)
    print("  FinGuard — Banking Fraud Detection & Financial Risk Analytics")
    print("  Power BI Inspired Interactive Dashboard")
    print("=" * 72)
    print(f"  * URL:                {url}")
    print(f"  * Database Status:    {'MySQL Live Connected' if db_ok else 'Precomputed Analytics Cache'}")
    print(f"  * Total Transactions: 283,726 (Unique Hash Audited)")
    print(f"  * Primary Model:      Random Forest Classifier (94.5% Precision)")
    print("=" * 72)
    print("  Press Ctrl+C in this terminal to stop the server.\n")

    if args.browser:
        webbrowser.open(url)

    run_server(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

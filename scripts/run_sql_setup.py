from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from finguard.config import load_environment
from finguard.database import connect_mysql, load_mysql_env


def execute_sql_file(connection, file_path: Path, export_prefix: str | None = None, export_dir: Path | None = None) -> int:
    sql_text = file_path.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]

    cursor = connection.cursor()
    executed_count = 0

    for idx, stmt in enumerate(statements, start=1):
        clean_stmt = "\n".join(
            line for line in stmt.splitlines() if not line.strip().startswith("--")
        ).strip()
        if not clean_stmt:
            continue

        try:
            cursor.execute(clean_stmt)
            executed_count += 1
            if cursor.description and export_prefix and export_dir:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=columns)
                target_csv = export_dir / f"{export_prefix}_{idx}.csv"
                df.to_csv(target_csv, index=False)
        except Exception as exc:
            print(f"Error executing statement #{idx} from {file_path.name}: {exc}")

    connection.commit()
    cursor.close()
    return executed_count


def ensure_database_and_schema() -> None:
    load_environment()
    creds = load_mysql_env()

    import mysql.connector

    # Ensure database exists
    admin_conn = mysql.connector.connect(
        host=creds["host"],
        port=creds["port"],
        user=creds["user"],
        password=creds["password"],
    )
    admin_cur = admin_conn.cursor()
    db_file = PROJECT_ROOT / "sql" / "01_create_database.sql"
    if db_file.exists():
        for stmt in db_file.read_text(encoding="utf-8").split(";"):
            if stmt.strip():
                admin_cur.execute(stmt.strip())
    admin_conn.commit()
    admin_cur.close()
    admin_conn.close()

    # Connect to the target database
    conn = connect_mysql()

    # 1. Create tables
    tables_file = PROJECT_ROOT / "sql" / "02_create_tables.sql"
    if tables_file.exists():
        execute_sql_file(conn, tables_file)
        print("Schema tables verified.")

    # 2. Create analytical views
    views_file = PROJECT_ROOT / "sql" / "05_analytical_views.sql"
    if views_file.exists():
        execute_sql_file(conn, views_file)
        print("Analytical views verified.")

    # 3. Export analytical queries
    export_dir = PROJECT_ROOT / "reports" / "sql_exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    analytics_files = [
        ("04_data_quality_checks.sql", "04_data_quality_checks"),
        ("06_fraud_analysis.sql", "06_fraud_analysis"),
        ("07_risk_analysis.sql", "07_risk_analysis"),
        ("08_business_questions.sql", "08_business_questions"),
    ]

    for fname, prefix in analytics_files:
        fpath = PROJECT_ROOT / "sql" / fname
        if fpath.exists():
            n = execute_sql_file(conn, fpath, export_prefix=prefix, export_dir=export_dir)
            print(f"Executed {fname}: {n} queries processed, exported to {export_dir}")

    conn.close()
    print("MySQL database setup and analytics export completed successfully.")


def main() -> int:
    try:
        ensure_database_and_schema()
        return 0
    except Exception as exc:
        print(f"Failed to complete SQL setup: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import importlib
import os
import platform
import sys
from pathlib import Path


def check_module(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def main() -> int:
    print("FinGuard environment validation")
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")

    required = [
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "sklearn",
        "pytest",
        "yaml",
        "dotenv",
        "mysql",
    ]
    missing = [name for name in required if not check_module(name)]

    if missing:
        print("Missing modules: " + ", ".join(missing))
        return 1

    project_root = Path(__file__).resolve().parents[1]
    env_file = project_root / ".env"

    if env_file.exists():
        print("Local .env file detected.")
        import dotenv
        dotenv.load_dotenv(env_file)
    else:
        print("No local .env file detected.")

    env_password = os.getenv("DB_PASSWORD")
    placeholder_values = {"", "your_mysql_password", "your_mysql_user", "changeme", "password"}

    if env_password is None or not env_password.strip() or env_password.lower() in {v.lower() for v in placeholder_values if v}:
        print("MySQL credential check: local DB_PASSWORD is not configured for this machine.")
        print("Create a project-local .env file with valid DB_HOST, DB_PORT, DB_NAME, DB_USER and DB_PASSWORD values, or set them in the current environment.")
        print("Do not commit or share the password.")
        return 2

    print("MySQL credential check: local DB_PASSWORD is configured.")

    try:
        import mysql.connector
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "3306"))
        user = os.getenv("DB_USER", "root")
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=env_password,
            connection_timeout=5,
        )
        conn.close()
        print(f"MySQL server connection verified at {host}:{port}.")
    except Exception as exc:
        print(f"MySQL server connection warning: {exc}")

    print("All required Python modules are available.")
    print(f"Project root: {project_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

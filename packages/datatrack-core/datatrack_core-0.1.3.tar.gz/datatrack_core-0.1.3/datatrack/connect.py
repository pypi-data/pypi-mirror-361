import re
from pathlib import Path
from urllib.parse import urlparse

import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

# Config paths
CONFIG_DIR = Path(".datatrack")
DB_LINK_FILE = CONFIG_DIR / "db_link.yaml"


def get_connected_db_name():
    """
    Returns a safe, filesystem-friendly name for the connected database.

    - For SQLite: extracts the file name without extension.
    - For other SQL DBs: extracts the database name from URI.
    - Ensures the result is alphanumeric + underscores only.
    """
    if not DB_LINK_FILE.exists():
        raise ValueError("No database connection found. Please connect first.")

    with open(DB_LINK_FILE) as f:
        uri = yaml.safe_load(f).get("link", "")
        parsed = urlparse(uri)

        if parsed.scheme.startswith("sqlite"):
            db_path = Path(parsed.path).name  # example.db
            db_name = db_path.replace(".db", "")
        else:
            db_name = parsed.path.lstrip("/")

        # Sanitize db_name: keep alphanumerics, underscores, dashes
        safe_name = re.sub(r"[^\w\-]", "_", db_name)
        if not safe_name:
            raise ValueError("Could not determine a valid database name from URI.")

        return safe_name


def save_connection(link: str):
    """
    Connects to the given DB link only if no connection exists or it's disconnected.
    """
    if DB_LINK_FILE.exists():
        print("A database is already connected. Please disconnect first using:")
        print("  datatrack disconnect")
        return

    try:
        engine = create_engine(link)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # FIXED: wrapped with `text()`
    except OperationalError as e:
        if "Access denied" in str(e):
            print("Access denied: Please check your username or password.\n")
        elif "Can't connect to MySQL server" in str(e):
            print(
                "Could not connect to the server. Check if the DB is running and reachable.\n"
            )
        else:
            print(f"Operational error: {e}\n")
        return
    except SQLAlchemyError as e:
        if "No module named" in str(e):
            print(
                "Missing driver: Ensure required DB drivers (e.g., pymysql, psycopg2) are installed.\n"
            )
        else:
            print(f"Connection failed: {e}\n")
        return

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(DB_LINK_FILE, "w") as f:
        yaml.dump({"link": link}, f)

    print(f"Successfully connected and saved link: {link}")


def get_saved_connection():
    """
    Returns the stored connection string, or None if not found.
    """
    if DB_LINK_FILE.exists():
        with open(DB_LINK_FILE) as f:
            data = yaml.safe_load(f)
            return data.get("link")
    return None


def remove_connection():
    """
    Deletes the saved connection config.
    """
    if DB_LINK_FILE.exists():
        DB_LINK_FILE.unlink()
        print("Disconnected from database and removed stored link.")
    else:
        print("No active connection found.")

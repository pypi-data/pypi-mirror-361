from pathlib import Path
from urllib.parse import urlparse

import yaml
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError

# Config paths
CONFIG_DIR = Path(".datatrack")
DB_LINK_FILE = CONFIG_DIR / "db_link.yaml"


def get_connected_db_name():
    """
    Returns the currently connected database name from the stored connection URI.
    Raises informative errors if connection config is missing or invalid.
    """
    if not DB_LINK_FILE.exists():
        raise ValueError("No database connection found. Please connect first.")

    with open(DB_LINK_FILE) as f:
        uri = yaml.safe_load(f).get("link", "")
        db_name = urlparse(uri).path.lstrip("/")
        if not db_name:
            raise ValueError("Could not extract database name from URI.")
        return db_name


def save_connection(link: str):
    """
    Tries to connect to the given DB link, validates it, and saves it if successful.
    """
    try:
        engine = create_engine(link)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except OperationalError as e:
        if "Access denied" in str(e):
            print("Access denied: Please check your username or password.\n")
        elif "Can't connect to MySQL server" in str(e):
            print(
                "Could not connect to the server. Check if MySQL is running and reachable.\n"
            )
        else:
            print(f"Operational error: {e}\n")
        return
    except SQLAlchemyError as e:
        if "No module named" in str(e):
            print(
                "Missing driver: Please ensure required DB drivers (e.g., pymysql) are installed.\n"
            )
        else:
            print(f"Connection failed: {e}\n")
        return

    # Save the link
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

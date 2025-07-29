from datetime import datetime
from pathlib import Path

import yaml
from sqlalchemy import create_engine, inspect

from datatrack.connect import get_connected_db_name, get_saved_connection

EXPORT_BASE_DIR = Path(".databases/exports")


def save_schema_snapshot(schema: dict, db_name: str):
    """
    Save the given schema dict into a timestamped YAML file under .databases/exports/<db_name>/snapshots/
    """
    snapshot_dir = EXPORT_BASE_DIR / db_name / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_file = snapshot_dir / f"snapshot_{timestamp}.yaml"

    with open(snapshot_file, "w") as f:
        yaml.dump(schema, f)

    print(f"Snapshot saved at: {snapshot_file}")
    return snapshot_file


def snapshot(source: str = None):
    """
    Connect to the database (from saved link or given source) and extract schema details.
    Save the schema snapshot to a timestamped file under .databases/exports/<db_name>/snapshots/
    """
    if source is None:
        source = get_saved_connection()
        if not source:
            raise ValueError(
                "No DB source provided or saved. Run `datatrack connect` first."
            )

    db_name = get_connected_db_name()

    engine = create_engine(source)
    insp = inspect(engine)

    schema_data = {"tables": []}

    for table_name in insp.get_table_names():
        columns = insp.get_columns(table_name)
        schema_data["tables"].append(
            {
                "name": table_name,
                "columns": [
                    {"name": col["name"], "type": str(col["type"])} for col in columns
                ],
            }
        )

    file_path = save_schema_snapshot(schema_data, db_name)
    return file_path

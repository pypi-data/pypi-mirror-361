from pathlib import Path

import yaml

from datatrack.connect import get_connected_db_name


def print_history():
    try:
        db_name = get_connected_db_name()
    except Exception as e:
        print(f"Failed to resolve connected database: {e}")
        return

    snapshot_dir = Path(f".databases/exports/{db_name}/snapshots")
    if not snapshot_dir.exists():
        print(f"No snapshot directory found for database: `{db_name}`")
        return

    snapshots = sorted(snapshot_dir.glob("*.yaml"), reverse=True)
    if not snapshots:
        print(f"No snapshots found for `{db_name}`.")
        return

    print(f"\nSnapshot History for `{db_name}`:\n")
    print(f"{'Timestamp':<25} | {'Tables':<7} | Filename")
    print("-" * 60)

    for snap_file in snapshots:
        timestamp = snap_file.stem  # removes ".yaml"
        try:
            with open(snap_file) as f:
                snap_data = yaml.safe_load(f)
                table_count = len(snap_data.get("tables", []))
        except Exception:
            table_count = "ERR"

        print(f"{timestamp:<25} | {table_count:<7} | {snap_file.name}")

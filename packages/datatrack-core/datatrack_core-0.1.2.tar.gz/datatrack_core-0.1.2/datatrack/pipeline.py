import typer

from datatrack.connect import get_saved_connection
from datatrack.diff import diff_schemas, load_snapshots
from datatrack.exporter import export_diff, export_snapshot
from datatrack.linter import lint_schema
from datatrack.linter import load_latest_snapshot as load_lint_snapshot
from datatrack.tracker import snapshot
from datatrack.verifier import load_latest_snapshot as load_ver_snapshot
from datatrack.verifier import load_rules, verify_schema

app = typer.Typer()


@app.command("run")
def run_pipeline(
    export_dir: str = typer.Option(".pipeline_output", help="Where to save outputs"),
    verbose: bool = typer.Option(True, help="Print detailed output"),
):
    print("=" * 50)
    print("           Running DataTrack Pipeline")
    print("=" * 50)

    source = get_saved_connection()
    if not source:
        print("No saved DB connection found. Run `datatrack connect <db_uri>` first.")
        raise typer.Exit(code=1)

    # Snapshot
    print("\n[1] Taking snapshot...")
    try:
        snapshot(source)
        print("Snapshot saved successfully.")
    except Exception as e:
        print(f"Snapshot error: {e}")
        raise typer.Exit(code=1)

    # Linting
    print("\n[2] Linting schema...")
    try:
        linted = load_lint_snapshot()
        lint_warnings = lint_schema(linted)
        if lint_warnings:
            print("Warnings:")
            for warn in lint_warnings:
                print(f"  - {warn}")
            raise typer.Exit(code=1)
        else:
            print("No linting issues found.")
    except Exception as e:
        print(f"Error during linting: {e}")
        raise typer.Exit(code=1)

    # Verify
    print("\n[3] Verifying schema...")
    try:
        schema = load_ver_snapshot()
        rules = load_rules()
        violations = verify_schema(schema, rules)
        if violations:
            print("Verification failed:")
            for v in violations:
                print(f"  - {v}")
            raise typer.Exit(code=1)
        else:
            print("Schema verification passed.")
    except Exception as e:
        print(f"Verification error: {e}")
        raise typer.Exit(code=1)

    # Diff
    print("\n[4] Computing schema diff...")
    try:
        old, new = load_snapshots()
        diff_schemas(old, new)
    except Exception as e:
        print(f"Diff skipped: {e}")
        raise typer.Exit(code=1)

    # Export
    print("\n[5] Exporting snapshot and diff...")
    try:
        export_snapshot(fmt="json")
        export_diff(fmt="json")
        print("Exported to default directory: .databases/exports/")
    except Exception as e:
        print(f"Export failed: {e}")
        return

    print("\nPipeline completed successfully.")
    print("=" * 50)

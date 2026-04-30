"""Command-line interface for ML Experiment Tracker."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


RUNS_DIR = Path("runs")


def create_run(name: str) -> Path:
    """Create a run JSON file in the local runs directory."""
    RUNS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    safe_name = name.strip().replace(" ", "_")
    run_file = RUNS_DIR / f"{timestamp.replace(':', '-')}_{safe_name}.json"

    payload = {
        "name": name,
        "timestamp": timestamp,
        "metadata": {},
    }

    run_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return run_file


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(prog="mltracker")
    subparsers = parser.add_subparsers(dest="command")

    create_run_parser = subparsers.add_parser("create-run", help="Create an experiment run")
    create_run_parser.add_argument("--name", required=True, help="Run name")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "create-run":
        run_path = create_run(args.name)
        print(f"Created run: {run_path}")
    else:
        print("ML Experiment Tracker")


if __name__ == "__main__":
    main()

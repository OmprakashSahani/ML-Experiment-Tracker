"""Command-line interface for ML Experiment Tracker."""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path


RUNS_DIR = Path("runs")


def sanitize_run_name(name: str) -> str:
    """Sanitize a run name so it is safe to use as part of a filename."""
    normalized = name.strip().replace(" ", "_")
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", normalized)
    return safe_name or "run"


def create_run(name: str) -> Path:
    """Create a run JSON file in the local runs directory."""
    RUNS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    safe_name = sanitize_run_name(name)
    run_file = RUNS_DIR / f"{timestamp.replace(':', '-')}_{safe_name}.json"

    payload = {
        "name": name,
        "timestamp": timestamp,
        "metadata": {},
    }

    run_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return run_file


def log_metric(run_file: str, name: str, value: float) -> Path:
    """Log a metric value to an existing run JSON file."""
    run_path = Path(run_file)
    payload = json.loads(run_path.read_text(encoding="utf-8"))

    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        metrics = {}

    metric_value = float(value)
    if not math.isfinite(metric_value):
        raise ValueError(f"Metric '{name}' must be a finite number; got {metric_value!r}.")

    metrics[name] = metric_value
    payload["metrics"] = metrics

    run_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return run_path


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(prog="mltracker")
    subparsers = parser.add_subparsers(dest="command")

    create_run_parser = subparsers.add_parser("create-run", help="Create an experiment run")
    create_run_parser.add_argument("--name", required=True, help="Run name")

    log_metric_parser = subparsers.add_parser("log-metric", help="Log a metric to a run")
    log_metric_parser.add_argument("--run-file", required=True, help="Path to run JSON file")
    log_metric_parser.add_argument("--name", required=True, help="Metric name")
    log_metric_parser.add_argument("--value", required=True, type=float, help="Metric value")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "create-run":
        run_path = create_run(args.name)
        print(f"Created run: {run_path}")
    elif args.command == "log-metric":
        run_path = log_metric(args.run_file, args.name, args.value)
        print(f"Updated run: {run_path}")
    else:
        print("ML Experiment Tracker")


if __name__ == "__main__":
    main()

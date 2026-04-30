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


def list_runs() -> list[str]:
    """List run summaries from JSON files in the local runs directory."""
    if not RUNS_DIR.exists():
        return ["No runs found yet. Create one with: mltracker create-run --name <run-name>"]

    lines: list[str] = []
    run_files = sorted(RUNS_DIR.glob("*.json"))
    if not run_files:
        return ["No runs found in runs/."]

    for run_file in run_files:
        try:
            payload = json.loads(run_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            lines.append(
                f"WARNING: Skipping malformed run file '{run_file.name}': {exc.msg}"
            )
            continue

        run_name = payload.get("name", "(unnamed)")
        timestamp = payload.get("timestamp", "(missing timestamp)")
        metrics = payload.get("metrics")
        metric_keys = sorted(metrics.keys()) if isinstance(metrics, dict) and metrics else []
        metric_text = ", ".join(metric_keys) if metric_keys else "none"
        lines.append(f"- {run_name} | {timestamp} | metrics: {metric_text}")

    return lines


def compare_runs(run_files: list[str], metric: str | None = None) -> list[str]:
    """Compare metrics across one or more run JSON files."""
    rows: list[tuple[str, dict[str, object]]] = []
    all_metrics: set[str] = set()

    for run_file in run_files:
        run_path = Path(run_file)
        payload = json.loads(run_path.read_text(encoding="utf-8"))
        run_name = payload.get("name")
        if not isinstance(run_name, str) or not run_name:
            run_name = run_path.stem

        metrics = payload.get("metrics")
        metric_map = metrics if isinstance(metrics, dict) else {}
        all_metrics.update(k for k in metric_map.keys() if isinstance(k, str))
        rows.append((run_name, metric_map))

    metric_names = [metric] if metric else sorted(all_metrics)
    if not metric_names:
        return ["No metrics found across the provided run files."]

    lines: list[str] = []
    for run_name, metrics in rows:
        values: list[str] = []
        for metric_name in metric_names:
            if metric_name in metrics:
                values.append(f"{metric_name}={metrics[metric_name]}")
            else:
                values.append(f"{metric_name}=<missing>")
        lines.append(f"- {run_name} | " + ", ".join(values))

    return lines


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
    subparsers.add_parser("list-runs", help="List tracked runs")
    compare_runs_parser = subparsers.add_parser("compare-runs", help="Compare metrics across runs")
    compare_runs_parser.add_argument("run_files", nargs="+", help="Run JSON files to compare")
    compare_runs_parser.add_argument("--metric", help="Metric to compare")

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
    elif args.command == "list-runs":
        for line in list_runs():
            print(line)
    elif args.command == "compare-runs":
        for line in compare_runs(args.run_files, args.metric):
            print(line)
    else:
        print("ML Experiment Tracker")


if __name__ == "__main__":
    main()

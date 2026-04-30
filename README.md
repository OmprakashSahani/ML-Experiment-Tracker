# ML Experiment Tracker

A lightweight CLI experiment tracker for learning ML systems, reproducibility, and engineering workflows.

---

## Goal

Build a small system that can:

- Create experiment runs
- Log metrics
- Store experiment metadata
- Compare runs
- Practice production-style GitHub workflow

---

## Why This Project Matters

Experiment tracking is a core part of ML systems.

It helps answer:

- What configuration was used?
- What metrics were produced?
- Which run performed best?
- Can the result be reproduced?

---

## Planned Features

- CLI interface
- Local file-based storage
- Run creation
- Metric logging
- Run listing
- Run comparison
- Tests and CI

---

## Workflow

This project will follow:

```text
Issue → Branch → Code → Test → PR → CI → Merge → Release
```
---

## Completed Workflow 1: Initial Project Structure

### Issue
Created Issue #1 to initialize the project structure.

### Codex Usage
Used Codex to generate the initial project layout and tests.

### Files Added
- `pyproject.toml`
- `src/mltracker/__init__.py`
- `src/mltracker/cli.py`
- `tests/test_cli.py`

### Result
The project now has a clean `src/` structure with an initial CLI and test.


---

## Current CLI Commands

Use the CLI module directly from the repository root:

```bash
PYTHONPATH=src python -m mltracker.cli <command> [options]
```

### `create-run`

Creates a new run JSON file under `runs/`.

**Example command**

```bash
PYTHONPATH=src python -m mltracker.cli create-run --name "baseline-model"
```

**Expected output**

```text
Created run: runs/<UTC_TIMESTAMP>_baseline-model.json
```

### `log-metric`

Adds or updates a metric in an existing run JSON file.

**Example command**

```bash
PYTHONPATH=src python -m mltracker.cli log-metric   --run-file "runs/<UTC_TIMESTAMP>_baseline-model.json"   --name accuracy   --value 0.91
```

**Expected output**

```text
Updated run: runs/<UTC_TIMESTAMP>_baseline-model.json
```

## Usage

Follow this end-to-end workflow to track and compare experiments.

### 1) Create a run

```bash
mltracker create-run --name baseline
```

Example output:

```text
Created run: runs/20260430T120000Z_baseline.json
```

### 2) Log metrics

```bash
mltracker log-metric --run-file runs/<file>.json --name accuracy --value 0.95
```

Example output:

```text
Updated run: runs/20260430T120000Z_baseline.json
```

### 3) List runs

```bash
mltracker list-runs
```

Example output:

```text
runs/20260430T120000Z_baseline.json
runs/20260430T121500Z_tuned.json
```

### 4) Compare runs

```bash
mltracker compare-runs runs/<file1>.json runs/<file2>.json
```

Example output:

```text
Comparing runs:
- runs/20260430T120000Z_baseline.json
- runs/20260430T121500Z_tuned.json

Metrics:
accuracy: 0.95 vs 0.97
loss: 0.42 vs 0.36
```

```bash
mltracker compare-runs runs/<file1>.json runs/<file2>.json --metric accuracy
```

Example output:

```text
Comparing metric: accuracy
runs/20260430T120000Z_baseline.json: 0.95
runs/20260430T121500Z_tuned.json: 0.97
```

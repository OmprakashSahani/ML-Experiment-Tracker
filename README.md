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

## Installation

```bash
pip install -e .
```

Optional (development usage): use `python -m mltracker.cli` if not installed.

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
- baseline | 2026-04-30T12:00:00+00:00 | metrics: accuracy, loss
- tuned | 2026-04-30T12:15:00+00:00 | metrics: accuracy, loss
```

### 4) Compare runs

```bash
mltracker compare-runs runs/<file1>.json runs/<file2>.json
```

Example output:

```text
- baseline | accuracy=0.95, loss=0.42
- tuned | accuracy=0.97, loss=0.36
```

```bash
mltracker compare-runs runs/<file1>.json runs/<file2>.json --metric accuracy
```

Example output:

```text
- baseline | accuracy=0.95
- tuned | accuracy=0.97
```

<div align="center">

# ML Experiment Tracker
### CLI-based experiment tracking system for reproducible ML workflows, structured metric logging, and run comparison.

</div>

---

## Problem

As machine learning experiments scale, it becomes difficult to track configurations, compare results, and reproduce outcomes. Without structured tracking, valuable insights are often lost across runs.

This project builds a lightweight experiment tracking system from first principles to understand how reproducibility and evaluation workflows are handled in ML systems.

---

## Overview

This project implements a command-line tool for managing experiment runs, logging metrics, and comparing results using local JSON-based storage.

The focus is on simplicity, reproducibility, and engineering workflow design rather than model complexity.

---

## System Design

- CLI interface for experiment lifecycle management
- Timestamped run creation for reproducibility
- JSON-based storage for experiment metadata
- Structured metric logging
- Run comparison across experiments

---

## Workflow

The system follows a production-style workflow:

```text
Issue → Branch → Code → Test → PR → CI → Merge → Release
```

---

## Key Capabilities

- Create and manage experiment runs
- Log metrics (accuracy, loss, etc.)
- Store metadata in structured format
- Compare runs across configurations
- Enable reproducible experiment tracking

---

## Example Usage

### Create a run

```bash
mltracker create-run --name baseline
```

Output:

```text
Created run: runs/20260430T120000Z_baseline.json
```

---

### Log metrics

```bash
mltracker log-metric --run-file runs/<file>.json --name accuracy --value 0.95
```

---

### List runs

```bash
mltracker list-runs
```

Output:

```text
- baseline | 2026-04-30T12:00:00+00:00 | metrics: accuracy, loss
- tuned    | 2026-04-30T12:15:00+00:00 | metrics: accuracy, loss
```

---

### Compare runs

```bash
mltracker compare-runs runs/<file1>.json runs/<file2>.json
```

Output:

```text
- baseline | accuracy=0.95, loss=0.42
- tuned    | accuracy=0.97, loss=0.36
```

---

## Key Metrics & Observations

- Enabled reproducible experiment tracking through structured run storage
- Simplified comparison of model performance across runs
- Demonstrated improved accuracy and loss through configuration changes
- Reduced ambiguity in experiment evaluation by standardizing workflows

---

## System Insights

- Reproducibility requires structured experiment tracking and metadata
- CLI-based workflows simplify experiment management and automation
- Consistent logging enables reliable comparison across runs
- Even simple tracking systems significantly improve ML workflow clarity

---

## CLI Demo

![CLI Demo](docs/cli_demo.gif)

---

## Example Results

### Accuracy Comparison

![Accuracy Comparison](docs/accuracy_comparison.png)

Higher accuracy indicates improved model performance under comparable configurations.

---

## Project Structure

```text
mltracker/
  ├── cli.py
  └── storage.py

tests/
examples/
scripts/
results/
```

---

## Testing

```bash
pytest -q
```

---

## Tech Stack

- Python
- JSON (file-based storage)
- PyTest
- CLI (argparse)

---

<div align="center">

*Omprakash Sahani — Machine Learning Systems Engineer (Early Career)*

</div>
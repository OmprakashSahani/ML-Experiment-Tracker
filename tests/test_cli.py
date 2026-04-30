import json
from pathlib import Path

from mltracker.cli import main


def test_main_prints_banner(capsys):
    main([])
    captured = capsys.readouterr()
    assert captured.out.strip() == "ML Experiment Tracker"


def test_create_run_creates_json_file(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "baseline"])

    runs_dir = tmp_path / "runs"
    assert runs_dir.exists()

    run_files = list(runs_dir.glob("*.json"))
    assert len(run_files) == 1

    payload = json.loads(run_files[0].read_text(encoding="utf-8"))
    assert payload["name"] == "baseline"
    assert isinstance(payload["timestamp"], str)
    assert payload["metadata"] == {}

    captured = capsys.readouterr()
    assert "Created run:" in captured.out


def test_create_run_sanitizes_slashes_in_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "model/v1"])

    run_files = list((tmp_path / "runs").glob("*.json"))
    assert len(run_files) == 1
    assert "model_v1" in run_files[0].name

    payload = json.loads(run_files[0].read_text(encoding="utf-8"))
    assert payload["name"] == "model/v1"


def test_create_run_prevents_nested_path_creation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "team/model:v1?best"])

    runs_dir = tmp_path / "runs"
    assert runs_dir.exists()
    assert not (runs_dir / "team").exists()

    run_files = list(runs_dir.glob("*.json"))
    assert len(run_files) == 1
    assert "team_model_v1_best" in run_files[0].name


def test_log_metric_adds_metrics_object_and_preserves_fields(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "baseline"])
    run_file = list((tmp_path / "runs").glob("*.json"))[0]

    main(["log-metric", "--run-file", str(run_file), "--name", "accuracy", "--value", "0.95"])

    payload = json.loads(run_file.read_text(encoding="utf-8"))
    assert payload["name"] == "baseline"
    assert isinstance(payload["timestamp"], str)
    assert payload["metadata"] == {}
    assert payload["metrics"]["accuracy"] == 0.95
    assert isinstance(payload["metrics"]["accuracy"], float)

    captured = capsys.readouterr()
    assert "Updated run:" in captured.out


def test_log_metric_updates_existing_metric_value(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "baseline"])
    run_file = list((tmp_path / "runs").glob("*.json"))[0]

    main(["log-metric", "--run-file", str(run_file), "--name", "loss", "--value", "2.5"])
    main(["log-metric", "--run-file", str(run_file), "--name", "loss", "--value", "1.75"])

    payload = json.loads(run_file.read_text(encoding="utf-8"))
    assert payload["metrics"]["loss"] == 1.75

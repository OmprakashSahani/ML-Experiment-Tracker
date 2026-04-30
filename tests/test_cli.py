import json
from pathlib import Path

import pytest

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


@pytest.mark.parametrize("bad_value", ["nan", "inf", "-inf"])
def test_log_metric_rejects_non_finite_values(tmp_path, monkeypatch, bad_value):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "baseline"])
    run_file = list((tmp_path / "runs").glob("*.json"))[0]

    with pytest.raises(ValueError, match=r"must be a finite number"):
        main(["log-metric", "--run-file", str(run_file), "--name", "loss", f"--value={bad_value}"])

    payload = json.loads(run_file.read_text(encoding="utf-8"))
    assert "metrics" not in payload


def test_list_runs_handles_missing_runs_dir(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["list-runs"])

    captured = capsys.readouterr()
    assert "No runs found yet." in captured.out


def test_list_runs_displays_run_name_timestamp_and_metric_keys(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "baseline"])
    run_file = list((tmp_path / "runs").glob("*.json"))[0]
    main(["log-metric", "--run-file", str(run_file), "--name", "accuracy", "--value", "0.95"])
    main(["log-metric", "--run-file", str(run_file), "--name", "loss", "--value", "0.42"])

    capsys.readouterr()
    main(["list-runs"])

    output = capsys.readouterr().out
    assert "- baseline | " in output
    assert "metrics: accuracy, loss" in output

def test_list_runs_skips_malformed_json_and_shows_warning(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "valid-run"])
    runs_dir = tmp_path / "runs"
    malformed_file = runs_dir / "broken.json"
    malformed_file.write_text('{"name": "oops",', encoding="utf-8")

    capsys.readouterr()
    main(["list-runs"])

    output = capsys.readouterr().out
    assert "- valid-run | " in output
    assert "WARNING: Skipping malformed run file 'broken.json'" in output


def test_list_runs_continues_when_multiple_malformed_files_exist(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "run-a"])
    runs_dir = tmp_path / "runs"
    (runs_dir / "bad1.json").write_text('{"name":', encoding="utf-8")
    (runs_dir / "bad2.json").write_text('not-json', encoding="utf-8")

    capsys.readouterr()
    main(["list-runs"])

    output = capsys.readouterr().out
    assert "- run-a | " in output
    assert "WARNING: Skipping malformed run file 'bad1.json'" in output
    assert "WARNING: Skipping malformed run file 'bad2.json'" in output


def test_compare_runs_with_all_metrics_when_metric_not_provided(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "run-a"])
    run_a = list((tmp_path / "runs").glob("*.json"))[0]
    main(["log-metric", "--run-file", str(run_a), "--name", "accuracy", "--value", "0.9"])

    main(["create-run", "--name", "run-b"])
    run_b = sorted((tmp_path / "runs").glob("*.json"))[-1]
    main(["log-metric", "--run-file", str(run_b), "--name", "loss", "--value", "0.2"])

    capsys.readouterr()
    main(["compare-runs", str(run_a), str(run_b)])

    output = capsys.readouterr().out
    assert "- run-a | accuracy=0.9, loss=<missing>" in output
    assert "- run-b | accuracy=<missing>, loss=0.2" in output


def test_compare_runs_with_specific_metric_only(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "run-a"])
    run_a = list((tmp_path / "runs").glob("*.json"))[0]
    main(["log-metric", "--run-file", str(run_a), "--name", "accuracy", "--value", "0.9"])

    main(["create-run", "--name", "run-b"])
    run_b = sorted((tmp_path / "runs").glob("*.json"))[-1]

    capsys.readouterr()
    main(["compare-runs", str(run_a), str(run_b), "--metric", "accuracy"])

    output = capsys.readouterr().out
    assert "- run-a | accuracy=0.9" in output
    assert "- run-b | accuracy=<missing>" in output
    assert "loss=" not in output


def test_compare_runs_skips_malformed_json_and_shows_warning(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "valid-run"])
    valid_run = list((tmp_path / "runs").glob("*.json"))[0]
    main(["log-metric", "--run-file", str(valid_run), "--name", "accuracy", "--value", "0.88"])
    malformed_run = tmp_path / "runs" / "broken.json"
    malformed_run.write_text('{"name":"bad",', encoding="utf-8")

    capsys.readouterr()
    main(["compare-runs", str(valid_run), str(malformed_run)])

    output = capsys.readouterr().out
    assert "- valid-run | accuracy=0.88" in output
    assert "WARNING: Skipping malformed run file 'broken.json'" in output


def test_compare_runs_continues_with_multiple_malformed_files(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["create-run", "--name", "run-a"])
    run_a = list((tmp_path / "runs").glob("*.json"))[0]
    main(["log-metric", "--run-file", str(run_a), "--name", "accuracy", "--value", "0.9"])

    runs_dir = tmp_path / "runs"
    (runs_dir / "bad1.json").write_text("{", encoding="utf-8")
    (runs_dir / "bad2.json").write_text("not-json", encoding="utf-8")

    capsys.readouterr()
    main(["compare-runs", str(run_a), str(runs_dir / "bad1.json"), str(runs_dir / "bad2.json")])

    output = capsys.readouterr().out
    assert "- run-a | accuracy=0.9" in output
    assert "WARNING: Skipping malformed run file 'bad1.json'" in output
    assert "WARNING: Skipping malformed run file 'bad2.json'" in output

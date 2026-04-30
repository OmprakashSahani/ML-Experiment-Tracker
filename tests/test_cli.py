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

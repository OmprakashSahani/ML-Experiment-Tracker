from mltracker.cli import main


def test_main_prints_banner(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "ML Experiment Tracker"

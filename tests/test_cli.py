import sys
import pytest
from cli import main


def test_cli_version(monkeypatch, capsys):
    test_args = ["cli.py", "--version"]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "CloudPilot" in captured.out


def test_cli_invalid_command(monkeypatch, capsys):
    test_args = ["cli.py", "invalid_command"]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    # Check the error message in stderr instead of stdout.
    assert "usage:" in captured.err


def test_cli_scale(monkeypatch, capsys):
    test_args = [
        "cli.py",
        "scale",
        "--cpu",
        "80",
        "--mem",
        "70",
        "--req",
        "0.8",
        "--latency",
        "100",
        "--demand",
        "0.9",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    main()
    captured = capsys.readouterr()
    assert "Scaling Recommendation:" in captured.out

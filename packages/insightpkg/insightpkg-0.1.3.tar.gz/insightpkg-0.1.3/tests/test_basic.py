# tests/test_basic.py
from insightpkg.cli import main

def test_main_runs_without_crash(monkeypatch):
    import sys
    monkeypatch.setattr(sys, "argv", ["insightpkg", "requests"])
    try:
        main()
    except SystemExit:
        pass  # Allow main() to call sys.exit()

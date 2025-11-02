from main import main
from pathlib import Path

def test_pipeline_integration(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main()
    # Vérifie création fichiers export
    exports = list(Path(".").glob("exports/*"))
    assert any(p.suffix == ".json" for p in exports)
    assert any(p.suffix == ".csv" for p in exports)

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_doctor_module():
    repo_root = Path(__file__).resolve().parents[2]
    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    module_path = scripts_dir / "doctor.py"
    spec = spec_from_file_location("doctor", module_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_heartbeat_state_detects_empty_and_configured(tmp_path: Path) -> None:
    module = _load_doctor_module()
    hb = tmp_path / "HEARTBEAT.md"
    hb.write_text(
        "# Heartbeat Tasks\n\n## Active Tasks\n\n<!-- Add your periodic tasks below this line -->\n",
        encoding="utf-8",
    )
    assert module._heartbeat_state(hb) == "empty"

    hb.write_text(
        "# Heartbeat Tasks\n\n## Active Tasks\n\n- 每天提醒我复盘\n",
        encoding="utf-8",
    )
    assert module._heartbeat_state(hb) == "configured"


def test_check_json_file_reports_missing_and_invalid(tmp_path: Path) -> None:
    module = _load_doctor_module()
    missing = tmp_path / "missing.json"
    invalid = tmp_path / "bad.json"
    invalid.write_text("{bad", encoding="utf-8")

    assert module._check_json_file(missing) == (False, "missing")
    ok, message = module._check_json_file(invalid)
    assert ok is False
    assert message.startswith("invalid json:")

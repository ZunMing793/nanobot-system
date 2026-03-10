import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_smoke_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "smoke_test_bot.py"
    spec = spec_from_file_location("smoke_test_bot", module_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_detect_text_issues_flags_replacement_and_mojibake_markers() -> None:
    module = _load_smoke_module()

    issues = module._detect_text_issues("正常文本\ufffd还有鈥异常")

    assert "replacement-char" in issues
    assert any(item.startswith("mojibake:") for item in issues)


def test_resolve_config_path_supports_relative_and_absolute(tmp_path: Path) -> None:
    module = _load_smoke_module()

    relative = module._resolve_config_path(tmp_path, Path("./workspace"))
    absolute = module._resolve_config_path(tmp_path, (tmp_path / "shared").resolve())

    assert relative == (tmp_path / "workspace").resolve()
    assert absolute == (tmp_path / "shared").resolve()

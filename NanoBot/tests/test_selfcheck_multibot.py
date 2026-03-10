import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace


def _load_selfcheck_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "selfcheck_multibot.py"
    spec = spec_from_file_location("selfcheck_multibot", module_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_missing_items_reports_only_missing(tmp_path: Path) -> None:
    module = _load_selfcheck_module()
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "ok.txt").write_text("ok", encoding="utf-8")

    missing = module._missing_items(tmp_path / "a", ["ok.txt", "missing.txt"])

    assert missing == ["missing.txt"]


def test_resolve_workspace_dir_uses_agent_default_workspace(tmp_path: Path) -> None:
    module = _load_selfcheck_module()
    cfg = SimpleNamespace(agents=SimpleNamespace(defaults=SimpleNamespace(workspace="./data/workspace")))

    workspace = module._resolve_workspace_dir(tmp_path, cfg)

    assert workspace == (tmp_path / "data" / "workspace").resolve()


def test_check_shared_layout_detects_missing_required_files(tmp_path: Path) -> None:
    module = _load_selfcheck_module()
    shared = tmp_path / "shared"
    shared.mkdir()

    missing = module._check_shared_layout(tmp_path)

    assert "memory/USER_PROFILE.md" in missing
    assert "learnings/SHARED.md" in missing
    assert "skills/" in missing


def test_check_shared_layout_passes_when_layout_complete(tmp_path: Path) -> None:
    module = _load_selfcheck_module()
    shared = tmp_path / "shared"
    for relative in module.SHARED_REQUIRED_FILES:
        path = shared / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    (shared / "skills").mkdir()

    missing = module._check_shared_layout(tmp_path)

    assert missing == []

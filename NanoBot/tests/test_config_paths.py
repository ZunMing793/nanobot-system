from pathlib import Path

from nanobot.config.loader import load_config


def test_load_config_resolves_relative_paths_from_config_file(tmp_path, monkeypatch):
    root = tmp_path / "deploy"
    bot_dir = root / "bot1_core"
    other_dir = tmp_path / "elsewhere"
    bot_dir.mkdir(parents=True)
    other_dir.mkdir()

    config_path = bot_dir / "config.json"
    config_path.write_text(
        """
        {
          "agents": {
            "defaults": {
              "workspace": "./workspace"
            }
          },
          "shared": {
            "skills_path": "../shared/skills",
            "memory_path": "../shared/memory",
            "learnings_path": "../shared/learnings"
          }
        }
        """,
        encoding="utf-8",
    )

    monkeypatch.chdir(other_dir)
    config = load_config(config_path)

    assert config.workspace_path == (bot_dir / "workspace").resolve()
    assert config.shared_skills_path == (root / "shared" / "skills").resolve()
    assert config.shared_memory_path == (root / "shared" / "memory").resolve()
    assert config.shared_learnings_path == (root / "shared" / "learnings").resolve()


def test_bind_config_path_preserves_absolute_paths(tmp_path):
    workspace = (tmp_path / "workspace").resolve()
    skills = (tmp_path / "shared" / "skills").resolve()

    config_path = tmp_path / "config.json"
    config_path.write_text(
        f"""
        {{
          "agents": {{
            "defaults": {{
              "workspace": "{workspace.as_posix()}"
            }}
          }},
          "shared": {{
            "skills_path": "{skills.as_posix()}"
          }}
        }}
        """,
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.workspace_path == workspace
    assert config.shared_skills_path == skills

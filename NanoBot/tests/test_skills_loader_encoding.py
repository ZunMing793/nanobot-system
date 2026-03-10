from pathlib import Path

from nanobot.agent.skills import SkillsLoader


def test_load_skill_guide_falls_back_to_gb18030(tmp_path):
    workspace = tmp_path / "workspace"
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "encoding-demo"
    skill_dir.mkdir(parents=True)
    workspace.mkdir()

    (skill_dir / "SKILL.md").write_text("---\nname: encoding-demo\n---\nbody", encoding="utf-8")
    (skill_dir / "GUIDE.md").write_bytes("中文指引".encode("gb18030"))

    loader = SkillsLoader(workspace=workspace, shared_skills_path=skills_dir)

    assert loader.load_skill_guide("encoding-demo") == "中文指引"


def test_load_skill_falls_back_to_utf8_replace_for_unknown_bytes(tmp_path):
    workspace = tmp_path / "workspace"
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "broken-demo"
    skill_dir.mkdir(parents=True)
    workspace.mkdir()

    (skill_dir / "SKILL.md").write_bytes(b"---\nname: broken-demo\n---\nabc\x80xyz")

    loader = SkillsLoader(workspace=workspace, shared_skills_path=skills_dir)

    assert "abc" in loader.load_skill("broken-demo")


def test_load_skill_rewrites_legacy_claude_skill_paths(tmp_path):
    workspace = tmp_path / "workspace"
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "agent-browser"
    skill_dir.mkdir(parents=True)
    workspace.mkdir()

    (skill_dir / "SKILL.md").write_text(
        "---\nname: agent-browser\n---\n`C:/Users/79345/.claude/skills/agent-browser/GUIDE.md`\n",
        encoding="utf-8",
    )

    loader = SkillsLoader(workspace=workspace, shared_skills_path=skills_dir)
    content = loader.load_skill("agent-browser")

    assert content is not None
    assert f"`{skills_dir.as_posix()}/agent-browser/GUIDE.md`" in content
    assert "C:/Users/79345/.claude/skills/agent-browser/GUIDE.md" not in content

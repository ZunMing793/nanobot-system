from nanobot.agent.loop import AgentLoop


def _mk_loop() -> AgentLoop:
    return AgentLoop.__new__(AgentLoop)


def test_infer_skills_from_tool_call_detects_skill_path() -> None:
    loop = _mk_loop()

    skills = loop._infer_skills_from_tool_call(
        "read_file",
        {"path": "/home/NanoBot/shared/skills/agent-browser/GUIDE.md"},
    )

    assert skills == ["agent-browser"]


def test_infer_skills_from_tool_call_detects_ab_wrapper() -> None:
    loop = _mk_loop()

    skills = loop._infer_skills_from_tool_call(
        "exec",
        {"command": 'ab open "https://mp.weixin.qq.com/s/abc"'},
    )

    assert skills == ["agent-browser"]


def test_prepend_usage_prefix_is_compact() -> None:
    loop = _mk_loop()

    content = loop._prepend_usage_prefix(
        "已完成读取。",
        ["read_file", "exec", "exec"],
        ["agent-browser", "agent-browser"],
    )

    assert content.startswith("已调用：")
    assert "skills：agent-browser" in content
    assert "tools：read_file、exec" in content
    assert "\n\n已完成读取。" in content

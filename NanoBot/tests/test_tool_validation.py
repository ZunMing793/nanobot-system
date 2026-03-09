import asyncio
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.agent.tools.filesystem import (
    EditFileTool,
    WriteFileTool,
    build_protected_document_paths,
)
from nanobot.agent.tools.registry import ToolRegistry
from nanobot.agent.tools.shell import ExecTool


class SampleTool(Tool):
    @property
    def name(self) -> str:
        return "sample"

    @property
    def description(self) -> str:
        return "sample tool"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 2},
                "count": {"type": "integer", "minimum": 1, "maximum": 10},
                "mode": {"type": "string", "enum": ["fast", "full"]},
                "meta": {
                    "type": "object",
                    "properties": {
                        "tag": {"type": "string"},
                        "flags": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["tag"],
                },
            },
            "required": ["query", "count"],
        }

    async def execute(self, **kwargs: Any) -> str:
        return "ok"


def test_validate_params_missing_required() -> None:
    tool = SampleTool()
    errors = tool.validate_params({"query": "hi"})
    assert "missing required count" in "; ".join(errors)


def test_validate_params_type_and_range() -> None:
    tool = SampleTool()
    errors = tool.validate_params({"query": "hi", "count": 0})
    assert any("count must be >= 1" in e for e in errors)

    errors = tool.validate_params({"query": "hi", "count": "2"})
    assert any("count should be integer" in e for e in errors)


def test_validate_params_enum_and_min_length() -> None:
    tool = SampleTool()
    errors = tool.validate_params({"query": "h", "count": 2, "mode": "slow"})
    assert any("query must be at least 2 chars" in e for e in errors)
    assert any("mode must be one of" in e for e in errors)


def test_validate_params_nested_object_and_array() -> None:
    tool = SampleTool()
    errors = tool.validate_params(
        {
            "query": "hi",
            "count": 2,
            "meta": {"flags": [1, "ok"]},
        }
    )
    assert any("missing required meta.tag" in e for e in errors)
    assert any("meta.flags[0] should be string" in e for e in errors)


def test_validate_params_ignores_unknown_fields() -> None:
    tool = SampleTool()
    errors = tool.validate_params({"query": "hi", "count": 2, "extra": "x"})
    assert errors == []


async def test_registry_returns_validation_error() -> None:
    reg = ToolRegistry()
    reg.register(SampleTool())
    result = await reg.execute("sample", {"query": "hi"})
    assert "Invalid parameters" in result


def test_exec_extract_absolute_paths_keeps_full_windows_path() -> None:
    cmd = r"type C:\user\workspace\txt"
    paths = ExecTool._extract_absolute_paths(cmd)
    assert paths == [r"C:\user\workspace\txt"]


def test_exec_extract_absolute_paths_ignores_relative_posix_segments() -> None:
    cmd = ".venv/bin/python script.py"
    paths = ExecTool._extract_absolute_paths(cmd)
    assert "/bin/python" not in paths


def test_exec_extract_absolute_paths_captures_posix_absolute_paths() -> None:
    cmd = "cat /tmp/data.txt > /tmp/out.txt"
    paths = ExecTool._extract_absolute_paths(cmd)
    assert "/tmp/data.txt" in paths
    assert "/tmp/out.txt" in paths


def test_write_file_blocks_protected_memory_documents(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    protected = build_protected_document_paths(workspace)
    tool = WriteFileTool(workspace=workspace, protected_paths=protected)

    result = asyncio.run(tool.execute("memory/MEMORY.md", "test"))

    assert "system-managed memory documents" in result
    assert not (workspace / "memory" / "MEMORY.md").exists()


def test_edit_file_blocks_protected_memory_documents(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    target = workspace / "user" / "PROFILE.md"
    target.parent.mkdir(parents=True)
    target.write_text("hello", encoding="utf-8")
    protected = build_protected_document_paths(workspace)
    tool = EditFileTool(workspace=workspace, protected_paths=protected)

    result = asyncio.run(tool.execute("user/PROFILE.md", "hello", "world"))

    assert "system-managed memory documents" in result
    assert target.read_text(encoding="utf-8") == "hello"


def test_exec_blocks_protected_memory_documents(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    protected = build_protected_document_paths(workspace)
    aliases = {str(path) for path in protected}
    aliases.add("memory/MEMORY.md")
    tool = ExecTool(working_dir=str(workspace), protected_paths=aliases)

    result = tool._guard_command("cat memory/MEMORY.md", str(workspace))

    assert result is not None
    assert "system-managed memory documents" in result



def test_registry_get_definitions_can_filter_tools() -> None:
    reg = ToolRegistry()
    reg.register(SampleTool())
    all_defs = reg.get_definitions()
    filtered_defs = reg.get_definitions(include_names={"sample"})
    missing_defs = reg.get_definitions(include_names={"missing"})

    assert len(all_defs) == 1
    assert len(filtered_defs) == 1
    assert filtered_defs[0]["function"]["name"] == "sample"
    assert missing_defs == []

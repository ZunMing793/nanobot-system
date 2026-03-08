"""Anthropic-compatible provider using the native /messages endpoint."""

from __future__ import annotations

import uuid
from typing import Any

import httpx

from nanobot.providers.base import LLMProvider, LLMResponse, ToolCallRequest


class AnthropicProvider(LLMProvider):
    """Anthropic-style provider backed by an API that exposes /messages."""

    def __init__(
        self,
        api_key: str = "",
        api_base: str | None = None,
        default_model: str = "claude-3-5-sonnet-20241022",
    ):
        super().__init__(api_key, api_base)
        self.default_model = default_model
        self._client = httpx.AsyncClient(
            base_url=(api_base or "").rstrip("/"),
            headers={
                "Authorization": f"Bearer {api_key or 'no-key'}",
                "Content-Type": "application/json",
                "x-session-affinity": uuid.uuid4().hex,
            },
            timeout=60,
        )

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        reasoning_effort: str | None = None,
    ) -> LLMResponse:
        system, anthropic_messages = self._convert_messages(self._sanitize_empty_content(messages))
        payload: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": anthropic_messages,
            "max_tokens": max(1, max_tokens),
            "temperature": temperature,
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = self._convert_tools(tools)
        if reasoning_effort:
            payload["metadata"] = {"reasoning_effort": reasoning_effort}

        try:
            response = await self._client.post("/messages", json=payload)
            response.raise_for_status()
            return self._parse(response.json())
        except Exception as e:
            return LLMResponse(content=f"Error: {e}", finish_reason="error")

    @staticmethod
    def _convert_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        converted = []
        for tool in tools:
            func = tool.get("function", {})
            converted.append(
                {
                    "name": func.get("name", "tool"),
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {"type": "object", "properties": {}}),
                }
            )
        return converted

    def _convert_messages(self, messages: list[dict[str, Any]]) -> tuple[str | None, list[dict[str, Any]]]:
        system_parts: list[str] = []
        converted: list[dict[str, Any]] = []

        for message in messages:
            role = message.get("role")
            if role == "system":
                text = self._content_to_text(message.get("content"))
                if text:
                    system_parts.append(text)
                continue

            if role == "tool":
                converted.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": message.get("tool_call_id", "tool-call"),
                                "content": self._content_to_text(message.get("content")),
                            }
                        ],
                    }
                )
                continue

            if role == "assistant":
                content_blocks = self._to_anthropic_content(message.get("content"))
                for tool_call in message.get("tool_calls") or []:
                    fn = tool_call.get("function", {})
                    content_blocks.append(
                        {
                            "type": "tool_use",
                            "id": tool_call.get("id", fn.get("name", "tool-call")),
                            "name": fn.get("name", "tool"),
                            "input": self._parse_tool_arguments(fn.get("arguments")),
                        }
                    )
                converted.append({"role": "assistant", "content": content_blocks or [{"type": "text", "text": ""}]})
                continue

            converted.append({"role": "user", "content": self._to_anthropic_content(message.get("content"))})

        return ("\n\n".join(system_parts) if system_parts else None, self._merge_messages(converted))

    @staticmethod
    def _parse_tool_arguments(arguments: Any) -> dict[str, Any]:
        if isinstance(arguments, dict):
            return arguments
        if isinstance(arguments, str):
            try:
                import json_repair

                parsed = json_repair.loads(arguments)
                return parsed if isinstance(parsed, dict) else {"value": parsed}
            except Exception:
                return {"raw": arguments}
        return {}

    @staticmethod
    def _content_to_text(content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") in {"text", "input_text", "output_text"}:
                        parts.append(item.get("text", ""))
                    elif item.get("type") == "image_url":
                        parts.append("[image]")
                else:
                    parts.append(str(item))
            return "\n".join(part for part in parts if part)
        if isinstance(content, dict):
            return str(content.get("text", content))
        return str(content)

    def _to_anthropic_content(self, content: Any) -> list[dict[str, Any]]:
        if content is None:
            return [{"type": "text", "text": ""}]
        if isinstance(content, str):
            return [{"type": "text", "text": content}]
        if isinstance(content, dict):
            return [{"type": "text", "text": self._content_to_text(content)}]

        blocks: list[dict[str, Any]] = []
        for item in content:
            if not isinstance(item, dict):
                blocks.append({"type": "text", "text": str(item)})
                continue

            item_type = item.get("type")
            if item_type in {"text", "input_text", "output_text"}:
                blocks.append({"type": "text", "text": item.get("text", "")})
                continue
            if item_type == "image_url":
                image = item.get("image_url", {})
                url = image.get("url", "")
                if url.startswith("data:") and ";base64," in url:
                    mime, data = url[5:].split(";base64,", 1)
                    media_type = mime or "image/png"
                    blocks.append(
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": media_type, "data": data},
                        }
                    )
                    continue
            blocks.append({"type": "text", "text": self._content_to_text(item)})

        return blocks or [{"type": "text", "text": ""}]

    @staticmethod
    def _merge_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for message in messages:
            if merged and merged[-1]["role"] == message["role"]:
                merged[-1]["content"].extend(message["content"])
            else:
                merged.append({"role": message["role"], "content": list(message["content"])})
        return merged

    @staticmethod
    def _parse(response: dict[str, Any]) -> LLMResponse:
        content_blocks = response.get("content") or []
        text_parts: list[str] = []
        tool_calls: list[ToolCallRequest] = []
        thinking_blocks: list[dict[str, Any]] = []

        for block in content_blocks:
            block_type = block.get("type")
            if block_type == "text":
                text_parts.append(block.get("text", ""))
            elif block_type == "tool_use":
                tool_calls.append(
                    ToolCallRequest(
                        id=block.get("id", block.get("name", "tool-call")),
                        name=block.get("name", "tool"),
                        arguments=block.get("input", {}),
                    )
                )
            elif block_type in {"thinking", "redacted_thinking"}:
                thinking_blocks.append(block)

        usage = response.get("usage") or {}
        normalized_usage = {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        }

        return LLMResponse(
            content="\n".join(part for part in text_parts if part) or None,
            tool_calls=tool_calls,
            finish_reason=response.get("stop_reason") or "stop",
            usage=normalized_usage,
            thinking_blocks=thinking_blocks or None,
        )

    async def close(self) -> None:
        await self._client.aclose()

    def get_default_model(self) -> str:
        return self.default_model

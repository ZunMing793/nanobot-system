import asyncio

from nanobot.providers.base import LLMResponse, LLMProvider
from nanobot.providers.fallback_provider import FallbackProvider, FallbackTarget


class _StubProvider(LLMProvider):
    def __init__(self, responses):
        super().__init__(None, None)
        self.responses = list(responses)
        self.calls = []

    async def chat(self, messages, tools=None, model=None, max_tokens=4096, temperature=0.7, reasoning_effort=None):
        self.calls.append(model)
        return self.responses.pop(0)

    def get_default_model(self) -> str:
        return "stub"


def test_fallback_provider_uses_backup_on_error():
    primary = _StubProvider([LLMResponse(content="Error: primary down", finish_reason="error")])
    backup = _StubProvider([LLMResponse(content="ok from backup", finish_reason="stop")])
    provider = FallbackProvider(
        primary=FallbackTarget(model="glm-5", provider=primary, label="glm-5"),
        fallbacks=[FallbackTarget(model="kimi-k2-0905", provider=backup, label="kimi-k2")],
    )

    response = asyncio.run(provider.chat(messages=[{"role": "user", "content": "hi"}]))

    assert response.content == "ok from backup"
    assert primary.calls == ["glm-5"]
    assert backup.calls == ["kimi-k2-0905"]


def test_fallback_provider_skips_backup_for_explicit_other_model():
    primary = _StubProvider([LLMResponse(content="direct ok", finish_reason="stop")])
    backup = _StubProvider([LLMResponse(content="unused", finish_reason="stop")])
    provider = FallbackProvider(
        primary=FallbackTarget(model="glm-5", provider=primary, label="glm-5"),
        fallbacks=[FallbackTarget(model="kimi-k2-0905", provider=backup, label="kimi-k2")],
    )

    response = asyncio.run(provider.chat(messages=[{"role": "user", "content": "hi"}], model="custom-model"))

    assert response.content == "direct ok"
    assert primary.calls == ["custom-model"]
    assert backup.calls == []

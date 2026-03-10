"""Provider wrapper that retries with backup models when the primary model fails."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger

from nanobot.providers.base import LLMProvider, LLMResponse


@dataclass
class FallbackTarget:
    model: str
    provider: LLMProvider
    label: str


class FallbackProvider(LLMProvider):
    """Wrap multiple providers/models and try them in order on hard failures."""

    def __init__(self, primary: FallbackTarget, fallbacks: list[FallbackTarget]):
        super().__init__(api_key=None, api_base=None)
        self.primary = primary
        self.fallbacks = fallbacks
        self.default_model = primary.model

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        reasoning_effort: str | None = None,
    ) -> LLMResponse:
        requested_model = model or self.default_model
        if requested_model != self.default_model:
            return await self.primary.provider.chat(
                messages=messages,
                tools=tools,
                model=requested_model,
                max_tokens=max_tokens,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
            )

        last_response: LLMResponse | None = None
        for index, target in enumerate([self.primary, *self.fallbacks]):
            response = await target.provider.chat(
                messages=messages,
                tools=tools,
                model=target.model,
                max_tokens=max_tokens,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
            )
            if not self._should_fallback(response):
                if index > 0:
                    logger.warning(
                        "Model fallback activated: {} -> {}",
                        self.primary.label,
                        target.label,
                    )
                return response
            last_response = response
            logger.warning("Model {} failed, trying next fallback if available", target.label)

        return last_response or LLMResponse(content="Error: no fallback providers configured", finish_reason="error")

    @staticmethod
    def _should_fallback(response: LLMResponse) -> bool:
        if response.finish_reason == "error":
            return True
        content = (response.content or "").strip().lower()
        return content.startswith("error:")

    def get_default_model(self) -> str:
        return self.default_model

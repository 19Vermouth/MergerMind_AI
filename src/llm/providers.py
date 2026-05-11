import os
import json
import logging
from typing import Any
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens_used: int | None = None
    latency_ms: int | None = None


class BaseLLMProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        raise NotImplementedError

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()


class GroqProvider(BaseLLMProvider):
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        import time
        start = time.monotonic()

        client = await self._get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }

        try:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            latency = int((time.monotonic() - start) * 1000)

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider="groq",
                model=self.model,
                tokens_used=data.get("usage", {}).get("total_tokens"),
                latency_ms=latency,
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Groq API error: {e.response.status_code} — {e.response.text}")
            raise


class OpenRouterProvider(BaseLLMProvider):
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        import time
        start = time.monotonic()

        client = await self._get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://dealsense.ai",
            "X-Title": "DealSense AI",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }

        try:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            latency = int((time.monotonic() - start) * 1000)

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider="openrouter",
                model=self.model,
                tokens_used=data.get("usage", {}).get("total_tokens"),
                latency_ms=latency,
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e.response.status_code}")
            raise


class GeminiProvider(BaseLLMProvider):
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        import time
        start = time.monotonic()

        client = await self._get_client()
        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.3),
                "maxOutputTokens": kwargs.get("max_tokens", 2000),
            },
        }

        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            latency = int((time.monotonic() - start) * 1000)

            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return LLMResponse(
                content=content,
                provider="gemini",
                model=self.model,
                latency_ms=latency,
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API error: {e.response.status_code}")
            raise


class LLMManager:
    def __init__(self) -> None:
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.providers: dict[str, BaseLLMProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        if self.groq_key:
            self.providers["groq"] = GroqProvider(self.groq_key, "llama-3.3-70b-versatile")
        if self.openrouter_key:
            self.providers["openrouter"] = OpenRouterProvider(
                self.openrouter_key, "anthropic/claude-3.5-sonnet"
            )
        if self.gemini_key:
            self.providers["gemini"] = GeminiProvider(
                self.gemini_key, "gemini-2.0-flash"
            )

    async def generate(self, prompt: str, provider: str | None = None, **kwargs) -> LLMResponse:
        if provider and provider in self.providers:
            return await self.providers[provider].generate(prompt, **kwargs)

        for p_name, p_instance in self.providers.items():
            try:
                logger.info(f"Attempting LLM provider: {p_name}")
                return await p_instance.generate(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"{p_name} failed: {e}, trying next...")
                continue

        raise RuntimeError("All LLM providers failed")
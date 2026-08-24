"""Minimal OpenAI-compatible JSON chat client (NVIDIA NIM / DeepSeek)."""
from __future__ import annotations

import json

import httpx

from app.config import settings
from app.core.errors import UpstreamError


class LLMClient:
    def __init__(
        self, base_url: str, api_key: str, model: str, timeout: float = 180.0
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def chat_json(
        self, system: str, user: str, *, max_tokens: int | None = None
    ) -> dict:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": max_tokens or settings.llm_max_output_tokens,
            # NVIDIA NIM reasoning models hang on non-streaming completions.
            "stream": True,
        }
        try:
            content = await self._stream_completion(url, headers, body)
            if content is None:
                # Some providers reject response_format — retry once without it.
                body.pop("response_format", None)
                content = await self._stream_completion(url, headers, body)
        except httpx.HTTPError as e:
            raise UpstreamError(f"LLM request failed: {e}") from e

        if content is None:
            raise UpstreamError("LLM returned empty response")

        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError):
            pass

        # Tolerate leading reasoning text / fences: extract the JSON object.
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except (json.JSONDecodeError, TypeError):
                pass
        raise UpstreamError("LLM returned invalid JSON") from None

    async def _stream_completion(
        self, url: str, headers: dict, body: dict
    ) -> str | None:
        """Consume an SSE chat completion; returns assistant content or None on 4xx."""
        parts: list[str] = []
        client = self._get_client()
        async with client.stream("POST", url, headers=headers, json=body) as resp:
            if resp.status_code >= 400:
                raw = (await resp.aread()).decode(errors="replace")
                if "response_format" in raw:
                    return None
                raise UpstreamError(
                    f"LLM error {resp.status_code}: {raw[:300]}"
                )
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[len("data:") :].strip()
                if not data or data == "[DONE]":
                    if data == "[DONE]":
                        break
                    continue
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = payload.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                piece = delta.get("content")
                if isinstance(piece, str):
                    parts.append(piece)
        return "".join(parts)


llm_client = LLMClient(
    settings.llm_base_url, settings.llm_api_key, settings.llm_model
)

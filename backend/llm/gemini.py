import json
import logging
import httpx

from backend.llm.base import LLMProvider

logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(self, prompt: str, system: str = "") -> str:
        parts = []
        if system:
            parts.append({"text": system})
        parts.append({"text": prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048,
            },
        }

        resp = await self.client.post(
            GEMINI_URL,
            params={"key": self.api_key},
            json=payload,
        )

        if resp.status_code != 200:
            logger.error(f"Gemini API error: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Gemini API returned {resp.status_code}")

        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Gemini response structure: {data}")
            raise RuntimeError("Could not parse Gemini response") from e

    async def generate_json(self, prompt: str, system: str = "") -> dict:
        # tell the model we want json back
        json_system = (system + "\n" if system else "") + "Respond with valid JSON only. No markdown, no explanation."
        raw = await self.generate(prompt, json_system)

        # sometimes the model wraps it in ```json ... ```
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # drop first and last lines (the ``` markers)
            cleaned = "\n".join(lines[1:-1])

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM output as JSON: {cleaned[:200]}")
            raise ValueError(f"LLM returned invalid JSON")
# rate limit: 1000 RPD for gemini free tier

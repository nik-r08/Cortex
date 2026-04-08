import json
import logging
import httpx

from backend.llm.base import LLMProvider

logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=60.0)

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
            body = resp.text[:500]
            logger.error(f"Gemini API error {resp.status_code}: {body}")
            raise RuntimeError(f"Gemini API returned {resp.status_code}: {body}")

        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Gemini response: {json.dumps(data)[:500]}")
            raise RuntimeError("Could not parse Gemini response") from e

    async def generate_json(self, prompt: str, system: str = "") -> dict:
        json_system = (system + "\n" if system else "") + "Respond with valid JSON only. No markdown, no explanation."
        raw = await self.generate(prompt, json_system)

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM JSON: {cleaned[:300]}")
            raise ValueError(f"LLM returned invalid JSON")

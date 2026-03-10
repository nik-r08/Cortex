import json
import logging
import httpx

from backend.llm.base import LLMProvider

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(self, prompt: str, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = await self.client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 2048,
            },
        )

        if resp.status_code != 200:
            logger.error(f"Groq API error: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Groq API returned {resp.status_code}")

        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def generate_json(self, prompt: str, system: str = "") -> dict:
        json_system = (system + "\n" if system else "") + "Respond with valid JSON only. No markdown."
        raw = await self.generate(prompt, json_system)

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(f"Groq returned invalid JSON: {cleaned[:200]}")
            raise ValueError("LLM returned invalid JSON")
# rate limit: 30 RPM for groq free tier

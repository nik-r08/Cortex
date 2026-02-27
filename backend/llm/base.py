from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for LLM providers. Swap implementations without touching business logic."""

    @abstractmethod
    async def generate(self, prompt: str, system: str = "") -> str:
        ...

    @abstractmethod
    async def generate_json(self, prompt: str, system: str = "") -> dict:
        """Same as generate but parse the response as JSON."""
        ...

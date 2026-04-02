from typing import TYPE_CHECKING

from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.core.config import settings

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class LLMFactory:
    """Factory for creating LLM instances based on configured provider."""

    @staticmethod
    def create(provider: str | None = None, **kwargs) -> "BaseChatModel":
        """Create a chat model instance for the given provider.

        Args:
            provider: One of "openai", "groq", "claude". Defaults to settings.llm_provider.
            **kwargs: Additional arguments passed to the chat model constructor.

        Returns:
            A BaseChatModel instance.

        Raises:
            ValueError: If the provider is unknown.
        """
        provider = (provider or settings.llm_provider).lower()

        if provider == "openai":
            return ChatOpenAI(
                api_key=kwargs.pop("api_key", settings.openai_api_key or None),
                model=kwargs.pop("model", settings.openai_model),
                **kwargs,
            )
        elif provider == "groq":
            return ChatGroq(
                api_key=kwargs.pop("api_key", settings.groq_api_key or None),
                model=kwargs.pop("model", settings.groq_model),
                **kwargs,
            )
        elif provider == "claude":
            return ChatAnthropic(
                api_key=kwargs.pop("api_key", settings.anthropic_api_key or None),
                model=kwargs.pop("model", settings.claude_model),
                **kwargs,
            )
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider!r}. "
                "Supported: openai, groq, claude."
            )

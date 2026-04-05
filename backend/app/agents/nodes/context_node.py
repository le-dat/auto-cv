"""Context node — loads knowledge docs and dynamic context."""

import logging
from pathlib import Path
from typing import Any

from langchain_core.language_models import BaseChatModel

from app.core.config import settings


class ContextNode:
    """Node responsible for gathering context from various sources."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def run(self, state: dict) -> dict[str, Any]:
        """Load context from configured providers."""
        context_chunks: list[str] = []
        errors: list[str] = []
        updates: dict[str, Any] = {}

        providers = settings.context_providers

        # Load Markdown knowledge docs
        if "markdown" in providers:
            try:
                chunks = await self._load_markdown_docs()
                context_chunks.extend(chunks)
            except Exception as e:
                errors.append(f"Markdown context error: {str(e)}")

        # Load FAISS context (TODO: implement FAISS integration)
        if "faiss" in providers:
            try:
                chunks = await self._load_faiss_context(state)
                context_chunks.extend(chunks)
            except Exception as e:
                errors.append(f"FAISS context error: {str(e)}")

        # Load DB context (TODO: implement DB context)
        if "db" in providers and settings.db_context_enabled:
            try:
                chunks = await self._load_db_context(state)
                context_chunks.extend(chunks)
            except Exception as e:
                errors.append(f"DB context error: {str(e)}")

        # Load HTTP context (TODO: implement HTTP context)
        if "http" in providers and settings.http_context_url:
            try:
                chunks = await self._load_http_context(state)
                context_chunks.extend(chunks)
            except Exception as e:
                errors.append(f"HTTP context error: {str(e)}")

        updates["context_chunks"] = context_chunks

        if errors and not context_chunks:
            updates["error"] = "; ".join(errors)

        return updates

    async def _load_markdown_docs(self) -> list[str]:
        """Load all .md files from the knowledge directory."""
        chunks: list[str] = []
        knowledge_dir = settings.knowledge_dir

        # Resolve relative path from backend/app directory
        if not Path(knowledge_dir).is_absolute():
            base_dir = Path(__file__).parent.parent.parent.parent
            knowledge_dir = base_dir / knowledge_dir

        knowledge_path = Path(knowledge_dir)
        if not knowledge_path.exists():
            return chunks

        for filepath in sorted(knowledge_path.glob("*.md")):
            try:
                content = filepath.read_text(encoding="utf-8")
                chunks.append(f"knowledge:{filepath.name}\n{content}")
            except Exception as exc:
                logging.warning(f"Failed to read knowledge file {filepath.name}: {exc}")

        return chunks[: settings.knowledge_max_docs]

    async def _load_faiss_context(self, state: dict) -> list[str]:
        """Load context from FAISS vector store."""
        # TODO: Implement FAISS integration
        return []

    async def _load_db_context(self, state: dict) -> list[str]:
        """Load context from past successful rewrites in DB."""
        # TODO: Implement DB context
        return []

    async def _load_http_context(self, state: dict) -> list[str]:
        """Load context from external HTTP API."""
        # TODO: Implement HTTP context
        return []


def create_context_node(llm: BaseChatModel):
    """Factory to create a context node with the given LLM."""
    return ContextNode(llm)

"""Context node — loads knowledge docs and dynamic context."""

import os
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

        # Resolve relative path from backend directory
        if not os.path.isabs(knowledge_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            knowledge_dir = os.path.join(base_dir, knowledge_dir)

        if not os.path.exists(knowledge_dir):
            return chunks

        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(knowledge_dir, filename)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                        chunks.append(f"knowledge:{filename}\n{content}")
                except Exception:
                    pass

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

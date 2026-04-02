"""Context provider services."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class ContextProvider(ABC):
    """Abstract base for context providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging/debugging."""
        ...

    @abstractmethod
    async def get_context(self, query: str, top_k: int = 5) -> AsyncGenerator[str, None]:
        """Yield context chunks relevant to the query."""
        ...


class MarkdownDocProvider(ContextProvider):
    """Loads .md files from the knowledge directory."""

    def __init__(self, knowledge_dir: str, max_docs: int = 10):
        self.knowledge_dir = knowledge_dir
        self.max_docs = max_docs
        self._name = "markdown"

    @property
    def name(self) -> str:
        return self._name

    async def get_context(self, query: str, top_k: int = 5) -> AsyncGenerator[str, None]:
        """Yield markdown document contents."""
        import os

        if not os.path.exists(self.knowledge_dir):
            return

        files = sorted(os.listdir(self.knowledge_dir))[: self.max_docs]
        for filename in files:
            if filename.endswith(".md"):
                filepath = os.path.join(self.knowledge_dir, filename)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                        yield f"knowledge:{filename}\n{content}"
                except Exception:
                    pass


class FAISSContextProvider(ContextProvider):
    """Vector similarity search against FAISS index."""

    def __init__(self, index_path: str | None = None):
        self.index_path = index_path
        self._name = "faiss"

    @property
    def name(self) -> str:
        return self._name

    async def get_context(self, query: str, top_k: int = 5) -> AsyncGenerator[str, None]:
        """Search FAISS index and yield relevant chunks."""
        # TODO: Implement FAISS search
        return


class DBContextProvider(ContextProvider):
    """Retrieves context from past successful rewrites in PostgreSQL."""

    def __init__(self, repository=None):
        self.repository = repository
        self._name = "db"

    @property
    def name(self) -> str:
        return self._name

    async def get_context(self, query: str, top_k: int = 5) -> AsyncGenerator[str, None]:
        """Query DB for relevant past rewrites."""
        # TODO: Implement DB context retrieval
        return


class HTTPContextProvider(ContextProvider):
    """Fetches context from external HTTP API."""

    def __init__(self, url: str):
        self.url = url
        self._name = "http"

    @property
    def name(self) -> str:
        return self._name

    async def get_context(self, query: str, top_k: int = 5) -> AsyncGenerator[str, None]:
        """Call external API and yield context."""
        # TODO: Implement HTTP context retrieval
        return


# Factory function to create providers from config
def create_context_providers(config: dict) -> list[ContextProvider]:
    """Create context providers based on configuration."""
    providers = []
    # This would be called with settings values
    return providers

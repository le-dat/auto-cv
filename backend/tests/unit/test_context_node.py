"""Unit tests for context node."""

import pytest
from unittest.mock import patch, MagicMock

from app.agents.nodes.context_node import ContextNode, create_context_node


class TestContextNode:
    """Tests for ContextNode."""

    @pytest.fixture
    def node(self, mock_llm) -> ContextNode:
        return ContextNode(llm=mock_llm)

    @pytest.mark.asyncio
    async def test_run_returns_empty_chunks_when_no_providers(
        self, node: ContextNode
    ):
        with patch.object(node, "_load_markdown_docs", return_value=[]):
            with patch.object(node, "_load_faiss_context", return_value=[]):
                with patch("app.agents.nodes.context_node.settings") as mock_settings:
                    mock_settings.context_providers = []
                    updates = await node.run({})
                    assert updates.get("context_chunks") == []

    @pytest.mark.asyncio
    async def test_run_loads_markdown_docs(self, node: ContextNode):
        """Should load markdown docs when provider is enabled."""
        fake_chunks = ["knowledge:skills.md\n# Skills\nPython, FastAPI"]
        with patch.object(node, "_load_markdown_docs", return_value=fake_chunks):
            with patch("app.agents.nodes.context_node.settings") as mock_settings:
                mock_settings.context_providers = ["markdown"]
                mock_settings.db_context_enabled = False
                mock_settings.http_context_url = ""
                updates = await node.run({})
                assert updates["context_chunks"] == fake_chunks

    @pytest.mark.asyncio
    async def test_run_sets_error_when_all_providers_fail(
        self, node: ContextNode
    ):
        """Should set error if all providers fail and no chunks returned."""
        with patch.object(node, "_load_markdown_docs", side_effect=Exception("No such file")):
            with patch("app.agents.nodes.context_node.settings") as mock_settings:
                mock_settings.context_providers = ["markdown"]
                updates = await node.run({})
                assert "error" in updates

    @pytest.mark.asyncio
    async def test_run_loads_multiple_providers(
        self, node: ContextNode
    ):
        """Should load from multiple providers when configured."""
        with patch.object(node, "_load_markdown_docs", return_value=["doc1"]):
            with patch.object(node, "_load_faiss_context", return_value=["faiss1"]):
                with patch("app.agents.nodes.context_node.settings") as mock_settings:
                    mock_settings.context_providers = ["markdown", "faiss"]
                    mock_settings.db_context_enabled = False
                    mock_settings.http_context_url = ""
                    updates = await node.run({})
                    assert updates["context_chunks"] == ["doc1", "faiss1"]

    @pytest.mark.asyncio
    async def test_create_context_node_factory(self, mock_llm):
        node = create_context_node(mock_llm)
        assert isinstance(node, ContextNode)
        assert node.llm is mock_llm

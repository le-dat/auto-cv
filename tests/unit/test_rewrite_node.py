"""Unit tests for rewrite node."""

from unittest.mock import MagicMock
import pytest

from app.agents.nodes.rewrite_node import RewriteNode, create_rewrite_node
from app.models.schemas import CVData, JDData, MatchResult


class MockLLM:
    """Simple sync mock LLM that returns fixed content."""

    def __init__(self, content: str):
        self._content = content

    async def ainvoke(self, messages):
        return MagicMock(content=self._content)


class TestRewriteNode:
    """Tests for RewriteNode."""

    @pytest.fixture
    def node(self) -> RewriteNode:
        return RewriteNode(
            llm=MockLLM(
                "# Alice Smith\n\n## Summary\nSenior Engineer with strong FastAPI skills...\n\n## Skills\nPython, FastAPI, PostgreSQL, AWS, Docker"
            )
        )

    @pytest.mark.asyncio
    async def test_run_returns_rewritten_cv(
        self,
        node: RewriteNode,
        sample_cv_data: CVData,
        sample_jd_data: JDData,
        sample_match_result: MatchResult,
    ):
        state = {
            "cv_data": sample_cv_data,
            "jd_data": sample_jd_data,
            "match_result": sample_match_result,
            "context_chunks": [],
        }
        updates = await node.run(state)
        assert "rewritten_cv" in updates
        assert "match_report" in updates
        assert updates["rewritten_cv"].startswith("# Alice Smith")

    @pytest.mark.asyncio
    async def test_run_sets_error_when_missing_data(self):
        node = RewriteNode(llm=MockLLM("irrelevant"))
        state = {"cv_data": None, "jd_data": None}
        updates = await node.run(state)
        assert "error" in updates
        assert "Cannot rewrite" in updates["error"]

    @pytest.mark.asyncio
    async def test_run_uses_context_chunks(self):
        """Rewrite should incorporate context chunks when available."""
        rewritten_content = "# Rewritten with context"
        node = RewriteNode(llm=MockLLM(rewritten_content))
        cv = CVData(
            name="Alice",
            skills=["Python"],
            experience=[],
            education=[],
        )
        jd = JDData(
            title="Engineer",
            required_skills=["Python"],
            preferred_skills=[],
            description="Build things",
        )
        state = {
            "cv_data": cv,
            "jd_data": jd,
            "match_result": None,
            "context_chunks": ["knowledge:skills.md\n# Skills"],
        }
        updates = await node.run(state)
        assert "rewritten_cv" in updates
        assert updates["rewritten_cv"] == rewritten_content

    @pytest.mark.asyncio
    async def test_build_cv_text_includes_all_sections(
        self, node: RewriteNode, sample_cv_data: CVData
    ):
        """_build_cv_text should produce markdown with all sections."""
        text = node._build_cv_text(sample_cv_data)
        assert "# Alice Smith" in text
        assert "## Skills" in text
        assert "Python" in text
        assert "## Experience" in text
        assert "## Education" in text

    def test_create_rewrite_node_factory(self):
        node = create_rewrite_node(MockLLM("irrelevant"))
        assert isinstance(node, RewriteNode)

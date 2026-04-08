"""Unit tests for match node."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.agents.nodes.match_node import MatchNode, create_match_node
from app.models.schemas import CVData, JDData


class MockLLM:
    """Simple sync mock LLM that returns fixed JSON content."""

    def __init__(self, content: str):
        self._content = content

    async def ainvoke(self, messages):
        return MagicMock(content=self._content)


class TestMatchNode:
    """Tests for MatchNode."""

    @pytest.fixture
    def node(self) -> MatchNode:
        return MatchNode(
            llm=MockLLM(
                '{"matched_skills":["Python","FastAPI"],"missing_skills":["AWS","Docker"],"weak_skills":["PostgreSQL"],"skill_match_score":0.67,"suggestions":["Add AWS experience"]}'
            )
        )

    @pytest.mark.asyncio
    async def test_run_returns_match_result(
        self,
        node: MatchNode,
        sample_cv_data: CVData,
        sample_jd_data: JDData,
    ):
        state = {"cv_data": sample_cv_data, "jd_data": sample_jd_data}
        updates = await node.run(state)
        assert "match_result" in updates
        result = updates["match_result"]
        assert result.skill_match_score == 0.67
        assert "Python" in result.matched_skills

    @pytest.mark.asyncio
    async def test_run_sets_error_when_missing_cv_or_jd(self):
        node = MatchNode(
            llm=MockLLM('{"matched_skills":[],"missing_skills":[],"weak_skills":[],"skill_match_score":0.0,"suggestions":[]}')
        )
        state = {"cv_data": None, "jd_data": None}
        updates = await node.run(state)
        assert "error" in updates
        assert "Cannot match" in updates["error"]

    @pytest.mark.asyncio
    async def test_run_sets_error_on_llm_failure(self):
        class FailingLLM:
            async def ainvoke(self, messages):
                raise Exception("LLM error")

        node = MatchNode(llm=FailingLLM())
        sample_cv = CVData(skills=["Python"], experience=[], education=[])
        sample_jd = JDData(required_skills=["Python"], preferred_skills=[])
        updates = await node.run({"cv_data": sample_cv, "jd_data": sample_jd})
        assert "error" in updates
        assert "Match failed" in updates["error"]

    def test_create_match_node_factory(self):
        node = create_match_node(MockLLM("{}"))
        assert isinstance(node, MatchNode)

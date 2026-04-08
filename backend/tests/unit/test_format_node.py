"""Unit tests for format node."""

import pytest

from app.agents.nodes.format_node import FormatNode, create_format_node
from app.models.schemas import GenerateResult, MatchResult


class TestFormatNode:
    """Tests for FormatNode."""

    @pytest.fixture
    def node(self) -> FormatNode:
        return FormatNode()

    @pytest.mark.asyncio
    async def test_run_creates_generate_result(self, node: FormatNode):
        state = {
            "rewritten_cv": "# Alice Smith\n\n## Skills\nPython",
            "match_report": "# Match Analysis\n\nMatch: 80%",
            "match_result": MatchResult(
                matched_skills=["Python"],
                missing_skills=["AWS"],
                weak_skills=[],
                skill_match_score=0.8,
                suggestions=[],
            ),
        }
        updates = await node.run(state)
        assert "result" in updates
        result = updates["result"]
        assert isinstance(result, GenerateResult)
        assert "# Alice Smith" in result.rewritten_cv

    @pytest.mark.asyncio
    async def test_run_sets_error_when_missing_rewritten_cv(
        self, node: FormatNode
    ):
        state = {"rewritten_cv": None}
        updates = await node.run(state)
        assert "error" in updates
        assert "Missing rewritten_cv" in updates["error"]

    @pytest.mark.asyncio
    async def test_run_generates_match_report_when_missing(
        self, node: FormatNode
    ):
        state = {
            "rewritten_cv": "# Alice Smith",
            "match_report": None,
            "match_result": MatchResult(
                matched_skills=["Python"],
                missing_skills=["AWS"],
                weak_skills=[],
                skill_match_score=0.7,
                suggestions=["Add AWS"],
            ),
        }
        updates = await node.run(state)
        assert "result" in updates
        result = updates["result"]
        assert "Match Analysis" in result.match_report or "Python" in result.match_report

    @pytest.mark.asyncio
    async def test_create_format_node_factory(self):
        node = create_format_node()
        assert isinstance(node, FormatNode)

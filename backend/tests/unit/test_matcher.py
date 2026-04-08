"""Unit tests for matcher service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.schemas import MatchResult
from app.services.matcher import MatcherService


class TestMatcherService:
    """Tests for MatcherService."""

    @pytest.fixture
    def service(self, mock_llm) -> MatcherService:
        return MatcherService(llm=mock_llm)

    @pytest.mark.asyncio
    async def test_match_returns_match_result(
        self, service: MatcherService, mock_llm_match
    ):
        """Service should return a valid MatchResult from LLM response."""
        result = await service.match(
            cv_skills=["Python", "FastAPI", "PostgreSQL"],
            required_skills=["Python", "FastAPI", "AWS"],
            preferred_skills=["Docker"],
        )
        assert isinstance(result, MatchResult)
        assert result.skill_match_score == 0.67
        assert "Python" in result.matched_skills
        assert "AWS" in result.missing_skills

    @pytest.mark.asyncio
    async def test_match_calls_llm_with_correct_prompt(
        self, service: MatcherService, mock_llm
    ):
        """LLM should be called with formatted prompt."""
        mock_llm.ainvoke.return_value = MagicMock(
            content='{"matched_skills":[],"missing_skills":[],"weak_skills":[],"skill_match_score":0.0,"suggestions":[]}'
        )
        await service.match(
            cv_skills=["Python"],
            required_skills=["Rust"],
            preferred_skills=["Go"],
        )
        mock_llm.ainvoke.assert_called_once()
        call_args = mock_llm.ainvoke.call_args
        messages = call_args[0][0]
        prompt_content = messages[1].content
        assert "Python" in prompt_content
        assert "Rust" in prompt_content
        assert "Go" in prompt_content

    @pytest.mark.asyncio
    async def test_match_handles_empty_skills(
        self, service: MatcherService, mock_llm
    ):
        """Should handle empty skill lists gracefully."""
        mock_llm.ainvoke.return_value = MagicMock(
            content='{"matched_skills":[],"missing_skills":[],"weak_skills":[],"skill_match_score":0.0,"suggestions":[]}'
        )
        result = await service.match(cv_skills=[], required_skills=[], preferred_skills=[])
        assert isinstance(result, MatchResult)
        assert result.skill_match_score == 0.0

    @pytest.mark.asyncio
    async def test_match_strips_markdown_code_blocks(
        self, service: MatcherService, mock_llm
    ):
        """Should handle LLM response with markdown code fences."""
        mock_llm.ainvoke.return_value = MagicMock(
            content='```json\n{"matched_skills":["Python"],"missing_skills":[],"weak_skills":[],"skill_match_score":0.5,"suggestions":[]}\n```'
        )
        result = await service.match(
            cv_skills=["Python"], required_skills=["Python"], preferred_skills=[]
        )
        assert result.matched_skills == ["Python"]

    @pytest.mark.asyncio
    async def test_match_score_bounds(
        self, service: MatcherService, mock_llm
    ):
        """Skill match score should be between 0 and 1."""
        mock_llm.ainvoke.return_value = MagicMock(
            content='{"matched_skills":[],"missing_skills":[],"weak_skills":[],"skill_match_score":0.5,"suggestions":[]}'
        )
        result = await service.match(cv_skills=[], required_skills=[], preferred_skills=[])
        assert 0.0 <= result.skill_match_score <= 1.0



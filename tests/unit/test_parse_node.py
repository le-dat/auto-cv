"""Unit tests for parse node."""

from unittest.mock import MagicMock
import pytest

from app.agents.nodes.parse_node import ParseNode, create_parse_node
from app.models.schemas import CVData, JDData


class MockLLM:
    """Simple sync mock LLM that returns fixed JSON content."""

    def __init__(self, content: str):
        self._content = content

    async def ainvoke(self, messages):
        return MagicMock(content=self._content)


class TestParseNode:
    """Tests for ParseNode."""

    @pytest.fixture
    def node(self) -> ParseNode:
        return ParseNode(
            llm=MockLLM(
                '{"name":"Alice Smith","email":"alice@example.com","phone":"555-1234","location":"NYC","summary":"Senior Engineer","skills":["Python","FastAPI","PostgreSQL"],"experience":[{"company":"TechCorp","title":"Senior Engineer","start_date":"2020-01","end_date":"Present","description":"Built APIs"}],"education":[{"institution":"MIT","degree":"BS","field_of_study":"CS","graduation_date":"2019"}]}'
            )
        )

    @pytest.mark.asyncio
    async def test_run_parses_cv_text(self, node: ParseNode):
        state = {"cv_text": "Alice Smith\nalice@example.com\nSenior Engineer"}
        updates = await node.run(state)
        assert "cv_data" in updates
        assert updates["cv_data"].name == "Alice Smith"
        assert updates["cv_data"].email == "alice@example.com"

    @pytest.mark.asyncio
    async def test_run_returns_error_on_missing_text(self):
        node = ParseNode(llm=MockLLM('{}'))
        state = {"cv_text": None, "jd_text": None}
        updates = await node.run(state)
        assert updates == {}

    @pytest.mark.asyncio
    async def test_run_sets_error_on_parse_failure(self):
        class FailingLLM:
            async def ainvoke(self, messages):
                raise Exception("LLM error")

        node = ParseNode(llm=FailingLLM())
        state = {"cv_text": "Some text"}
        updates = await node.run(state)
        assert "error" in updates
        assert "CV parsing failed" in updates["error"]

    @pytest.mark.asyncio
    async def test_parse_cv_extracts_skills(self):
        node = ParseNode(
            llm=MockLLM(
                '{"name":"Alice","email":null,"phone":null,"location":null,"summary":null,"skills":["Python","FastAPI"],"experience":[],"education":[]}'
            )
        )
        updates = await node.run({"cv_text": "Skills: Python, FastAPI"})
        assert updates["cv_data"].skills == ["Python", "FastAPI"]

    def test_create_parse_node_factory(self):
        node = create_parse_node(MockLLM("{}"))
        assert isinstance(node, ParseNode)

"""Unit tests for validate node."""

import pytest

from app.agents.nodes.validate_node import ValidateNode, create_validate_node
from app.models.schemas import CVData, JDData


class TestValidateNode:
    """Tests for ValidateNode."""

    @pytest.fixture
    def node(self) -> ValidateNode:
        return ValidateNode()

    @pytest.mark.asyncio
    async def test_run_passes_valid_cv_data_through(
        self, node: ValidateNode, sample_cv_data: CVData
    ):
        state = {"cv_data": sample_cv_data, "jd_data": None}
        updates = await node.run(state)
        assert updates == {}

    @pytest.mark.asyncio
    async def test_run_validates_dict_as_cvdata(
        self, node: ValidateNode
    ):
        """Dict CV data should be validated into CVData."""
        cv_dict = {
            "name": "Bob Jones",
            "email": "bob@example.com",
            "skills": ["Go", "Kubernetes"],
            "experience": [],
            "education": [],
        }
        state = {"cv_data": cv_dict, "jd_data": None}
        updates = await node.run(state)
        assert "cv_data" in updates
        assert updates["cv_data"].name == "Bob Jones"
        assert updates["cv_data"].skills == ["Go", "Kubernetes"]

    @pytest.mark.asyncio
    async def test_run_returns_empty_on_no_data(self, node: ValidateNode):
        state = {"cv_data": None, "jd_data": None}
        updates = await node.run(state)
        assert updates == {}

    @pytest.mark.asyncio
    async def test_create_validate_node_factory(self):
        node = create_validate_node()
        assert isinstance(node, ValidateNode)

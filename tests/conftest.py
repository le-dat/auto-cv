"""Pytest fixtures for CV Optimizer tests."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure app is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.models.schemas import (
    CVData,
    Education,
    Experience,
    JDData,
    JobRecord,
    JobStatus,
    MatchResult,
)
from app.repositories.job_repository import InMemoryJobRepository


# ── Repository fixtures ─────────────────────────────────────────


@pytest.fixture
def repo() -> InMemoryJobRepository:
    """Return a fresh InMemoryJobRepository for each test."""
    return InMemoryJobRepository()


@pytest.fixture
def repo_singleton() -> InMemoryJobRepository:
    """Return the singleton InMemoryJobRepository instance."""
    return InMemoryJobRepository.get_instance()


# ── LLM fixtures ────────────────────────────────────────────────


@pytest.fixture
def mock_llm():
    """Return a mock LLM with an async ainvoke method.

    Use a plain MagicMock as the base so `await mock_llm.ainvoke(...)`
    returns the configured return_value, not another AsyncMock.
    """
    m = MagicMock()
    m.ainvoke = AsyncMock()
    return m


@pytest.fixture
def mock_llm_cv_parse(mock_llm):
    """Mock LLM that returns a valid CVData JSON response."""
    mock_llm.ainvoke.return_value = MagicMock(
        content='{"name":"Alice Smith","email":"alice@example.com","phone":"555-1234","location":"NYC","summary":"Senior Engineer","skills":["Python","FastAPI","PostgreSQL"],"experience":[{"company":"TechCorp","title":"Senior Engineer","start_date":"2020-01","end_date":"Present","description":"Built APIs"}],"education":[{"institution":"MIT","degree":"BS","field_of_study":"CS","graduation_date":"2019"}]}'
    )
    return mock_llm


@pytest.fixture
def mock_llm_jd_parse(mock_llm):
    """Mock LLM that returns a valid JDData JSON response."""
    mock_llm.ainvoke.return_value = MagicMock(
        content='{"title":"Backend Engineer","company":"HireCorp","location":"Remote","description":"Build scalable APIs","required_skills":["Python","FastAPI","PostgreSQL"],"preferred_skills":["AWS","Docker"]}'
    )
    return mock_llm


@pytest.fixture
def mock_llm_match(mock_llm):
    """Mock LLM that returns a valid MatchResult JSON response."""
    mock_llm.ainvoke.return_value = MagicMock(
        content='{"matched_skills":["Python","FastAPI"],"missing_skills":["AWS","Docker"],"weak_skills":["PostgreSQL"],"skill_match_score":0.67,"suggestions":["Add AWS experience","Highlight Docker projects"]}'
    )
    return mock_llm


@pytest.fixture
def mock_llm_rewrite(mock_llm):
    """Mock LLM that returns a rewritten CV."""
    mock_llm.ainvoke.return_value = MagicMock(
        content="# Alice Smith\n\n## Summary\nSenior Engineer with strong FastAPI skills...\n\n## Skills\nPython, FastAPI, PostgreSQL, AWS, Docker"
    )
    return mock_llm


# ── Sample data fixtures ────────────────────────────────────────


@pytest.fixture
def sample_cv_data() -> CVData:
    """Return a sample CVData object."""
    return CVData(
        name="Alice Smith",
        email="alice@example.com",
        phone="555-1234",
        location="NYC",
        summary="Senior Software Engineer with 5 years of experience",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        experience=[
            Experience(
                company="TechCorp",
                title="Senior Software Engineer",
                start_date="2020-01",
                end_date="Present",
                description="Built and maintained scalable APIs using FastAPI and PostgreSQL.",
            ),
            Experience(
                company="StartupXYZ",
                title="Software Engineer",
                start_date="2018-06",
                end_date="2019-12",
                description="Developed backend services in Python.",
            ),
        ],
        education=[
            Education(
                institution="MIT",
                degree="BS",
                field_of_study="Computer Science",
                graduation_date="2018",
            ),
        ],
    )


@pytest.fixture
def sample_jd_data() -> JDData:
    """Return a sample JDData object."""
    return JDData(
        title="Backend Engineer",
        company="HireCorp",
        location="Remote",
        description="We are looking for a Backend Engineer to build scalable APIs.",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        preferred_skills=["AWS", "Terraform", "Redis"],
    )


@pytest.fixture
def sample_match_result() -> MatchResult:
    """Return a sample MatchResult object."""
    return MatchResult(
        matched_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        missing_skills=["AWS", "Terraform", "Redis"],
        weak_skills=[],
        skill_match_score=0.57,
        suggestions=[
            "Add AWS experience to match preferred skills",
            "Highlight any infrastructure or DevOps work",
        ],
    )


@pytest.fixture
def sample_job_record(repo: InMemoryJobRepository) -> JobRecord:
    """Create and return a pending job record."""
    return repo.create("job-123")  # sync for test


# ── State fixtures ──────────────────────────────────────────────


@pytest.fixture
def workflow_state(sample_cv_data: CVData, sample_jd_data: JDData) -> dict:
    """Return a workflow state dict with CV and JD data."""
    return {
        "cv_text": "Alice Smith\nalice@example.com\nSenior Engineer...",
        "jd_text": "Backend Engineer\nHireCorp\nWe are looking for...",
        "cv_file_name": "alice_cv.pdf",
        "jd_file_name": "jd_backend.txt",
        "cv_data": sample_cv_data,
        "jd_data": sample_jd_data,
    }


@pytest.fixture
def workflow_state_empty() -> dict:
    """Return an empty workflow state."""
    return {
        "cv_text": None,
        "jd_text": None,
        "cv_data": None,
        "jd_data": None,
        "context_chunks": None,
        "match_result": None,
        "rewritten_cv": None,
        "match_report": None,
        "result": None,
        "error": None,
    }

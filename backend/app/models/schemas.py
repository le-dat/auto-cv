"""Pydantic v2 schemas for CV Optimizer."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class JobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ── CV/JD structured data ──────────────────────────────────────


class Experience(BaseModel):
    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class Education(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    graduation_date: str | None = None


class CVData(BaseModel):
    """Structured data extracted from a CV/resume."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    raw_text: str | None = None


class JDData(BaseModel):
    """Structured data extracted from a job description."""

    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    raw_text: str | None = None


# ── Match & Rewrite results ─────────────────────────────────────


class SkillGap(BaseModel):
    skill: str
    gap_type: Annotated[str, Field(description="'missing' | 'weak'")]


class MatchResult(BaseModel):
    """Skill matching analysis between CV and JD."""

    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    weak_skills: list[str] = Field(default_factory=list)
    skill_match_score: float = Field(
        ge=0.0, le=1.0, description="Normalized match score"
    )
    suggestions: list[str] = Field(default_factory=list)


class GenerateResult(BaseModel):
    """Final rewritten CV with match report."""

    rewritten_cv: str = Field(description="Rewritten CV text")
    match_report: str = Field(description="Summary of match analysis")
    match_result: MatchResult | None = None


# ── Job record ──────────────────────────────────────────────────


class JobRecord(BaseModel):
    """Persistent job record stored in the repository."""

    job_id: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cv_data: CVData | None = None
    jd_data: JDData | None = None
    result: GenerateResult | None = None
    error: str | None = None


# ── API request/response schemas ───────────────────────────────


class JobCreateResponse(BaseModel):
    """Response returned immediately after job creation."""

    job_id: str
    status: JobStatus
    message: str = "Job queued for processing"


class JobStatusResponse(BaseModel):
    """Response for job status polling."""

    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result: GenerateResult | None = None
    error: str | None = None


class InputPayload(BaseModel):
    """Combined CV + JD input for the workflow."""

    cv_text: str | None = None
    cv_file_name: str | None = None
    jd_text: str | None = None
    jd_file_name: str | None = None

    @model_validator(mode="after")
    def check_cv_and_jd(self) -> "InputPayload":
        has_cv = bool(self.cv_text or self.cv_file_name)
        has_jd = bool(self.jd_text or self.jd_file_name)
        if not has_cv:
            raise ValueError("At least one of cv_text or cv_file_name must be provided")
        if not has_jd:
            raise ValueError("At least one of jd_text or jd_file_name must be provided")
        return self

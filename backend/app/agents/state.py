"""LangGraph WorkflowState TypedDict."""

from typing import Annotated

from langgraph.graph import add_messages

from app.models.schemas import CVData, GenerateResult, JDData, MatchResult


class WorkflowState(dict):
    """State passed between LangGraph nodes.

    Attributes:
        cv_text: Raw CV input text.
        jd_text: Raw job description input text.
        cv_data: Structured CV data after parsing.
        jd_data: Structured JD data after parsing.
        validation_errors: Any validation errors encountered.
        context_chunks: Retrieved context from knowledge sources.
        match_result: Skill matching analysis result.
        rewritten_cv: The final rewritten CV text.
        match_report: Summary of match analysis.
        result: Final GenerateResult object.
        error: Error message if any node failed.
        messages: Message history for the graph (used by add_messages reducer).
    """

    cv_text: str | None = None
    jd_text: str | None = None
    cv_file_name: str | None = None
    jd_file_name: str | None = None

    cv_data: CVData | None = None
    jd_data: JDData | None = None
    validation_errors: list[str] | None = None

    context_chunks: list[str] | None = None

    match_result: MatchResult | None = None

    rewritten_cv: str | None = None
    match_report: str | None = None
    result: GenerateResult | None = None

    error: str | None = None

    # Used by LangGraph for message handling
    messages: Annotated[list, add_messages] = []

"""Matcher service — scores skill match between CV and JD."""

import json

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.models.schemas import MatchResult

MATCH_PROMPT = """You are an ATS skill matcher. Analyze the CV skills against the job requirements.

Given:
- CV Skills: {cv_skills}
- Required Skills: {required_skills}
- Preferred Skills: {preferred_skills}

Return ONLY a valid JSON object with this structure:
{{
    "matched_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", ...],
    "weak_skills": ["skill1", ...],
    "skill_match_score": 0.85,
    "suggestions": ["suggestion1", ...]
}}
"""


class MatcherService:
    """Service for matching CV skills against JD requirements."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def match(
        self,
        cv_skills: list[str],
        required_skills: list[str],
        preferred_skills: list[str] | None = None,
    ) -> MatchResult:
        """Perform skill matching analysis.

        Args:
            cv_skills: List of skills from CV.
            required_skills: List of required skills from JD.
            preferred_skills: List of preferred skills from JD.

        Returns:
            MatchResult with matched/missing skills and score.
        """
        prompt = MATCH_PROMPT.format(
            cv_skills=", ".join(cv_skills) or "None listed",
            required_skills=", ".join(required_skills) or "None listed",
            preferred_skills=", ".join(preferred_skills or []) or "None listed",
        )

        messages = [
            SystemMessage(content="You are an ATS skill matching assistant."),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0].strip()

        parsed = json.loads(content)
        return MatchResult.model_validate(parsed)

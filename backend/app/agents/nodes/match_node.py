"""Match node — scores skill match between CV and JD."""

import json
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.models.schemas import MatchResult

MATCH_PROMPT = """You are an ATS skill matcher. Analyze the CV skills against the job requirements.

Given:
- CV Skills: {cv_skills}
- Required Skills: {required_skills}
- Preferred Skills: {preferred_skills}

Return ONLY a valid JSON object with this structure:
{
    "matched_skills": ["skill1", "skill2", ...],  # Skills present in both CV and JD
    "missing_skills": ["skill1", ...],            # Required skills NOT in CV
    "weak_skills": ["skill1", ...],               # Skills mentioned but not well demonstrated
    "skill_match_score": 0.85,                     # 0.0 to 1.0 normalized score
    "suggestions": ["suggestion1", ...]            # How to improve match
}
"""


class MatchNode:
    """Node responsible for matching CV skills against JD requirements."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def run(self, state: dict) -> dict[str, Any]:
        """Perform skill matching analysis."""
        updates: dict[str, Any] = {}
        cv_data = state.get("cv_data")
        jd_data = state.get("jd_data")

        if not cv_data or not jd_data:
            updates["error"] = "Cannot match: missing CV or JD data"
            return updates

        try:
            match_result = await self._match_skills(
                cv_skills=cv_data.skills or [],
                required_skills=jd_data.required_skills or [],
                preferred_skills=jd_data.preferred_skills or [],
            )
            updates["match_result"] = match_result
        except Exception as e:
            updates["error"] = f"Match failed: {str(e)}"

        return updates

    async def _match_skills(
        self,
        cv_skills: list[str],
        required_skills: list[str],
        preferred_skills: list[str],
    ) -> MatchResult:
        """Call LLM to perform skill matching."""
        prompt = MATCH_PROMPT.format(
            cv_skills=", ".join(cv_skills),
            required_skills=", ".join(required_skills),
            preferred_skills=", ".join(preferred_skills),
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


def create_match_node(llm: BaseChatModel):
    """Factory to create a match node with the given LLM."""
    return MatchNode(llm)

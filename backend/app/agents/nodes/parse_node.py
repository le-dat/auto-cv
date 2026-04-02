"""Parse node — extracts structured CV/JD data from raw input."""

import json
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.models.schemas import CVData, JDData

# System prompt for CV parsing
CV_PARSE_PROMPT = """You are a CV parser. Extract structured data from the provided CV text.

Return ONLY a valid JSON object with this structure:
{
    "name": "Full name or null",
    "email": "Email or null",
    "phone": "Phone or null",
    "location": "Location or null",
    "summary": "Professional summary or null",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {"company": "company name", "title": "job title", "start_date": "YYYY-MM", "end_date": "YYYY-MM or Present", "description": "job description"},
        ...
    ],
    "education": [
        {"institution": "school name", "degree": "degree type", "field_of_study": "field", "graduation_date": "YYYY or null"},
        ...
    ]
}

If a field is not present in the CV, use null. Return empty arrays [] for missing lists.
"""

# System prompt for JD parsing
JD_PARSE_PROMPT = """You are a Job Description parser. Extract structured data from the provided job description.

Return ONLY a valid JSON object with this structure:
{
    "title": "Job title",
    "company": "Company name or null",
    "location": "Location or null",
    "description": "Full job description or null",
    "required_skills": ["skill1", "skill2", ...],
    "preferred_skills": ["skill1", "skill2", ...]
}

If a field is not present, use null. Return empty arrays [] for missing lists.
"""


class ParseNode:
    """Node responsible for parsing raw CV and JD text into structured data."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def run(self, state: dict) -> dict[str, Any]:
        """Parse CV and JD text into structured data."""
        updates: dict[str, Any] = {}

        # Parse CV if provided
        if state.get("cv_text"):
            try:
                cv_data = await self._parse_cv(state["cv_text"])
                updates["cv_data"] = cv_data
            except Exception as e:
                updates["error"] = f"CV parsing failed: {str(e)}"
                return updates

        # Parse JD if provided
        if state.get("jd_text"):
            try:
                jd_data = await self._parse_jd(state["jd_text"])
                updates["jd_data"] = jd_data
            except Exception as e:
                updates["error"] = f"JD parsing failed: {str(e)}"
                return updates

        return updates

    async def _parse_cv(self, cv_text: str) -> CVData:
        """Parse CV text into CVData object."""
        messages = [
            SystemMessage(content=CV_PARSE_PROMPT),
            HumanMessage(content=f"CV Text:\n{cv_text}"),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0].strip()

        parsed = json.loads(content)
        return CVData.model_validate(parsed)

    async def _parse_jd(self, jd_text: str) -> JDData:
        """Parse JD text into JDData object."""
        messages = [
            SystemMessage(content=JD_PARSE_PROMPT),
            HumanMessage(content=f"Job Description:\n{jd_text}"),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0].strip()

        parsed = json.loads(content)
        return JDData.model_validate(parsed)


def create_parse_node(llm: BaseChatModel):
    """Factory to create a parse node with the given LLM."""
    return ParseNode(llm)

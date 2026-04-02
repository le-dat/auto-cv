"""Rewriter service — rewrites CV optimized for job description."""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.models.schemas import CVData, JDData, MatchResult

REWRITE_PROMPT = """You are a professional CV writer. Rewrite the provided CV to be optimized for the job description.

IMPORTANT RULES:
- NEVER fabricate experience, skills, or achievements not in the original CV
- Only highlight and emphasize existing skills and experience that match the JD
- Reorder bullet points to prioritize most relevant achievements first
- Use ATS-friendly keywords from the job description naturally
- Maintain the CV in the same format (markdown)
- Keep all information truthful and accurate

CV:
{cv_text}

Job Description:
{jd_text}

Match Analysis:
{match_analysis}

Context (optional knowledge):
{context}

Return ONLY the rewritten CV text in markdown format.
"""


class RewriterService:
    """Service for rewriting CVs to match job descriptions."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def rewrite(
        self,
        cv_data: CVData,
        jd_data: JDData,
        match_result: MatchResult | None = None,
        context: list[str] | None = None,
    ) -> str:
        """Rewrite CV optimized for the job description.

        Args:
            cv_data: Structured CV data.
            jd_data: Structured JD data.
            match_result: Optional match analysis result.
            context: Optional list of context strings.

        Returns:
            Rewritten CV text in markdown format.
        """
        cv_text = self._build_cv_text(cv_data)
        jd_text = jd_data.description or str(jd_data)
        match_analysis = self._format_match(match_result)
        context_text = "\n\n".join(context[:3]) if context else "No additional context."

        prompt = REWRITE_PROMPT.format(
            cv_text=cv_text,
            jd_text=jd_text,
            match_analysis=match_analysis,
            context=context_text,
        )

        messages = [
            SystemMessage(content="You are a professional CV writer."),
            HumanMessage(content=prompt),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        return content.strip()

    def _build_cv_text(self, cv_data: CVData) -> str:
        """Build plain text CV from structured data."""
        lines = []

        if cv_data.name:
            lines.append(f"# {cv_data.name}")
        if cv_data.email:
            lines.append(f"Email: {cv_data.email}")
        if cv_data.phone:
            lines.append(f"Phone: {cv_data.phone}")
        if cv_data.location:
            lines.append(f"Location: {cv_data.location}")
        if cv_data.summary:
            lines.append(f"\n## Summary\n{cv_data.summary}")

        if cv_data.skills:
            lines.append(f"\n## Skills\n{', '.join(cv_data.skills)}")

        if cv_data.experience:
            lines.append("\n## Experience")
            for exp in cv_data.experience:
                lines.append(f"\n### {exp.title} at {exp.company}")
                if exp.start_date:
                    end = exp.end_date or "Present"
                    lines.append(f"{exp.start_date} - {end}")
                if exp.description:
                    lines.append(exp.description)

        if cv_data.education:
            lines.append("\n## Education")
            for edu in cv_data.education:
                lines.append(f"\n### {edu.degree} in {edu.field_of_study}")
                lines.append(f"{edu.institution}")
                if edu.graduation_date:
                    lines.append(f"Graduated: {edu.graduation_date}")

        return "\n".join(lines)

    def _format_match(self, match_result: MatchResult | None) -> str:
        """Format match result for prompt."""
        if not match_result:
            return "No match analysis available."

        lines = [
            f"Match Score: {match_result.skill_match_score:.0%}",
            f"Matched Skills: {', '.join(match_result.matched_skills) or 'None'}",
            f"Missing Skills: {', '.join(match_result.missing_skills) or 'None'}",
            f"Weak Skills: {', '.join(match_result.weak_skills) or 'None'}",
        ]
        if match_result.suggestions:
            lines.append("Suggestions:")
            lines.extend(f"- {s}" for s in match_result.suggestions)
        return "\n".join(lines)
